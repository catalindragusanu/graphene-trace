from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import numpy as np
import logging

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.frame import Frame
from app.schemas.patient import PatientSummary
from app.services.authorization_service import AuthorizationService
from app.utils.pressure_matrix import decode_matrix

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/patients", response_model=List[PatientSummary])
def get_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the clinician's patients (members of their groups) with real-time status.
    Only accessible by clinicians.
    """
    if current_user.role != UserRole.clinician:
        raise HTTPException(status_code=403, detail="Only clinicians can access this endpoint")

    # Subquery to get latest frame ID for each patient (optimized - single query)
    latest_frame_subq = (
        db.query(
            Frame.user_id,
            func.max(Frame.id).label('latest_frame_id')
        )
        .group_by(Frame.user_id)
        .subquery()
    )

    # Get all patients with their latest frame in single query
    patients_with_frames = db.query(
        User,
        Frame
    ).outerjoin(
        latest_frame_subq,
        User.id == latest_frame_subq.c.user_id
    ).outerjoin(
        Frame,
        Frame.id == latest_frame_subq.c.latest_frame_id
    ).filter(
        User.role == UserRole.patient,
        User.id.in_(AuthorizationService.get_accessible_patients(current_user, db))
    ).all()

    result = []

    for patient, last_frame in patients_with_frames:
        risk_level = "Unknown"
        avg_pressure = 0
        max_pressure = 0
        last_updated = None

        if last_frame:
            last_updated = last_frame.captured_at
            try:
                # Calculate stats
                matrix = decode_matrix(last_frame.data)
                avg_pressure = int(np.mean(matrix))
                max_pressure = int(np.max(matrix))

                if max_pressure > 200:
                    risk_level = "Critical"
                elif max_pressure > 150:
                    risk_level = "High"
                else:
                    risk_level = "Safe"
            except ValueError as e:
                logger.error(f"Invalid frame data for frame_id={last_frame.id}, user_id={patient.id}: {e}")
            except Exception:
                logger.exception(f"Unexpected error processing frame for user_id={patient.id}")

        result.append(PatientSummary(
            id=patient.id,
            name=patient.name,
            email=patient.email,
            photo_url=patient.photo_url,
            medical_condition=patient.medical_condition,
            last_updated=last_updated,
            risk_level=risk_level,
            avg_pressure=avg_pressure,
            max_pressure=max_pressure
        ))

    return result
