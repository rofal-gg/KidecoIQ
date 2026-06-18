#!/usr/bin/env bash
# KidecoIQ — Backend Docker Entrypoint
# Waits for PostgreSQL, runs migrations, then starts uvicorn.

set -euo pipefail

echo "================================================"
echo "  KidecoIQ API — Docker Entrypoint"
echo "================================================"

# ── 1. Wait for PostgreSQL ─────────────────────────
echo ""
echo "[1/3] Waiting for PostgreSQL ..."
python /app/scripts/wait_for_db.py "${DATABASE_URL}"

# ── 2. Run database migrations ─────────────────────
echo ""
echo "[2/3] Running database migrations ..."
cd /app
alembic upgrade head
echo "  Migrations complete."

# ── 3. Start application ───────────────────────────
echo ""
echo "[3/3] Starting KidecoIQ API ..."
echo "================================================"
echo ""

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info
