"""Pydantic schemas for alerts"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict


class AlertBase(BaseModel):
    """Base alert schema"""
    frame_id: int
    severity: str
    region: Optional[Dict] = None


class AlertResponse(AlertBase):
    """Schema for alert response"""
    id: int
    acknowledged: bool
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AlertWithFrame(AlertResponse):
    """Schema for alert with frame information"""
    frame_captured_at: datetime
    user_id: int
    user_name: str


class AcknowledgeAlertRequest(BaseModel):
    """Schema for acknowledging an alert"""
    acknowledged: bool
