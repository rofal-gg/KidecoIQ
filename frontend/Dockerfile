# KidecoIQ — Frontend Dockerfile
# Multi-stage build: install deps → build → standalone runner

# ── Stage 1: Dependencies ─────────────────────────
FROM node:22-alpine AS deps
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --only=production

# ── Stage 2: Builder ──────────────────────────────
FROM node:22-alpine AS builder

# API_URL: set at build time (e.g. http://backend:8000 in Docker)
ARG API_URL=http://localhost:8000
ENV API_URL=$API_URL

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ── Stage 3: Runner ───────────────────────────────
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Override API_URL at runtime too
ARG API_URL=http://localhost:8000
ENV API_URL=$API_URL

# Copy standalone build output
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

ENV HOSTNAME=0.0.0.0

CMD ["node", "server.js"]
