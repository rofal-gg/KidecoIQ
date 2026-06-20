"""
KidecoIQ — Modul Reklamasi: Pydantic Schemas
=============================================
Response models untuk endpoint API reklamasi.
Kontrak sesuai SPEC.md §5.
"""

from datetime import date, datetime
from pydantic import BaseModel, Field


class ZoneResponse(BaseModel):
    """Daftar zona reklamasi dengan status terbaru."""
    id: str
    name: str
    status: str = Field(description="Status klasifikasi: air / lahan_kosong / vegetasi_stres / vegetasi_sehat")
    ndvi_latest: float = Field(..., ge=-1.0, le=1.0)
    area_ha: float = Field(..., ge=0)
    vegetation_cover_pct: float = Field(..., ge=0.0, le=100.0)
    trend_prediction: str = Field(description="Prediksi tren NDVI 30 hari: meningkat / menurun / stabil")
    updated_at: datetime
    southwest_lat: float = Field(..., ge=-90, le=90, description="Latitude sudut barat-daya bounding box zona")
    southwest_lng: float = Field(..., ge=-180, le=180, description="Longitude sudut barat-daya bounding box zona")
    northeast_lat: float = Field(..., ge=-90, le=90, description="Latitude sudut timur-laut bounding box zona")
    northeast_lng: float = Field(..., ge=-180, le=180, description="Longitude sudut timur-laut bounding box zona")


class HistoryPoint(BaseModel):
    """Satu titik data time-series NDVI."""
    image_date: date
    ndvi_mean: float = Field(..., ge=-1.0, le=1.0)
    classification: str
    vegetation_cover_pct: float = Field(..., ge=0.0, le=100.0)


class ZoneHistoryResponse(BaseModel):
    """Riwayat NDVI time-series untuk satu zona."""
    zone_id: str
    zone_name: str
    history: list[HistoryPoint]


class StatusSummary(BaseModel):
    """Ringkasan jumlah zona per status."""
    vegetasi_sehat: int = 0
    vegetasi_stres: int = 0
    lahan_kosong: int = 0
    air: int = 0


class ZoneReportItem(BaseModel):
    """Item zona dalam laporan kepatuhan."""
    zone_id: str
    name: str
    status: str
    ndvi_mean: float
    area_ha: float
    risk_flag: bool = Field(description="True jika tren NDVI menurun atau status kritis")


class ZoneCreateRequest(BaseModel):
    """Request body untuk membuat zona reklamasi baru."""
    name: str = Field(..., min_length=1, max_length=200,
                      description="Nama zona reklamasi yang akan ditambahkan")
    southwest_lat: float = Field(..., ge=-90, le=90,
                                 description="Latitude sudut barat-daya bounding box")
    southwest_lng: float = Field(..., ge=-180, le=180,
                                 description="Longitude sudut barat-daya bounding box")
    northeast_lat: float = Field(..., ge=-90, le=90,
                                 description="Latitude sudut timur-laut bounding box")
    northeast_lng: float = Field(..., ge=-180, le=180,
                                 description="Longitude sudut timur-laut bounding box")


class ReportResponse(BaseModel):
    """Laporan kepatuhan reklamasi komprehensif."""
    generated_at: datetime
    total_zones: int
    status_summary: StatusSummary
    overall_ndvi_mean: float
    overall_vegetation_cover_pct: float = Field(..., ge=0.0, le=100.0)
    compliance_score: float = Field(..., ge=0.0, le=100.0,
                                    description="Skor kepatuhan 0-100, semakin tinggi semakin baik")
    zones: list[ZoneReportItem]
