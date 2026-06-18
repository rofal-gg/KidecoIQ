"""
KidecoIQ API — Main Application
FastAPI entry point with health check, CORS, and module router mounting.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import engine, SessionLocal
from app.modules.reklamasi.router import router as reklamasi_router
from app.modules.operasional.router import router as operasional_router

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: test database connectivity and log status."""
    logger.info("Starting KidecoIQ API ...")
    try:
        with SessionLocal() as db:
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
        logger.info("Database connection OK")
    except Exception as e:
        logger.warning(f"Database not available at startup: {e}")
    yield
    # Shutdown
    engine.dispose()
    logger.info("KidecoIQ API shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow all origins for MVP development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health Check ──────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint.
    Returns 200 with DB status when the app is alive.
    """
    db_ok = False
    try:
        with SessionLocal() as db:
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            db_ok = True
    except Exception as e:
        db_ok = False

    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unavailable",
        "app": settings.APP_NAME,
        "version": "0.1.0",
    }


# ── Mount Module Routers ──────────────────────────────────────
app.include_router(reklamasi_router)
app.include_router(operasional_router)
