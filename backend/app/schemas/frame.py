"""Pydantic schemas for frames"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class FrameBase(BaseModel):
    """Base frame schema"""
    user_id: int
    captured_at: datetime


class FrameCreate(FrameBase):
    """Schema for creating a frame"""
    data: List[List[int]]  # 32x32 matrix as nested list


class FrameResponse(FrameBase):
    """Schema for frame response"""
    id: int
    data: List[List[int]]  # 32x32 matrix as nested list
    created_at: datetime

    class Config:
        from_attributes = True


class FrameSummary(BaseModel):
    """Schema for frame summary (without data)"""
    id: int
    user_id: int
    captured_at: datetime
    has_metrics: bool
    has_alerts: bool
    average_pressure: Optional[int] = 0
    max_pressure: Optional[int] = 0

    class Config:
        from_attributes = True
