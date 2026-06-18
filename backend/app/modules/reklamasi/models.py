"""
KidecoIQ — Modul Reklamasi: SQLAlchemy Models
Tabel: reklamasi_zones, reklamasi_history
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, UniqueConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from app.core.database import Base


class ReklamasiZone(Base):
    __tablename__ = "reklamasi_zones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    geometry = Column(Geometry("POLYGON", srid=4326), nullable=True)
    status = Column(String(20), nullable=False, default="unknown")
    ndvi_latest = Column(Float, nullable=True)
    area_ha = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<ReklamasiZone id={self.id} name='{self.name}' status='{self.status}'>"


class ReklamasiHistory(Base):
    __tablename__ = "reklamasi_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("reklamasi_zones.id", ondelete="CASCADE"), nullable=False)
    ndvi_mean = Column(Float, nullable=False)
    ndvi_min = Column(Float, nullable=True)
    ndvi_max = Column(Float, nullable=True)
    classification = Column(String(20), nullable=False)
    vegetation_cover_pct = Column(Float, nullable=True)
    image_date = Column(Date, nullable=False)
    source_band_path = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("zone_id", "image_date", name="uq_zone_image_date"),
    )

    def __repr__(self) -> str:
        return f"<ReklamasiHistory zone={self.zone_id} date={self.image_date} ndvi={self.ndvi_mean:.4f}>"
