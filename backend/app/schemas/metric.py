"""Pydantic schemas for metrics"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict


class MetricBase(BaseModel):
    """Base metric schema"""
    frame_id: int
    peak_pressure: float
    contact_area_percent: float
    high_pressure_region: Optional[Dict] = None
    alert_generated: bool


class MetricResponse(MetricBase):
    """Schema for metric response"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MetricWithFrame(MetricResponse):
    """Schema for metric with frame timestamp"""
    frame_captured_at: datetime
    user_id: int


class MetricsSummary(BaseModel):
    """Schema for aggregated metrics summary"""
    avg_peak_pressure: float
    max_peak_pressure: float
    min_peak_pressure: float
    avg_contact_area: float
    total_alerts: int
    frames_analyzed: int
