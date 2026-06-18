# KidecoIQ — Backend Dockerfile
# Build context MUST be the repo root (contains SPEC.md + data/ directory).
# docker build -f backend/Dockerfile -t kideco-iq-backend .

FROM python:3.11-slim

# ── System dependencies ────────────────────────────
# rasterio, geoalchemy2, and psycopg2 need C libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgdal-dev \
    gdal-bin \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Install Python dependencies ────────────────────
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application code ──────────────────────────
# Context = repo root, so SPEC.md and data/ are accessible
COPY backend/ ./
COPY data/ ./data/
# SPEC.md is needed by synthetic_raster._get_project_root() at import time
COPY SPEC.md ./SPEC.md

# ── Copy entrypoint ────────────────────────────────
COPY backend/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/docker-entrypoint.sh"]
