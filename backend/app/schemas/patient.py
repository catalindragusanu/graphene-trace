from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PatientSummary(BaseModel):
    id: int
    name: str
    email: str
    photo_url: Optional[str] = None
    medical_condition: Optional[str] = None
    last_updated: Optional[datetime] = None
    risk_level: str = "Unknown"  # Safe, High, Critical, Unknown
    avg_pressure: int = 0
    max_pressure: int = 0

    class Config:
        from_attributes = True
