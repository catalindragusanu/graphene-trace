"""Risk Score Model"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class RiskScore(Base):
    """Risk score calculation result"""
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    score = Column(Integer, nullable=False)  # 0-100
    factors = Column(JSON)  # Breakdown of contributing factors
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="risk_scores")

    def __repr__(self):
        return f"<RiskScore(id={self.id}, user_id={self.user_id}, score={self.score})>"
