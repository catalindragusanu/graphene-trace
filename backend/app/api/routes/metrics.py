"""Metrics API routes"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import Integer, func
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.frame import Frame
from app.models.metric import Metric
from app.schemas.metric import MetricWithFrame, MetricsSummary
from app.services.authorization_service import AuthorizationService
from app.cache import cache_result

router = APIRouter()


@router.get("", response_model=List[MetricWithFrame])
def get_metrics(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    user_id: Optional[int] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get metrics with pagination and filters.

    Returns:
        List[MetricWithFrame]: List of metrics with frame timestamps
    """
    # Build query joining metrics with frames
    query = db.query(
        Metric,
        Frame.captured_at,
        Frame.user_id
    ).join(Frame, Metric.frame_id == Frame.id)

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

    # Order by timestamp
    query = query.order_by(Frame.captured_at.desc())

    # Apply pagination
    results = query.offset(offset).limit(limit).all()

    # Build response
    return [
        MetricWithFrame(
            id=metric.id,
            frame_id=metric.frame_id,
            peak_pressure=metric.peak_pressure,
            contact_area_percent=metric.contact_area_percent,
            high_pressure_region=metric.high_pressure_region,
            alert_generated=metric.alert_generated,
            created_at=metric.created_at,
            frame_captured_at=captured_at,
            user_id=user_id
        )
        for metric, captured_at, user_id in results
    ]


@cache_result("metrics_summary", ttl=60)  # Cache for 1 minute
def _get_cached_metrics_summary(
    user_id: Optional[int],
    start_time: Optional[str],
    end_time: Optional[str],
    current_user_id: int,
    current_user_role: str
) -> dict:
    """
    Cacheable helper for metrics summary (called by endpoint).
    Converts datetime to string for JSON serialization in cache.
    """
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        # Reconstruct user object for authorization
        from app.models.user import User
        current_user = db.query(User).filter(User.id == current_user_id).first()

        # Build query
        query = db.query(Metric).join(Frame, Metric.frame_id == Frame.id)

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
            query = query.filter(Frame.captured_at >= datetime.fromisoformat(start_time))
        if end_time:
            query = query.filter(Frame.captured_at <= datetime.fromisoformat(end_time))

        # Calculate aggregates
        aggregates = query.with_entities(
            func.avg(Metric.peak_pressure).label('avg_peak'),
            func.max(Metric.peak_pressure).label('max_peak'),
            func.min(Metric.peak_pressure).label('min_peak'),
            func.avg(Metric.contact_area_percent).label('avg_contact'),
            func.sum(Metric.alert_generated.cast(Integer)).label('total_alerts'),
            func.count(Metric.id).label('frames_analyzed')
        ).first()

        return {
            "avg_peak_pressure": float(aggregates.avg_peak or 0.0),
            "max_peak_pressure": float(aggregates.max_peak or 0.0),
            "min_peak_pressure": float(aggregates.min_peak or 0.0),
            "avg_contact_area": float(aggregates.avg_contact or 0.0),
            "total_alerts": int(aggregates.total_alerts or 0),
            "frames_analyzed": int(aggregates.frames_analyzed or 0)
        }
    finally:
        db.close()


@router.get("/summary", response_model=MetricsSummary)
def get_metrics_summary(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    user_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get aggregated metrics summary (cached for 1 minute).

    Returns:
        MetricsSummary: Aggregated statistics
    """
    # Convert datetimes to strings for caching
    start_str = start_time.isoformat() if start_time else None
    end_str = end_time.isoformat() if end_time else None

    # Get cached or compute
    result = _get_cached_metrics_summary(
        user_id=user_id,
        start_time=start_str,
        end_time=end_str,
        current_user_id=current_user.id,
        current_user_role=current_user.role.value
    )

    return MetricsSummary(**result)
