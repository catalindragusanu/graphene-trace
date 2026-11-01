"""Posture Label Model for ML Training"""
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class PostureLabel(Base):
    """Posture labels for training ML model"""
    __tablename__ = "posture_labels"

    id = Column(Integer, primary_key=True, index=True)
    frame_id = Column(Integer, ForeignKey("frames.id"), nullable=False, index=True)
    posture = Column(String(20), nullable=False)  # supine, left_lateral, right_lateral, seated
    labeled_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    frame = relationship("Frame")
    labeler = relationship("User")

    def __repr__(self):
        return f"<PostureLabel(id={self.id}, frame_id={self.frame_id}, posture='{self.posture}')>"
