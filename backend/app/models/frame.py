"""Frame model for storing pressure matrix data"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Frame(Base):
    """Frame model storing 32x32 pressure matrix data as BYTEA"""
    __tablename__ = "frames"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    captured_at = Column(DateTime(timezone=True), nullable=False, index=True)
    data = Column(LargeBinary, nullable=False)  # 1024 bytes (32x32 uint8)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="frames")
    metric = relationship("Metric", back_populates="frame", uselist=False, cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="frame", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="frame", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Frame(id={self.id}, user_id={self.user_id}, captured_at='{self.captured_at}')>"
