#!/usr/bin/env bash
# scripts/bootstrap-repo.sh
#
# Todo en uno: autentica gh CLI (si hace falta), inicializa git, hace el
# primer commit, y crea+pushea el repo en GitHub. Pensado para correr una
# sola vez, al arrancar el proyecto.
#
# Uso:
#   ./scripts/bootstrap-repo.sh mixtools
#   ./scripts/bootstrap-repo.sh mixtools --private
#
# El login de GitHub es inherentemente interactivo (abre el navegador o pide
# pegar un token) — no hay forma de scriptearlo 100% sin exponer un token en
# texto plano. Este script te lleva hasta ahí y te avisa qué elegir.
set -euo pipefail

REPO_NAME="${1:-}"
VISIBILITY="--public"
if [[ "${2:-}" == "--private" ]]; then
  VISIBILITY="--private"
fi

if [[ -z "$REPO_NAME" ]]; then
  echo "Uso: $0 nombre-del-repo [--private]"
  exit 1
fi

# --- 1. gh CLI instalado ---
if ! command -v gh &> /dev/null; then
  echo "ERROR: no tenés GitHub CLI instalado."
  echo "  macOS:   brew install gh"
  echo "  Ubuntu:  sudo apt install gh"
  echo "  Windows: winget install --id GitHub.cli"
  echo "Más opciones: https://github.com/cli/cli#installation"
  exit 1
fi

# --- 2. Autenticación ---
if gh auth status &> /dev/null; then
  echo "== gh ya está autenticado =="
  gh auth status
else
  echo "== gh no está autenticado. Elegí un método: =="
  echo "  1) Navegador (recomendado, abre GitHub y confirmás con un click)"
  echo "  2) Pegar un Personal Access Token (para SSH remoto/sin navegador)"
  read -rp "Opción [1/2]: " AUTH_CHOICE

  if [[ "$AUTH_CHOICE" == "2" ]]; then
    echo "Generá un token en: https://github.com/settings/tokens/new"
    echo "  Permisos necesarios: repo, workflow, read:org"
    read -rsp "Pegá el token (no se muestra en pantalla): " GH_TOKEN_INPUT
    echo ""
    echo "$GH_TOKEN_INPUT" | gh auth login --with-token
  else
    gh auth login --web --git-protocol https
  fi
fi

echo ""
gh auth status

# --- 3. git init + primer commit ---
if [[ ! -d ".git" ]]; then
  echo "== git init =="
  git init
  git branch -M main
fi

if [[ -z "$(git config user.email 2>/dev/null)" ]]; then
  echo "AVISO: no tenés git user.email/user.name configurados globalmente."
  read -rp "  Tu nombre para los commits: " GIT_NAME
  read -rp "  Tu email para los commits: " GIT_EMAIL
  git config user.name "$GIT_NAME"
  git config user.email "$GIT_EMAIL"
fi

git add .
if git diff --cached --quiet; then
  echo "== Nada nuevo para commitear =="
else
  git commit -m "chore: scaffolding inicial (backend, frontend preview, docs, scripts, agentes)"
fi

# --- 4. Crear repo en GitHub + push ---
if git remote get-url origin &> /dev/null; then
  echo "== Ya existe un remote 'origin', pusheando ahí =="
  git push -u origin main
else
  echo "== Creando repo '$REPO_NAME' en GitHub ($VISIBILITY) y pusheando =="
  gh repo create "$REPO_NAME" "$VISIBILITY" --source=. --remote=origin --push
fi

echo ""
echo "Listo. Repo disponible en:"
gh repo view --json url --jq .url
