"""
KidecoIQ — Modul Operasional: Pydantic Schemas
===============================================
Response models untuk endpoint API operasional.
Kontrak sesuai SPEC.md §6.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class FleetUnitResponse(BaseModel):
    """Status satu unit fleet dengan ringkasan operasional."""
    unit_id: str
    model: str = Field(description="Tipe/model alat berat")
    status: str = Field(description="Status operasional: active / idle / maintenance")
    idle_ratio_avg: float = Field(..., ge=0.0, le=100.0, description="Rata-rata idle ratio (%)")
    fuel_avg: float = Field(..., ge=0, description="Rata-rata konsumsi BBM (L/shift)")
    total_hours: float = Field(..., ge=0, description="Total jam operasi kumulatif")
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Skor risiko maintenance (0-100)")
    alert_level: str = Field(description="Level alert: low / medium / high")


class AnomalyPoint(BaseModel):
    """Satu shift data untuk deteksi anomali."""
    shift: int
    idle_ratio: float
    fuel_consumption: float
    anomaly_score: int = Field(description="-1 = anomali, 1 = normal")
    anomaly_label: str = Field(description="anomaly / normal")


class AnomalyResponse(BaseModel):
    """Hasil deteksi anomali untuk satu unit."""
    unit_id: str
    shifts: list[AnomalyPoint]


class AlertItem(BaseModel):
    """Satu alert/peringatan maintenance."""
    unit_id: str
    alert_level: str = Field(description="low / medium / high")
    risk_score: float
    message: str
    recommendation: str


class AlertsResponse(BaseModel):
    """Daftar semua alert aktif."""
    alerts: list[AlertItem]
    total_alerts: int
    generated_at: datetime
