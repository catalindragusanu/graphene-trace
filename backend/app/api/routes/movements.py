"""Movement Events API Routes"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.frame import Frame
from app.models.movement_event import MovementEvent
from app.services.authorization_service import AuthorizationService
from app.services.movement_analyzer import MovementAnalyzer
from app.utils.pressure_matrix import decode_matrix
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)


class MovementEventResponse(BaseModel):
    id: int
    user_id: int
    from_frame_id: int
    to_frame_id: int
    movement_type: str
    quality_score: float
    metrics: dict
    detected_at: datetime

    class Config:
        from_attributes = True


class MovementSummary(BaseModel):
    total_movements: int
    macro_movements: int
    micro_movements: int
    avg_quality_score: float
    last_macro_movement: Optional[datetime]
    time_since_last_macro: Optional[int]  # minutes


@router.post("/analyze", response_model=dict)
def analyze_recent_movements(
    user_id: Optional[int] = Query(None, description="User ID (clinicians only)"),
    hours: int = Query(24, description="Hours to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze movements for a user over the specified time period.
    Processes consecutive frames and detects movement events.
    """
    # Determine target user
    target_user_id = AuthorizationService.resolve_target_user_id(current_user, user_id, db)

    # Get frames from the last N hours
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    frames = db.query(Frame).filter(
        Frame.user_id == target_user_id,
        Frame.captured_at >= since
    ).order_by(Frame.captured_at.asc()).all()

    if len(frames) < 2:
        return {
            "message": "Not enough frames to analyze",
            "frames_found": len(frames),
            "movements_detected": 0
        }

    # Analyze consecutive frames
    movements_detected = 0
    macro_count = 0
    micro_count = 0

    for i in range(1, len(frames)):
        prev_frame = frames[i-1]
        curr_frame = frames[i]

        # Decode matrices
        try:
            prev_matrix = decode_matrix(prev_frame.data)
            curr_matrix = decode_matrix(curr_frame.data)
        except Exception:
            logger.warning("Skipping undecodable frame pair %s -> %s", prev_frame.id, curr_frame.id)
            continue

        # Analyze movement
        movement_type, quality_score, metrics = MovementAnalyzer.analyze_movement(
            prev_matrix, curr_matrix
        )

        if movement_type != 'none':
            # Check if event already exists
            existing = db.query(MovementEvent).filter(
                MovementEvent.from_frame_id == prev_frame.id,
                MovementEvent.to_frame_id == curr_frame.id
            ).first()

            if not existing:
                # Create new movement event
                event = MovementEvent(
                    user_id=target_user_id,
                    from_frame_id=prev_frame.id,
                    to_frame_id=curr_frame.id,
                    movement_type=movement_type,
                    quality_score=quality_score,
                    metrics=metrics,
                    detected_at=curr_frame.captured_at
                )
                db.add(event)
                movements_detected += 1

                if movement_type == 'macro':
                    macro_count += 1
                elif movement_type == 'micro':
                    micro_count += 1

    db.commit()

    return {
        "message": "Movement analysis complete",
        "frames_analyzed": len(frames),
        "movements_detected": movements_detected,
        "macro_movements": macro_count,
        "micro_movements": micro_count
    }


@router.get("/summary", response_model=MovementSummary)
def get_movement_summary(
    user_id: Optional[int] = Query(None, description="User ID (clinicians only)"),
    hours: int = Query(24, description="Hours to summarize"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get movement summary for a user"""
    # Determine target user
    target_user_id = AuthorizationService.resolve_target_user_id(current_user, user_id, db)

    # Get movement events from the last N hours
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    events = db.query(MovementEvent).filter(
        MovementEvent.user_id == target_user_id,
        MovementEvent.detected_at >= since
    ).all()

    if not events:
        return MovementSummary(
            total_movements=0,
            macro_movements=0,
            micro_movements=0,
            avg_quality_score=0.0,
            last_macro_movement=None,
            time_since_last_macro=None
        )

    # Calculate summary
    macro_events = [e for e in events if e.movement_type == 'macro']
    micro_events = [e for e in events if e.movement_type == 'micro']

    avg_quality = sum(e.quality_score for e in events) / len(events)

    last_macro = max((e.detected_at for e in macro_events), default=None)
    time_since_macro = None
    if last_macro:
        time_since_macro = int((datetime.now(timezone.utc) - last_macro).total_seconds() / 60)

    return MovementSummary(
        total_movements=len(events),
        macro_movements=len(macro_events),
        micro_movements=len(micro_events),
        avg_quality_score=round(avg_quality, 2),
        last_macro_movement=last_macro,
        time_since_last_macro=time_since_macro
    )


@router.get("", response_model=List[MovementEventResponse])
def get_movement_events(
    user_id: Optional[int] = Query(None, description="User ID (clinicians only)"),
    limit: int = Query(50, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent movement events"""
    # Determine target user
    target_user_id = AuthorizationService.resolve_target_user_id(current_user, user_id, db)

    events = db.query(MovementEvent).filter(
        MovementEvent.user_id == target_user_id
    ).order_by(MovementEvent.detected_at.desc()).limit(limit).all()

    return events
