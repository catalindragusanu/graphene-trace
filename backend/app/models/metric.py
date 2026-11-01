"""Metric model for storing pre-computed analytics"""
from sqlalchemy import Column, Integer, ForeignKey, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Metric(Base):
    """Metric model storing pre-computed analytics for each frame"""
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    frame_id = Column(Integer, ForeignKey("frames.id"), unique=True, nullable=False, index=True)
    peak_pressure = Column(Float, nullable=False)
    contact_area_percent = Column(Float, nullable=False)
    high_pressure_region = Column(JSONB)  # {"x1": int, "y1": int, "x2": int, "y2": int, "area": int}
    alert_generated = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    frame = relationship("Frame", back_populates="metric")

    def __repr__(self):
        return (
            f"<Metric(id={self.id}, frame_id={self.frame_id}, ppi={self.peak_pressure:.1f}, "
            f"contact_area={self.contact_area_percent:.1f}%)>"
        )
