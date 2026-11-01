"""Alert model for high-pressure warnings"""
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class AlertSeverity(str, enum.Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Alert(Base):
    """Alert model for flagging high-pressure regions"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    frame_id = Column(Integer, ForeignKey("frames.id"), nullable=False, index=True)
    # Persist enum values ('low', ...) to match the labels created by the migration
    severity = Column(
        Enum(AlertSeverity, values_callable=lambda enum_cls: [member.value for member in enum_cls]),
        nullable=False
    )
    region = Column(JSONB)  # {"x1": int, "y1": int, "x2": int, "y2": int, "area": int}
    acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    frame = relationship("Frame", back_populates="alerts")

    def __repr__(self):
        return (
            f"<Alert(id={self.id}, frame_id={self.frame_id}, "
            f"severity='{self.severity}', acknowledged={self.acknowledged})>"
        )
