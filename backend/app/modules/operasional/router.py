"""
KidecoIQ — Modul Operasional: Router
======================================
Endpoint API untuk modul operasional sesuai SPEC.md §6.

Menggunakan in-memory data_store (MVP). Saat PostgreSQL tersedia,
cukup ganti body fungsi dengan SQLAlchemy queries.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.modules.operasional import data_store
from app.modules.operasional.schemas import (
    FleetUnitResponse,
    AnomalyResponse,
    AnomalyPoint,
    AlertItem,
    AlertsResponse,
)

router = APIRouter(prefix="/operasional", tags=["Operasional"])


@router.get("/fleet", response_model=list[FleetUnitResponse])
async def get_fleet():
    """
    Status semua unit fleet alat berat.
    Setiap unit mencakup: unit_id, model, status operasional,
    rata-rata idle ratio, konsumsi BBM, total jam operasi,
    skor risiko maintenance, dan level alert.
    """
    return data_store.get_fleet_summary()


@router.get("/fleet/{unit_id}/anomaly", response_model=AnomalyResponse)
async def get_unit_anomaly(unit_id: str):
    """
    Deteksi anomali untuk satu unit fleet berdasarkan
    pola idle ratio dan konsumsi BBM per shift.

    Menggunakan IsolationForest untuk mengidentifikasi
    shift-shift dengan pola operasi yang tidak normal.

    Args:
        unit_id: String ID unit (contoh: HD-001).

    Returns:
        AnomalyResponse dengan daftar shift + label anomali.

    Raises:
        404: Jika unit_id tidak dikenal.
    """
    anomalies = data_store.get_unit_anomalies(unit_id)
    if anomalies is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unit '{unit_id}' not found",
        )

    shifts = [
        AnomalyPoint(
            shift=a["shift"],
            idle_ratio=float(a["idle_ratio"]),
            fuel_consumption=float(a["fuel_consumption"]),
            anomaly_score=int(a["anomaly_score"]),
            anomaly_label=str(a["anomaly_label"]),
        )
        for a in anomalies
    ]

    return AnomalyResponse(unit_id=unit_id, shifts=shifts)


@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts():
    """
    Daftar alert / peringatan maintenance aktif.

    Alert dihasilkan untuk unit dengan risk_score ≥ 30:
    - medium (30-69): monitoring ditingkatkan
    - high (≥70): maintenance segera diperlukan

    Unit dengan status normal (risk_score < 30) tidak muncul.
    """
    alerts = data_store.get_alerts()
    items = [AlertItem(**a) for a in alerts]

    return AlertsResponse(
        alerts=items,
        total_alerts=len(items),
        generated_at=datetime.now(timezone.utc),
    )
