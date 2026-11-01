"""Ulcer Risk Prediction Service

Calculates dynamic risk scores based on pressure history and movement patterns.
Uses feature engineering approach (not deep learning initially).
"""
import numpy as np
import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.frame import Frame
from app.models.movement_event import MovementEvent
from app.utils.pressure_matrix import decode_matrix

logger = logging.getLogger(__name__)


class RiskAnalyzer:
    """Analyzes ulcer risk based on pressure patterns"""

    # Risk thresholds
    CRITICAL_PRESSURE = 200
    HIGH_PRESSURE = 150
    MAX_SAFE_TIME_WITHOUT_REPOSITION = 120  # minutes

    @staticmethod
    def calculate_risk_score(
        user_id: int,
        db: Session,
        hours_to_analyze: int = 2
    ) -> Tuple[int, Dict]:
        """
        Calculate ulcer risk score (0-100) for a user.

        Args:
            user_id: User ID to analyze
            db: Database session
            hours_to_analyze: Hours of history to consider

        Returns:
            Tuple of (risk_score, factors_breakdown)
        """
        since = datetime.now(timezone.utc) - timedelta(hours=hours_to_analyze)

        # Get recent frames
        frames = db.query(Frame).filter(
            Frame.user_id == user_id,
            Frame.captured_at >= since
        ).order_by(Frame.captured_at.desc()).all()

        if not frames:
            return 0, {"error": "No recent data"}

        # Calculate factors
        max_pressure_factor = RiskAnalyzer._calculate_max_pressure_factor(frames, db)
        avg_pressure_factor = RiskAnalyzer._calculate_avg_pressure_factor(frames, db)
        reposition_factor = RiskAnalyzer._calculate_reposition_factor(user_id, db, since)
        variance_factor = RiskAnalyzer._calculate_variance_factor(frames, db)

        # Weighted combination
        risk_score = (
            0.35 * max_pressure_factor +
            0.25 * avg_pressure_factor +
            0.30 * reposition_factor +
            0.10 * variance_factor
        )

        # Clamp to 0-100
        risk_score = max(0, min(100, int(risk_score)))

        factors = {
            "max_pressure_factor": round(max_pressure_factor, 1),
            "avg_pressure_factor": round(avg_pressure_factor, 1),
            "reposition_factor": round(reposition_factor, 1),
            "variance_factor": round(variance_factor, 1),
            "frames_analyzed": len(frames)
        }

        return risk_score, factors

    @staticmethod
    def _calculate_max_pressure_factor(frames: List[Frame], db: Session) -> float:
        """Calculate risk factor from maximum pressure (0-100)"""
        max_pressures = []

        for frame in frames[:10]:  # Check last 10 frames
            try:
                matrix = decode_matrix(frame.data)
                max_pressures.append(np.max(matrix))
            except ValueError as e:
                logger.error(f"Invalid frame data for frame_id={frame.id}: {e}")
                continue
            except Exception:
                logger.exception(f"Unexpected error processing frame_id={frame.id}")
                continue

        if not max_pressures:
            return 0.0

        avg_max = np.mean(max_pressures)

        # Normalize to 0-100
        if avg_max >= RiskAnalyzer.CRITICAL_PRESSURE:
            return 100.0
        elif avg_max >= RiskAnalyzer.HIGH_PRESSURE:
            # Linear scale from 150-200 -> 50-100
            return 50 + ((avg_max - RiskAnalyzer.HIGH_PRESSURE) /
                         (RiskAnalyzer.CRITICAL_PRESSURE - RiskAnalyzer.HIGH_PRESSURE)) * 50
        else:
            # Linear scale from 0-150 -> 0-50
            return (avg_max / RiskAnalyzer.HIGH_PRESSURE) * 50

    @staticmethod
    def _calculate_avg_pressure_factor(frames: List[Frame], db: Session) -> float:
        """Calculate risk factor from average pressure (0-100)"""
        avg_pressures = []

        for frame in frames[:10]:
            try:
                matrix = decode_matrix(frame.data)
                avg_pressures.append(np.mean(matrix))
            except ValueError as e:
                logger.error(f"Invalid frame data for frame_id={frame.id}: {e}")
                continue
            except Exception:
                logger.exception(f"Unexpected error processing frame_id={frame.id}")
                continue

        if not avg_pressures:
            return 0.0

        overall_avg = np.mean(avg_pressures)

        # Normalize to 0-100 (assuming avg rarely exceeds 100)
        return min(100, overall_avg)

    @staticmethod
    def _calculate_reposition_factor(user_id: int, db: Session, since: datetime) -> float:
        """Calculate risk factor from repositioning frequency (0-100)"""
        # Get macro movements (effective repositioning)
        macro_movements = db.query(MovementEvent).filter(
            MovementEvent.user_id == user_id,
            MovementEvent.movement_type == 'macro',
            MovementEvent.detected_at >= since
        ).order_by(MovementEvent.detected_at.desc()).all()

        if not macro_movements:
            # No repositioning in the time window = high risk
            return 100.0

        # Calculate time since last macro movement
        last_macro = macro_movements[0].detected_at
        minutes_since = (datetime.now(timezone.utc) - last_macro).total_seconds() / 60

        # Risk increases linearly after 60 minutes
        if minutes_since >= RiskAnalyzer.MAX_SAFE_TIME_WITHOUT_REPOSITION:
            return 100.0
        elif minutes_since >= 60:
            # Linear scale from 60-120 min -> 50-100 risk
            return 50 + ((minutes_since - 60) / 60) * 50
        else:
            # Linear scale from 0-60 min -> 0-50 risk
            return (minutes_since / 60) * 50

    @staticmethod
    def _calculate_variance_factor(frames: List[Frame], db: Session) -> float:
        """Calculate risk factor from pressure variance (0-100)"""
        # Low variance = pressure concentrated in same spot = higher risk
        variances = []

        for frame in frames[:10]:
            try:
                matrix = decode_matrix(frame.data)
                variances.append(np.var(matrix))
            except ValueError as e:
                logger.error(f"Invalid frame data for frame_id={frame.id}: {e}")
                continue
            except Exception:
                logger.exception(f"Unexpected error processing frame_id={frame.id}")
                continue

        if not variances:
            return 50.0  # Default medium risk

        avg_variance = np.mean(variances)

        # High variance (>1000) = good (pressure distributed) = low risk
        # Low variance (<100) = bad (pressure concentrated) = high risk
        if avg_variance >= 1000:
            return 0.0
        elif avg_variance <= 100:
            return 100.0
        else:
            # Inverse linear scale: 100-1000 variance -> 100-0 risk
            return 100 - ((avg_variance - 100) / 900) * 100

    @staticmethod
    def get_risk_level(score: int) -> Tuple[str, str]:
        """
        Get risk level label and color from score.

        Returns:
            Tuple of (label, color_hex)
        """
        if score >= 75:
            return "CRITICAL", "#ef4444"
        elif score >= 50:
            return "HIGH", "#f59e0b"
        elif score >= 25:
            return "MODERATE", "#eab308"
        else:
            return "LOW", "#10b981"
