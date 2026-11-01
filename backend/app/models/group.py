"""Group models for clinician patient management"""
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# Association table for many-to-many relationship between groups and patients
group_membership = Table(
    'group_membership',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('user_groups.id'), primary_key=True),
    Column('patient_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('added_at', DateTime(timezone=True), server_default=func.now())
)


class UserGroup(Base):
    """UserGroup model for clinicians to organize patients"""
    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    clinician_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    clinician = relationship("User", back_populates="groups_owned")
    patients = relationship(
        "User",
        secondary=group_membership,
        backref="patient_groups"
    )

    def __repr__(self):
        return f"<UserGroup(id={self.id}, name='{self.name}', clinician_id={self.clinician_id})>"
