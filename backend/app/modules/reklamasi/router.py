"""
KidecoIQ — Modul Reklamasi: Router
====================================
Endpoint API untuk modul reklamasi sesuai SPEC.md §5.

Menggunakan in-memory data_store (MVP). Saat PostgreSQL tersedia,
cukup ganti body fungsi dengan SQLAlchemy queries.
"""

from fastapi import APIRouter, HTTPException

from app.modules.reklamasi import data_store
from app.modules.reklamasi.schemas import (
    ZoneResponse,
    ZoneHistoryResponse,
    ReportResponse,
)

router = APIRouter(prefix="/reklamasi", tags=["Reklamasi"])


@router.get("/zones", response_model=list[ZoneResponse])
async def get_zones():
    """
    Daftar semua zona reklamasi beserta status terbaru.
    Setiap zona mencakup: id, nama, status klasifikasi,
    NDVI terkini, luas area, dan persentase tutupan vegetasi.
    """
    zones = data_store.get_all_zones()
    return [ZoneResponse(**z) for z in zones]


@router.get("/zones/{zone_id}/history", response_model=ZoneHistoryResponse)
async def get_zone_history(zone_id: str):
    """
    Riwayat NDVI time-series untuk satu zona reklamasi.
    Mengembalikan data NDVI pada beberapa titik waktu untuk
    analisis tren pertumbuhan vegetasi.

    Args:
        zone_id: UUID string dari zona.

    Returns:
        ZoneHistoryResponse dengan daftar titik waktu.

    Raises:
        404: Jika zone_id tidak ditemukan.
    """
    zone = data_store.get_zone_by_id(zone_id)
    if zone is None:
        raise HTTPException(
            status_code=404,
            detail=f"Zone with id '{zone_id}' not found",
        )
    history = data_store.get_zone_history(zone_id)
    return ZoneHistoryResponse(
        zone_id=zone_id,
        zone_name=zone["name"],
        history=history,
    )


@router.get("/report", response_model=ReportResponse)
async def get_report():
    """
    Laporan kepatuhan reklamasi komprehensif.
    Berisi ringkasan status semua zona, rata-rata NDVI,
    persentase tutupan vegetasi, skor kepatuhan (0-100),
    serta daftar setiap zona dengan risk flag.

    Skor kepatuhan:
        - vegetasi_sehat  → 100 poin
        - vegetasi_stres  → 50 poin
        - lahan_kosong    → 10 poin
        - air             → 25 poin
        - Skor = (total / max_possible) × 100
    """
    report = data_store.generate_report()
    return ReportResponse(**report)
