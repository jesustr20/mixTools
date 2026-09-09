#!/usr/bin/env bash
# scripts/create-github-issues.sh
#
# Crea todos los issues definidos en docs/issues/*.md en el repo de GitHub.
# Uso:
#   ./scripts/create-github-issues.sh owner/nombre-repo
#   ./scripts/create-github-issues.sh owner/nombre-repo --dry-run
set -euo pipefail

REPO="${1:-}"
shift || true

if [[ -z "$REPO" ]]; then
  echo "Uso: $0 owner/nombre-repo [--dry-run]"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "== Sincronizando labels en $REPO =="
"$SCRIPT_DIR/sync-labels.sh" "$REPO"

echo ""
echo "== Creando issues en $REPO =="
python3 "$SCRIPT_DIR/create_github_issues.py" --repo "$REPO" "$@"
