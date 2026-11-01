"""User model for authentication and role-based access"""
from sqlalchemy import Column, Integer, String, Enum, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """User roles for RBAC"""
    patient = "patient"
    clinician = "clinician"


class User(Base):
    """User model for both patients and clinicians"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    medical_condition = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    frames = relationship("Frame", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user")
    groups_owned = relationship("UserGroup", back_populates="clinician", cascade="all, delete-orphan")
    movement_events = relationship("MovementEvent", back_populates="user", cascade="all, delete-orphan")
    risk_scores = relationship("RiskScore", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
