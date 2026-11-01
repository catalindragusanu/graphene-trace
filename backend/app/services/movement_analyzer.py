"""Movement Quality Analyzer Service

Analyzes consecutive pressure frames to detect and classify patient movements.
Distinguishes between:
- Micro-movements: Small shifts (fidgeting, minor adjustments)
- Macro-movements: Significant repositioning (effective pressure relief)
"""
import numpy as np
from typing import Tuple, Dict


class MovementAnalyzer:
    """Analyzes movement quality from pressure matrix data"""

    # Thresholds
    MICRO_THRESHOLD = 30  # Max pressure shift for micro-movement
    MACRO_THRESHOLD = 50  # Min pressure shift for macro-movement
    MICRO_AREA_THRESHOLD = 0.2  # Max affected area for micro
    MACRO_AREA_THRESHOLD = 0.4  # Min affected area for macro
    CHANGE_THRESHOLD = 10  # Min change to count as affected

    @staticmethod
    def analyze_movement(
        frame_t0: np.ndarray,
        frame_t1: np.ndarray
    ) -> Tuple[str, float, Dict]:
        """
        Analyze movement between two consecutive frames.

        Args:
            frame_t0: Previous frame (32x32 numpy array)
            frame_t1: Current frame (32x32 numpy array)

        Returns:
            Tuple of (movement_type, quality_score, metrics)
            - movement_type: 'macro', 'micro', or 'none'
            - quality_score: 0.0-1.0 (effectiveness of movement)
            - metrics: Dict with detailed analysis
        """
        # Calculate difference matrix
        diff = np.abs(frame_t1.astype(float) - frame_t0.astype(float))

        # Calculate metrics
        max_shift = np.max(diff)
        mean_shift = np.mean(diff)
        total_cells = frame_t0.size
        affected_cells = np.sum(diff > MovementAnalyzer.CHANGE_THRESHOLD)
        affected_area = affected_cells / total_cells

        # Calculate center of pressure shift
        cop_t0 = MovementAnalyzer._calculate_center_of_pressure(frame_t0)
        cop_t1 = MovementAnalyzer._calculate_center_of_pressure(frame_t1)
        cop_shift = np.linalg.norm(cop_t1 - cop_t0)

        metrics = {
            'max_shift': float(max_shift),
            'mean_shift': float(mean_shift),
            'affected_area': float(affected_area),
            'cop_shift': float(cop_shift),
            'affected_cells': int(affected_cells)
        }

        # Classify movement
        if max_shift > MovementAnalyzer.MACRO_THRESHOLD and affected_area > MovementAnalyzer.MACRO_AREA_THRESHOLD:
            # Macro-movement (effective repositioning)
            quality_score = MovementAnalyzer._calculate_quality_score(
                max_shift, affected_area, cop_shift, is_macro=True
            )
            return 'macro', quality_score, metrics

        elif max_shift > MovementAnalyzer.MICRO_THRESHOLD or affected_area > MovementAnalyzer.MICRO_AREA_THRESHOLD:
            # Micro-movement (fidgeting)
            quality_score = MovementAnalyzer._calculate_quality_score(
                max_shift, affected_area, cop_shift, is_macro=False
            )
            return 'micro', quality_score, metrics

        else:
            # No significant movement
            return 'none', 0.0, metrics

    @staticmethod
    def _calculate_center_of_pressure(frame: np.ndarray) -> np.ndarray:
        """Calculate center of pressure (weighted centroid)"""
        total_pressure = np.sum(frame)
        if total_pressure == 0:
            return np.array([16.0, 16.0])  # Center of 32x32 grid

        y_indices, x_indices = np.indices(frame.shape)
        cop_x = np.sum(x_indices * frame) / total_pressure
        cop_y = np.sum(y_indices * frame) / total_pressure

        return np.array([cop_x, cop_y])

    @staticmethod
    def _calculate_quality_score(
        max_shift: float,
        affected_area: float,
        cop_shift: float,
        is_macro: bool
    ) -> float:
        """
        Calculate movement quality score (0.0-1.0).
        Higher score = more effective pressure relief.
        """
        if is_macro:
            # For macro-movements, reward large shifts and area changes
            shift_score = min(max_shift / 150, 1.0)  # Normalize to 150
            area_score = min(affected_area / 0.8, 1.0)  # Normalize to 80%
            cop_score = min(cop_shift / 20, 1.0)  # Normalize to 20 units

            # Weighted average
            quality = 0.4 * shift_score + 0.3 * area_score + 0.3 * cop_score
            return min(max(quality, 0.5), 1.0)  # Macro movements are at least 0.5

        else:
            # For micro-movements, score is lower (not effective repositioning)
            return min(max_shift / 100, 0.4)  # Max 0.4 for micro-movements
