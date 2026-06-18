"""
KidecoIQ — Modul Operasional: SQLAlchemy Models
Tabel: fleet_units, fleet_logs
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from app.core.database import Base


class FleetUnit(Base):
    __tablename__ = "fleet_units"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unit_id = Column(String(50), unique=True, nullable=False)
    model = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default="active")
    operating_hours = Column(Float, default=0.0)
    last_latitude = Column(Float, nullable=True)
    last_longitude = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<FleetUnit unit_id='{self.unit_id}' status='{self.status}'>"


class FleetLog(Base):
    __tablename__ = "fleet_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("fleet_units.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), nullable=False)
    fuel_consumption = Column(Float, nullable=True)
    engine_temp = Column(Float, nullable=True)
    location = Column(Geometry("POINT", srid=4326), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("idx_fleet_logs_unit_timestamp", "unit_id", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<FleetLog unit={self.unit_id} ts={self.timestamp} status='{self.status}'>"
