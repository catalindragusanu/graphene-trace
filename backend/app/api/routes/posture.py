"""Posture Labeling API Routes

Allows clinicians to label frames with posture data for ML training.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.posture_label import PostureLabel
from app.models.frame import Frame
from app.services.authorization_service import AuthorizationService
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class PostureLabelCreate(BaseModel):
    frame_id: int
    posture: str  # supine, left_lateral, right_lateral, seated


class PostureLabelResponse(BaseModel):
    id: int
    frame_id: int
    posture: str
    labeled_by: int
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/label", response_model=PostureLabelResponse)
def create_posture_label(
    label_data: PostureLabelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a posture label for a frame.
    Only clinicians can label frames.
    """
    if current_user.role != UserRole.clinician:
        raise HTTPException(status_code=403, detail="Only clinicians can label frames")

    # Validate posture value
    valid_postures = ['supine', 'left_lateral', 'right_lateral', 'seated']
    if label_data.posture not in valid_postures:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid posture. Must be one of: {', '.join(valid_postures)}"
        )

    # Check if frame exists
    frame = db.query(Frame).filter(Frame.id == label_data.frame_id).first()
    if not frame:
        raise HTTPException(status_code=404, detail="Frame not found")

    AuthorizationService.require_patient_access(current_user, frame.user_id, db)

    # Check if label already exists
    existing = db.query(PostureLabel).filter(
        PostureLabel.frame_id == label_data.frame_id
    ).first()

    if existing:
        # Update existing label
        existing.posture = label_data.posture
        existing.labeled_by = current_user.id
        db.commit()
        db.refresh(existing)
        return existing

    # Create new label
    label = PostureLabel(
        frame_id=label_data.frame_id,
        posture=label_data.posture,
        labeled_by=current_user.id
    )
    db.add(label)
    db.commit()
    db.refresh(label)

    return label


@router.get("/labels", response_model=List[PostureLabelResponse])
def get_posture_labels(
    limit: int = Query(100, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all posture labels (for training data export)"""
    if current_user.role != UserRole.clinician:
        raise HTTPException(status_code=403, detail="Only clinicians can access labels")

    patient_ids = AuthorizationService.get_accessible_patients(current_user, db)
    labels = db.query(PostureLabel).join(
        Frame, PostureLabel.frame_id == Frame.id
    ).filter(
        Frame.user_id.in_(patient_ids)
    ).order_by(
        PostureLabel.created_at.desc()
    ).limit(limit).all()

    return labels


@router.get("/stats", response_model=dict)
def get_labeling_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get labeling statistics"""
    if current_user.role != UserRole.clinician:
        raise HTTPException(status_code=403, detail="Only clinicians can access stats")

    patient_ids = AuthorizationService.get_accessible_patients(current_user, db)
    scoped = db.query(PostureLabel).join(
        Frame, PostureLabel.frame_id == Frame.id
    ).filter(Frame.user_id.in_(patient_ids))
    total = scoped.count()

    # Count by posture
    supine = scoped.filter(PostureLabel.posture == 'supine').count()
    left_lateral = scoped.filter(PostureLabel.posture == 'left_lateral').count()
    right_lateral = scoped.filter(PostureLabel.posture == 'right_lateral').count()
    seated = scoped.filter(PostureLabel.posture == 'seated').count()

    return {
        "total_labels": total,
        "by_posture": {
            "supine": supine,
            "left_lateral": left_lateral,
            "right_lateral": right_lateral,
            "seated": seated
        },
        "target": 2000,
        "progress": round((total / 2000) * 100, 1) if total < 2000 else 100.0
    }
