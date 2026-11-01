"""Alerts API routes"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.frame import Frame
from app.models.alert import Alert
from app.schemas.alert import AlertResponse, AlertWithFrame, AcknowledgeAlertRequest
from app.services.authorization_service import AuthorizationService

router = APIRouter()


@router.get("", response_model=List[AlertWithFrame])
def get_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledged status"),
    user_id: Optional[int] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get alerts with filters.

    Returns:
        List[AlertWithFrame]: List of alerts with frame information
    """
    # Build query
    query = db.query(
        Alert,
        Frame.captured_at,
        Frame.user_id,
        User.name
    ).join(Frame, Alert.frame_id == Frame.id).join(User, Frame.user_id == User.id)

    # Apply authorization filtering
    query = AuthorizationService.filter_by_access(
        current_user=current_user,
        query=query,
        user_id_column=Frame.user_id,
        requested_user_id=user_id,
        db=db
    )

    # Apply filters
    if severity:
        query = query.filter(Alert.severity == severity)
    if acknowledged is not None:
        query = query.filter(Alert.acknowledged == acknowledged)

    # Order by timestamp
    query = query.order_by(Alert.created_at.desc())

    # Apply pagination
    results = query.offset(offset).limit(limit).all()

    # Build response
    return [
        AlertWithFrame(
            id=alert.id,
            frame_id=alert.frame_id,
            severity=alert.severity.value,
            region=alert.region,
            acknowledged=alert.acknowledged,
            acknowledged_by=alert.acknowledged_by,
            acknowledged_at=alert.acknowledged_at,
            created_at=alert.created_at,
            frame_captured_at=captured_at,
            user_id=user_id,
            user_name=user_name
        )
        for alert, captured_at, user_id, user_name in results
    ]


@router.patch("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: int,
    request: AcknowledgeAlertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Acknowledge or unacknowledge an alert.

    Args:
        alert_id: Alert ID
        request: Acknowledge request
        current_user: Current user
        db: Database session

    Returns:
        AlertResponse: Updated alert
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    frame = db.query(Frame).filter(Frame.id == alert.frame_id).first()
    if not frame:
        raise HTTPException(status_code=404, detail="Alert not found")
    AuthorizationService.require_patient_access(current_user, frame.user_id, db)

    # Update acknowledgement
    alert.acknowledged = request.acknowledged
    if request.acknowledged:
        alert.acknowledged_by = current_user.id
        alert.acknowledged_at = datetime.now(timezone.utc)
    else:
        alert.acknowledged_by = None
        alert.acknowledged_at = None

    db.commit()
    db.refresh(alert)

    return alert
