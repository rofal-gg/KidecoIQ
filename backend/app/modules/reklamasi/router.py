"""
KidecoIQ — Modul Reklamasi: Router
====================================
Endpoint API untuk modul reklamasi sesuai SPEC.md §5.

Menggunakan in-memory data_store (MVP). Saat PostgreSQL tersedia,
cukup ganti body fungsi dengan SQLAlchemy queries.
"""

from fastapi import APIRouter, HTTPException, status

from app.modules.reklamasi import data_store
from app.modules.reklamasi.schemas import (
    ZoneResponse,
    ZoneHistoryResponse,
    ReportResponse,
    ZoneCreateRequest,
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


@router.post("/zones", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
async def create_zone(body: ZoneCreateRequest):
    """
    Tambah zona reklamasi baru.

    Menerima nama zona dan bounding box (sudut barat-daya dan timur-laut),
    kemudian menghasilkan data NDVI sintetis untuk zona tersebut.

    Args:
        body: JSON body dengan field name, southwest_lat/lng, northeast_lat/lng.

    Returns:
        ZoneResponse dari zona yang baru dibuat.

    Raises:
        409: Jika nama zona sudah ada.
        422: Jika validasi bounding box gagal.
    """
    # Validate bounding box order
    if body.southwest_lat >= body.northeast_lat:
        raise HTTPException(
            status_code=422,
            detail="southwest_lat must be less than northeast_lat",
        )
    if body.southwest_lng >= body.northeast_lng:
        raise HTTPException(
            status_code=422,
            detail="southwest_lng must be less than northeast_lng",
        )

    try:
        zone = data_store.add_zone(body.model_dump())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    return ZoneResponse(**zone)


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
