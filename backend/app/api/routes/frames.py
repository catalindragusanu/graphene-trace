"""Frames API routes"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
import numpy as np
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.frame import Frame
from app.models.metric import Metric
from app.models.alert import Alert
from app.schemas.frame import FrameResponse, FrameSummary
from app.utils.pressure_matrix import decode_matrix, matrix_to_list
from app.services.authorization_service import AuthorizationService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[FrameSummary])
def get_frames(
    start_time: Optional[datetime] = Query(None, description="Start time filter"),
    end_time: Optional[datetime] = Query(None, description="End time filter"),
    user_id: Optional[int] = Query(None, description="Filter by user ID (clinicians only)"),
    limit: int = Query(100, le=1000, description="Maximum number of frames to return"),
    offset: int = Query(0, ge=0, description="Number of frames to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get frames with pagination and filters.

    Patients can only see their own frames.
    Clinicians can see frames from patients in their groups.

    Args:
        start_time: Optional start time filter
        end_time: Optional end time filter
        user_id: Optional user ID filter (clinicians only)
        limit: Maximum frames to return
        offset: Pagination offset
        current_user: Current authenticated user
        db: Database session

    Returns:
        List[FrameSummary]: List of frame summaries
    """
    # Build query
    query = db.query(Frame)

    # Apply authorization filtering
    query = AuthorizationService.filter_by_access(
        current_user=current_user,
        query=query,
        user_id_column=Frame.user_id,
        requested_user_id=user_id,
        db=db
    )

    # Apply time filters
    if start_time:
        query = query.filter(Frame.captured_at >= start_time)
    if end_time:
        query = query.filter(Frame.captured_at <= end_time)

    # Order by timestamp (most recent first)
    query = query.order_by(Frame.captured_at.desc())

    # Apply pagination
    frames = query.offset(offset).limit(limit).all()

    # Look up metric/alert presence for the whole page in two queries (avoids N+1)
    frame_ids = [frame.id for frame in frames]
    frames_with_metrics = {
        row[0] for row in db.query(Metric.frame_id).filter(Metric.frame_id.in_(frame_ids)).distinct()
    } if frame_ids else set()
    frames_with_alerts = {
        row[0] for row in db.query(Alert.frame_id).filter(Alert.frame_id.in_(frame_ids)).distinct()
    } if frame_ids else set()

    # Build response with summary information
    result = []
    for frame in frames:
        has_metrics = frame.id in frames_with_metrics
        has_alerts = frame.id in frames_with_alerts

        # Summary stats are derived from the stored matrix
        try:
            matrix = decode_matrix(frame.data)
            avg = int(np.mean(matrix))
            mx = int(np.max(matrix))
        except Exception:
            logger.warning("Could not decode frame %s for summary", frame.id)
            avg = 0
            mx = 0

        result.append(FrameSummary(
            id=frame.id,
            user_id=frame.user_id,
            captured_at=frame.captured_at,
            has_metrics=has_metrics,
            has_alerts=has_alerts,
            average_pressure=avg,
            max_pressure=mx
        ))

    return result


@router.get("/{frame_id}", response_model=FrameResponse)
def get_frame(
    frame_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific frame with full data.

    Args:
        frame_id: Frame ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        FrameResponse: Frame data including pressure matrix

    Raises:
        HTTPException: If frame not found or access denied
    """
    frame = db.query(Frame).filter(Frame.id == frame_id).first()

    if not frame:
        raise HTTPException(status_code=404, detail="Frame not found")

    # Check access permissions (denies unknown roles by default)
    AuthorizationService.require_patient_access(current_user, frame.user_id, db)

    # Decode pressure matrix
    try:
        matrix = decode_matrix(frame.data)
        matrix_list = matrix_to_list(matrix)
    except Exception:
        logger.exception("Error decoding frame %s", frame_id)
        raise HTTPException(status_code=500, detail="Error decoding frame data")

    return FrameResponse(
        id=frame.id,
        user_id=frame.user_id,
        captured_at=frame.captured_at,
        data=matrix_list,
        created_at=frame.created_at
    )
