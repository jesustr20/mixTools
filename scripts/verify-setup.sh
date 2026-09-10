#!/usr/bin/env bash
set -uo pipefail

REPO="${1:-}"
if [[ -z "$REPO" ]]; then
  echo "Uso: $0 tu-usuario/nombre-repo"
  exit 1
fi

PASS=0
FAIL=0

check() {
  local desc="$1"
  local result="$2"
  if [[ "$result" == "0" ]]; then
    echo "  ✓ $desc"
    PASS=$((PASS+1))
  else
    echo "  ✗ $desc"
    FAIL=$((FAIL+1))
  fi
}

echo "== 1. Repo local — estructura de archivos =="
for f in \
  ".gitignore" "AGENTS.md" "opencode.jsonc" "README.md" \
  "backend/pyproject.toml" "backend/uv.lock" "backend/app/main.py" \
  "docs/labels.yaml" "docs/adr/0001-arquitectura-backend-frontend.md" \
  "scripts/bootstrap-repo.sh" "scripts/create-github-issues.sh" \
  "scripts/sync-labels.sh" "scripts/setup-branch-protection.sh" \
  ".github/workflows/ci.yml" ".github/workflows/ci-frontend.yml" \
  ".github/workflows/issue-ops.yml"
do
  [[ -f "$f" ]]; check "$f existe" "$?"
done
[[ -f "backend/requirements.txt" ]]; check "requirements.txt YA NO existe (migrado a uv)" $((! $?))

echo ""
echo "== 2. Git — remote y estado =="
REMOTE_URL=$(git remote get-url origin 2>/dev/null)
[[ "$REMOTE_URL" == *"$REPO"* ]]; check "remote origin apunta a $REPO (es: $REMOTE_URL)" "$?"
[[ -z "$(git status --porcelain 2>/dev/null)" ]]; check "no hay cambios sin commitear" "$?"
[[ "$(git branch --show-current)" == "main" ]]; check "estás en la rama main" "$?"

echo ""
echo "== 3. Backend — calidad y arranque real =="
cd backend 2>/dev/null || { echo "  ✗ no se pudo entrar a backend/"; FAIL=$((FAIL+1)); }
uv lock --check &>/dev/null; check "uv.lock sincronizado con pyproject.toml" "$?"
uv run ruff check app/ &>/dev/null; check "ruff sin errores" "$?"
(uv run uvicorn app.main:app --port 8099 > /tmp/verify_uvicorn.log 2>&1 &)
sleep 4
HEALTH=$(curl -s http://localhost:8099/api/health 2>/dev/null)
[[ "$HEALTH" == *'"status":"ok"'* ]]; check "servidor arranca y /api/health responde" "$?"
pkill -f "uvicorn app.main:app --port 8099" 2>/dev/null
cd ..

echo ""
echo "== 4. GitHub — labels, issues, milestone =="
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  LABEL_COUNT=$(gh label list --repo "$REPO" --json name --jq 'length' 2>/dev/null)
  [[ "$LABEL_COUNT" == "17" ]]; check "17 labels en GitHub (hay: ${LABEL_COUNT:-0})" "$?"

  ISSUE_COUNT=$(gh issue list --repo "$REPO" --state all --json number --jq 'length' 2>/dev/null)
  [[ "$ISSUE_COUNT" -ge "12" ]] 2>/dev/null; check "al menos 12 issues en GitHub (hay: ${ISSUE_COUNT:-0})" "$?"

  MILESTONE=$(gh api "repos/$REPO/milestones" --jq '.[] | select(.title=="MixTools v1") | .title' 2>/dev/null)
  [[ "$MILESTONE" == "MixTools v1" ]]; check "milestone 'MixTools v1' existe" "$?"

  echo ""
  echo "== 5. GitHub — branch protection =="
  PROTECTED_CHECKS=$(gh api "repos/$REPO/branches/main/protection/required_status_checks" --jq '.contexts | length' 2>/dev/null)
  [[ "$PROTECTED_CHECKS" == "2" ]]; check "branch protection exige 2 checks (hay: ${PROTECTED_CHECKS:-0})" "$?"

  echo ""
  echo "== 6. GitHub — último run de CI real (no skipped) =="
  LAST_RUN=$(gh run list --repo "$REPO" --workflow=ci.yml --limit 1 --json conclusion,status --jq '.[0]')
  LAST_CONCLUSION=$(echo "$LAST_RUN" | grep -o '"conclusion":"[^"]*"' | cut -d'"' -f4)
  [[ "$LAST_CONCLUSION" == "success" ]]; check "último run de CI (backend) = success (es: ${LAST_CONCLUSION:-desconocido})" "$?"
else
  echo "  ⚠ gh no disponible o no autenticado — se salta la verificación de GitHub"
fi

echo ""
echo "== 7. Toolchain de agentes =="
command -v opencode &>/dev/null; check "opencode instalado" "$?"
opencode auth list 2>/dev/null | grep -qi deepseek; check "DeepSeek autenticado en opencode" "$?"
opencode mcp list 2>/dev/null | grep -qi codebase-memory; check "codebase-memory-mcp conectado" "$?"
grep -q "deepseek-v4-pro" opencode.jsonc 2>/dev/null; check "opencode.jsonc apunta a deepseek-v4-pro" "$?"

echo ""
echo "================================"
echo " $PASS OK, $FAIL con problemas"
echo "================================"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
