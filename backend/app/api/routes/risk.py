"""Risk Analysis API Routes"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.risk_score import RiskScore
from app.services.authorization_service import AuthorizationService
from app.services.risk_analyzer import RiskAnalyzer
from pydantic import BaseModel

router = APIRouter()


class RiskScoreResponse(BaseModel):
    score: int
    level: str
    color: str
    factors: dict
    calculated_at: datetime

    class Config:
        from_attributes = True


@router.get("/current", response_model=RiskScoreResponse)
def get_current_risk(
    user_id: Optional[int] = Query(None, description="User ID (clinicians only)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current risk score for a user.
    Calculates on-the-fly based on recent data.
    """
    # Determine target user
    target_user_id = AuthorizationService.resolve_target_user_id(current_user, user_id, db)

    # Calculate risk score
    score, factors = RiskAnalyzer.calculate_risk_score(target_user_id, db, hours_to_analyze=2)
    level, color = RiskAnalyzer.get_risk_level(score)

    # Store in database for historical tracking
    risk_record = RiskScore(
        user_id=target_user_id,
        score=score,
        factors=factors
    )
    db.add(risk_record)
    db.commit()
    db.refresh(risk_record)

    return RiskScoreResponse(
        score=score,
        level=level,
        color=color,
        factors=factors,
        calculated_at=risk_record.calculated_at
    )


@router.post("/calculate", response_model=dict)
def calculate_and_store_risk(
    user_id: Optional[int] = Query(None, description="User ID (clinicians only)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate and store risk score.
    This endpoint can be called periodically by a scheduler.
    """
    # Determine target user
    target_user_id = AuthorizationService.resolve_target_user_id(current_user, user_id, db)

    # Calculate risk score
    score, factors = RiskAnalyzer.calculate_risk_score(target_user_id, db)
    level, color = RiskAnalyzer.get_risk_level(score)

    # Store in database
    risk_record = RiskScore(
        user_id=target_user_id,
        score=score,
        factors=factors
    )
    db.add(risk_record)
    db.commit()

    return {
        "message": "Risk score calculated and stored",
        "score": score,
        "level": level,
        "user_id": target_user_id
    }
