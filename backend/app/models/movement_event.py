"""Movement Event Model"""
from sqlalchemy import Column, Integer, ForeignKey, String, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class MovementEvent(Base):
    """Movement event detected between consecutive frames"""
    __tablename__ = "movement_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    from_frame_id = Column(Integer, ForeignKey("frames.id"), nullable=False)
    to_frame_id = Column(Integer, ForeignKey("frames.id"), nullable=False)
    movement_type = Column(String(10), nullable=False)  # 'macro', 'micro', 'none'
    quality_score = Column(Float, nullable=False)  # 0.0-1.0
    metrics = Column(JSON)  # Detailed analysis metrics
    detected_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="movement_events")
    from_frame = relationship("Frame", foreign_keys=[from_frame_id])
    to_frame = relationship("Frame", foreign_keys=[to_frame_id])

    def __repr__(self):
        return f"<MovementEvent(id={self.id}, type={self.movement_type}, quality={self.quality_score:.2f})>"
