#!/usr/bin/env bash
# KidecoIQ — Migration helper
# Usage: ./migrate.sh [up|down|revision]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PYTHONPATH="${SCRIPT_DIR}"

ACTION="${1:-up}"

case "$ACTION" in
  up)
    echo ">>> Running migrations: upgrade head"
    alembic upgrade head
    ;;
  down)
    echo ">>> Rolling back: downgrade -1"
    alembic downgrade -1
    ;;
  revision)
    MSG="${2:-auto}"
    echo ">>> Creating new migration: $MSG"
    alembic revision --autogenerate -m "$MSG"
    ;;
  status)
    alembic current
    ;;
  *)
    echo "Usage: $0 [up|down|revision <msg>|status]"
    exit 1
    ;;
esac
echo ">>> Done."
