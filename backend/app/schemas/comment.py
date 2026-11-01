"""Pydantic schemas for comments"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
import bleach


class CommentBase(BaseModel):
    """Base comment schema"""
    frame_id: int = Field(..., gt=0, description="Frame ID must be positive")
    text: str = Field(..., min_length=1, max_length=5000, description="Comment text (1-5000 characters)")
    parent_comment_id: Optional[int] = Field(None, gt=0, description="Parent comment ID must be positive if provided")

    @field_validator('text')
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        """Strip HTML tags to prevent XSS attacks"""
        return bleach.clean(v, tags=[], strip=True)

    @field_validator('text')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure comment is not empty after stripping whitespace"""
        if not v.strip():
            raise ValueError('Comment text cannot be empty or only whitespace')
        return v.strip()


class CommentCreate(CommentBase):
    """Schema for creating a comment"""


class CommentResponse(CommentBase):
    """Schema for comment response"""
    id: int
    user_id: int
    user_name: str
    user_role: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommentThread(CommentResponse):
    """Schema for comment with replies"""
    replies: List["CommentResponse"] = []

    class Config:
        from_attributes = True
