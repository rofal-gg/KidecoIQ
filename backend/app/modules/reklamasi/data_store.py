"""
KidecoIQ — Modul Reklamasi: In-Memory Data Store
=================================================
MVP data layer yang membaca raster sintetis dari data/satellite_samples/
dan menyediakan data zona + history untuk endpoint API.

Ketika PostgreSQL tersedia, layer ini akan diganti dengan SQLAlchemy queries.
"""

import uuid
import os
from datetime import datetime, timezone, timedelta, date
from typing import Optional

import numpy as np

from app.modules.reklamasi.ndvi import process_bands
from app.modules.reklamasi.synthetic_raster import (
    _make_synthetic_arrays,
    load_band,
    DEFAULT_OUTPUT_DIR,
    _get_project_root,
)

# ── Constants ─────────────────────────────────────────────────

RASTER_RED_PATH = os.path.join(DEFAULT_OUTPUT_DIR, "band4_red.tif")
RASTER_NIR_PATH = os.path.join(DEFAULT_OUTPUT_DIR, "band8_nir.tif")

ZONE_NAMES = [
    "Roto Samurangau - Sektor A",
    "Roto Samurangau - Sektor B",
    "Roto Samurangau - Sektor C",
    "Roto Samurangau - Sektor D",
    "Roto Samurangau - Buffer Zone",
]

ZONE_DESCRIPTIONS = [
    "Area pilot reklamasi dengan vegetasi sehat",
    "Area reklamasi dengan vegetasi stres",
    "Area lahan kosong pascatambang",
    "Area badan air/settling pond",
    "Zona penyangga antara area aktif dan reklamasi",
]

# Historical dates for simulation (dd/mm/yyyy simulation)
HISTORY_DATES = [
    date(2026, 1, 15),
    date(2026, 3, 1),
    date(2026, 6, 18),  # current
]

NOW = datetime.now(timezone.utc)

# ── In-memory storage ────────────────────────────────────────

_zones: list[dict] = []
_zone_history: dict[str, list[dict]] = {}


# ── Initialisation ───────────────────────────────────────────

def _compute_quadrant_stats(
    ndvi: np.ndarray,
    codes: np.ndarray,
    veg_mask: np.ndarray,
    h_start: int,
    h_end: int,
    w_start: int,
    w_end: int,
) -> dict:
    """Compute NDVI stats for a rectangular region of the array."""
    region_ndvi = ndvi[h_start:h_end, w_start:w_end]
    region_codes = codes[h_start:h_end, w_start:w_end]
    region_veg = veg_mask[h_start:h_end, w_start:w_end]

    return {
        "ndvi_mean": float(np.mean(region_ndvi)),
        "ndvi_min": float(np.min(region_ndvi)),
        "ndvi_max": float(np.max(region_ndvi)),
        "classification_code": int(np.median(region_codes)),  # majority class
        "vegetation_cover_pct": round(float(np.mean(region_veg) * 100), 2),
    }


def _init_data():
    """
    Initialize in-memory data store from synthetic rasters.
    Called once on module import.
    """
    global _zones, _zone_history

    # Try loading raster files; fall back to generating fresh arrays
    if os.path.isfile(RASTER_RED_PATH) and os.path.isfile(RASTER_NIR_PATH):
        red = load_band(RASTER_RED_PATH)
        nir = load_band(RASTER_NIR_PATH)
    else:
        # Generate arrays on the fly (no files needed)
        red, nir = _make_synthetic_arrays(width=20, height=20, seed=42)

    # Process full raster
    result = process_bands(red, nir)
    ndvi_arr = result["ndvi"]
    codes_arr = result["classification_codes"]
    veg_mask_arr = codes_arr >= 2  # class 2 or 3 = vegetation

    h, w = ndvi_arr.shape
    half_h, half_w = h // 2, w // 2

    # Define 4 quadrants + 1 center strip for zone 5
    quadrants = [
        (0, half_h, 0, half_w),       # Top-left: healthy
        (0, half_h, half_w, w),       # Top-right: stressed
        (half_h, h, 0, half_w),       # Bottom-left: bare
        (half_h, h, half_w, w),       # Bottom-right: water
        (half_h - 2, half_h + 2, half_w - 2, half_w + 2),  # Center cross-section
    ]

    _zones = []
    _zone_history = {}

    for i, (h0, h1, w0, w1) in enumerate(quadrants):
        zone_id = str(uuid.uuid4())
        stats = _compute_quadrant_stats(
            ndvi_arr, codes_arr, veg_mask_arr, h0, h1, w0, w1
        )

        status = _code_to_label(stats["classification_code"])
        area_values = [45.2, 38.7, 52.1, 28.5, 12.3]  # hectares per zone
        ndvi_current = stats["ndvi_mean"]

        zone = {
            "id": zone_id,
            "name": ZONE_NAMES[i] if i < len(ZONE_NAMES) else f"Zone {i+1}",
            "status": status,
            "ndvi_latest": round(ndvi_current, 4),
            "area_ha": area_values[i] if i < len(area_values) else 10.0,
            "vegetation_cover_pct": stats["vegetation_cover_pct"],
            "updated_at": NOW,
        }
        _zones.append(zone)

        # Generate historical data with slight variation
        history = _generate_history(zone_id, ndvi_current, status, stats["vegetation_cover_pct"])
        _zone_history[zone_id] = history

    return _zones


def _code_to_label(code: int) -> str:
    """Map classification code to label string."""
    from app.modules.reklamasi.ndvi import CLASS_MAP
    return CLASS_MAP.get(code, "unknown")


def _generate_history(
    zone_id: str,
    current_ndvi: float,
    current_status: str,
    current_veg_pct: float,
) -> list[dict]:
    """Generate 3-point time-series history with realistic variation."""
    rng = np.random.default_rng(hash(zone_id) % 2**32)

    history = []
    for i, dt in enumerate(HISTORY_DATES):
        # Each earlier date has slightly different NDVI (mostly improving trend)
        # Current date is the latest
        if dt == HISTORY_DATES[-1]:
            ndvi = current_ndvi
            veg_pct = current_veg_pct
        else:
            # Simulate trend: earlier dates have slightly worse NDVI
            offset = rng.uniform(-0.08, 0.15) * (len(HISTORY_DATES) - 1 - i)
            ndvi = max(-1.0, min(1.0, current_ndvi - offset))
            veg_pct = max(0.0, min(100.0, current_veg_pct - offset * 50))

        # Determine classification from NDVI value
        from app.modules.reklamasi.ndvi import classify_ndvi
        class_code = int(classify_ndvi(np.array([[ndvi]]))[0, 0])
        classification = _code_to_label(class_code)

        history.append({
            "image_date": dt,
            "ndvi_mean": round(ndvi, 4),
            "classification": classification,
            "vegetation_cover_pct": round(veg_pct, 2),
        })

    return history


def _compute_compliance_score(zones: list[dict]) -> float:
    """
    Simple compliance score based on vegetation cover.
    - Healthy vegetation: 100 points per zone
    - Stressed vegetation: 50 points per zone
    - Bare land: 10 points per zone
    - Water: 25 points per zone
    Score = (total / max_possible) * 100
    """
    score_map = {
        "vegetasi_sehat": 100,
        "vegetasi_stres": 50,
        "lahan_kosong": 10,
        "air": 25,
    }
    total = sum(score_map.get(z["status"], 0) for z in zones)
    max_possible = len(zones) * 100
    return round((total / max_possible) * 100, 2)


# ── Public API ───────────────────────────────────────────────

def get_all_zones() -> list[dict]:
    """Return all reclamation zones with latest status."""
    return _zones


def get_zone_by_id(zone_id: str) -> Optional[dict]:
    """Find a zone by its UUID string. Returns None if not found."""
    for z in _zones:
        if z["id"] == zone_id:
            return z
    return None


def get_zone_history(zone_id: str) -> list[dict]:
    """Return time-series history for a zone."""
    return _zone_history.get(zone_id, [])


def generate_report() -> dict:
    """Generate compliance report aggregating all zones."""
    status_summary = {"vegetasi_sehat": 0, "vegetasi_stres": 0, "lahan_kosong": 0, "air": 0}
    total_ndvi = 0.0
    total_veg_pct = 0.0
    report_zones = []

    for z in _zones:
        status_summary[z["status"]] = status_summary.get(z["status"], 0) + 1
        total_ndvi += z["ndvi_latest"]
        total_veg_pct += z["vegetation_cover_pct"]

        # Risk flag: status is air or lahan_kosong, or declining trend
        history = _zone_history.get(z["id"], [])
        risk_flag = z["status"] in ("air", "lahan_kosong")
        if not risk_flag and len(history) >= 2:
            # Check if recent trend is declining
            recent = history[-2:]  # last 2 points
            if len(recent) == 2 and recent[0]["ndvi_mean"] > recent[1]["ndvi_mean"]:
                risk_flag = True

        report_zones.append({
            "zone_id": z["id"],
            "name": z["name"],
            "status": z["status"],
            "ndvi_mean": z["ndvi_latest"],
            "area_ha": z["area_ha"],
            "risk_flag": risk_flag,
        })

    n = len(_zones) or 1
    compliance_score = _compute_compliance_score(_zones)

    return {
        "generated_at": NOW,
        "total_zones": len(_zones),
        "status_summary": status_summary,
        "overall_ndvi_mean": round(total_ndvi / n, 4),
        "overall_vegetation_cover_pct": round(total_veg_pct / n, 2),
        "compliance_score": compliance_score,
        "zones": report_zones,
    }


# ── Bootstrap on import ──────────────────────────────────────

_init_data()
