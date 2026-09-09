#!/usr/bin/env bash
# scripts/sync-labels.sh
set -euo pipefail
REPO="${1:-}"
if [[ -z "$REPO" ]]; then
  echo "Uso: $0 owner/nombre-repo [--dry-run]"
  exit 1
fi
shift || true
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/sync_labels.py" --repo "$REPO" "$@"
