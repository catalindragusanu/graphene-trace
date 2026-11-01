"""Shared Pydantic validators for input validation"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class DateRangeQuery(BaseModel):
    """Query parameters for date range filtering"""

    start_time: Optional[datetime] = Field(None, description="Start time for filtering")
    end_time: Optional[datetime] = Field(None, description="End time for filtering")

    @field_validator('end_time')
    @classmethod
    def validate_date_range(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Ensure end_time is after start_time"""
        if v is not None:
            start_time = info.data.get('start_time')
            if start_time is not None and v < start_time:
                raise ValueError('end_time must be after start_time')
        return v

    @field_validator('start_time', 'end_time')
    @classmethod
    def validate_not_future(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Ensure dates are not in the future"""
        if v is not None and v > datetime.now():
            raise ValueError('Date cannot be in the future')
        return v


class PaginationQuery(BaseModel):
    """Query parameters for pagination"""

    limit: int = Field(100, ge=1, le=1000, description="Maximum number of items to return")
    offset: int = Field(0, ge=0, description="Number of items to skip")

    @field_validator('limit')
    @classmethod
    def validate_reasonable_limit(cls, v: int) -> int:
        """Warn about very large limits"""
        if v > 500:
            # In production, you might want to log this
            pass
        return v


class EmailValidator:
    """Reusable email validation"""

    @staticmethod
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Basic email validation"""
        if not v or '@' not in v:
            raise ValueError('Invalid email address')
        if len(v) > 254:  # RFC 5321
            raise ValueError('Email address too long')
        return v.lower().strip()
