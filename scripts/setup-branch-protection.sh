#!/usr/bin/env bash
# scripts/setup-branch-protection.sh
#
# Activa la regla de protección en `main` para que el check de CI
# ("lint-and-test", definido en .github/workflows/ci.yml) sea obligatorio
# antes de poder mergear un PR.
#
# Uso:
#   ./scripts/setup-branch-protection.sh tu-usuario/nombre-repo
#
# Requisito: que ya haya corrido al menos un PR con el workflow de CI, para
# que GitHub reconozca el nombre del check "lint-and-test". Si el comando
# falla con "status check not found", abrí un PR de prueba primero, dejá
# que corra el CI, y recién ahí corré este script.
set -euo pipefail

REPO="${1:-}"
if [[ -z "$REPO" ]]; then
  echo "Uso: $0 tu-usuario/nombre-repo"
  exit 1
fi

echo "Activando branch protection en $REPO (rama main)…"

gh api \
  --method PUT \
  "repos/$REPO/branches/main/protection" \
  --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["lint-and-test-backend", "lint-and-test-frontend"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0
  },
  "restrictions": null
}
EOF

echo "Listo. Un PR contra main ahora necesita que 'lint-and-test' pase para poder mergear."
echo "Verificar: gh api repos/$REPO/branches/main/protection --jq .required_status_checks"
