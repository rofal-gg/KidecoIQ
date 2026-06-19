"""
KidecoIQ — Modul Operasional: In-Memory Data Store
====================================================
MVP data layer yang menggunakan fleet_data pipeline untuk
menyediakan data fleet + anomali + alert ke endpoint API.

Ketika PostgreSQL tersedia, layer ini akan diganti dengan SQLAlchemy queries.
"""

import os
from datetime import datetime, timezone
from typing import Optional

import pandas as pd

from app.modules.operasional import fleet_data

# ── In-memory storage ────────────────────────────────────────

_summary_df: pd.DataFrame = None   # per-unit summary with anomaly + risk
_raw_df: pd.DataFrame = None       # raw shift-level data
_unit_anomaly_cache: dict = {}     # unit_id → anomaly list

NOW = datetime.now(timezone.utc)


# ── Initialisation ───────────────────────────────────────────

def _init_data():
    """Bootstrap in-memory store by running the full pipeline."""
    global _summary_df, _raw_df, _unit_anomaly_cache

    csv_path = fleet_data.DEFAULT_CSV_PATH
    if not os.path.isfile(csv_path):
        fleet_data.generate_fleet_csv(csv_path)

    _raw_df = pd.read_csv(csv_path)
    # Summary: aggregate + anomaly detection on shift level + risk scores
    _summary_df = fleet_data.compute_summary_with_anomaly(
        _raw_df,
        contamination=0.02,      # hanya ~12 shift paling ekstrem (cukup untuk 6 injected)
        random_state=42,
        anomaly_shift_threshold_pct=3.0,
    )
    _summary_df = fleet_data.compute_risk_scores(_summary_df)

    # Pre-compute anomaly data per unit
    for unit_id in _summary_df["unit_id"].unique():
        anomalies = fleet_data.get_anomalies_for_unit(_raw_df, unit_id)
        _unit_anomaly_cache[unit_id] = anomalies


# ── Public API ───────────────────────────────────────────────

def get_fleet_summary() -> list[dict]:
    """
    Return list of all fleet units with summary stats.
    Each item matches FleetUnitResponse shape.
    """
    records = _summary_df.to_dict(orient="records")
    result = []
    for r in records:
        unit_id = r["unit_id"]
        model = _get_model_for_unit(unit_id)
        result.append({
            "unit_id": unit_id,
            "model": model,
            "status": r["status"],
            "idle_ratio_avg": r["idle_ratio_avg"],
            "fuel_avg": r["fuel_avg"],
            "total_hours": r["total_hours"],
            "risk_score": r["risk_score"],
            "alert_level": r["alert_level"],
        })
    return result


def get_unit_anomalies(unit_id: str) -> Optional[list[dict]]:
    """
    Return anomaly detection results for a specific unit.
    Returns None if unit not found.
    """
    if unit_id not in _summary_df["unit_id"].values:
        return None
    return _unit_anomaly_cache.get(unit_id, [])


def get_alerts() -> list[dict]:
    """Return list of active alerts (medium + high risk)."""
    return fleet_data.get_alerts_from_summary(_summary_df)


def _get_model_for_unit(unit_id: str) -> str:
    """Look up unit model from definitions."""
    for uid, model in fleet_data.UNIT_DEFINITIONS:
        if uid == unit_id:
            return model
    return "Unknown"


# ── Bootstrap on import ──────────────────────────────────────

_init_data()
