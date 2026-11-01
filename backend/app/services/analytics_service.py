"""Analytics service for calculating pressure metrics"""
import numpy as np
from typing import Dict, Optional
from app.utils.region_detection import find_largest_region, find_all_regions


class AnalyticsService:
    """Service for calculating pressure-related metrics"""

    def __init__(self):
        self.contact_threshold = 10  # Pixels below this are not considered "contact"
        self.high_pressure_threshold = 200  # Threshold for high-pressure alerts
        self.alert_threshold_severe = 230  # Threshold for severe alerts

    def calculate_peak_pressure(self, matrix: np.ndarray) -> float:
        """
        Calculate Peak Pressure Index (PPI).

        PPI is the maximum pressure value, excluding pixels with pressure < threshold.

        Args:
            matrix: 32x32 numpy array of pressure values (uint8)

        Returns:
            float: Peak pressure value (0 if no valid pixels)
        """
        valid_pixels = matrix[matrix >= self.contact_threshold]

        if len(valid_pixels) == 0:
            return 0.0

        return float(np.max(valid_pixels))

    def calculate_contact_area(self, matrix: np.ndarray) -> float:
        """
        Calculate Contact Area Percentage.

        Contact Area % = (number of pixels > threshold) / total pixels × 100

        Args:
            matrix: 32x32 numpy array of pressure values (uint8)

        Returns:
            float: Contact area as percentage (0-100)
        """
        total_pixels = 1024  # 32 × 32
        contact_pixels = np.sum(matrix > self.contact_threshold)

        return (float(contact_pixels) / total_pixels) * 100

    def detect_high_pressure_region(
        self,
        matrix: np.ndarray,
        threshold: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Detect high-pressure regions using connected component labeling.

        Finds the largest contiguous region where pressure exceeds the threshold.

        Args:
            matrix: 32x32 numpy array of pressure values (uint8)
            threshold: Pressure threshold (default: 200)

        Returns:
            Dict with bounding box and area, or None if no region found:
            {
                "x1": int,
                "y1": int,
                "x2": int,
                "y2": int,
                "area": int
            }
        """
        if threshold is None:
            threshold = self.high_pressure_threshold

        # Create binary mask
        binary_mask = (matrix > threshold).astype(np.uint8)

        # Find largest region
        region = find_largest_region(binary_mask)

        return region

    def detect_all_high_pressure_regions(
        self,
        matrix: np.ndarray,
        threshold: Optional[int] = None,
        min_area: int = 4
    ) -> list:
        """
        Detect all high-pressure regions above a minimum area.

        Args:
            matrix: 32x32 numpy array of pressure values (uint8)
            threshold: Pressure threshold (default: 200)
            min_area: Minimum pixels for a region to be reported (default: 4)

        Returns:
            List of region dicts, sorted by area (largest first)
        """
        if threshold is None:
            threshold = self.high_pressure_threshold

        # Create binary mask
        binary_mask = (matrix > threshold).astype(np.uint8)

        # Find all regions
        regions = find_all_regions(binary_mask, min_area=min_area)

        return regions

    def calculate_mean_pressure(self, matrix: np.ndarray) -> float:
        """
        Calculate mean pressure across all contact pixels.

        Args:
            matrix: 32x32 numpy array of pressure values (uint8)

        Returns:
            float: Mean pressure (0 if no contact pixels)
        """
        contact_pixels = matrix[matrix > self.contact_threshold]

        if len(contact_pixels) == 0:
            return 0.0

        return float(np.mean(contact_pixels))

    def calculate_pressure_distribution(self, matrix: np.ndarray) -> Dict:
        """
        Calculate pressure distribution statistics.

        Args:
            matrix: 32x32 numpy array of pressure values (uint8)

        Returns:
            Dict with distribution statistics:
            {
                "mean": float,
                "std": float,
                "median": float,
                "q25": float,  # 25th percentile
                "q75": float   # 75th percentile
            }
        """
        contact_pixels = matrix[matrix > self.contact_threshold]

        if len(contact_pixels) == 0:
            return {
                "mean": 0.0,
                "std": 0.0,
                "median": 0.0,
                "q25": 0.0,
                "q75": 0.0
            }

        return {
            "mean": float(np.mean(contact_pixels)),
            "std": float(np.std(contact_pixels)),
            "median": float(np.median(contact_pixels)),
            "q25": float(np.percentile(contact_pixels, 25)),
            "q75": float(np.percentile(contact_pixels, 75))
        }

    def determine_alert_severity(self, peak_pressure: float, region_area: int) -> str:
        """
        Determine alert severity based on pressure and area.

        Args:
            peak_pressure: Maximum pressure in the region
            region_area: Number of pixels in the region

        Returns:
            str: "low", "medium", or "high"
        """
        if peak_pressure >= self.alert_threshold_severe or region_area >= 50:
            return "high"
        elif peak_pressure >= self.high_pressure_threshold or region_area >= 20:
            return "medium"
        else:
            return "low"

    def process_frame(self, matrix: np.ndarray) -> Dict:
        """
        Process a complete frame and return all metrics.

        This is the main method that combines all analytics algorithms.

        Args:
            matrix: 32x32 numpy array of pressure values (uint8)

        Returns:
            Dict with all metrics:
            {
                "peak_pressure": float,
                "contact_area_percent": float,
                "high_pressure_region": dict or None,
                "alert_generated": bool,
                "alert_severity": str or None,
                "mean_pressure": float,
                "distribution": dict
            }
        """
        # Calculate basic metrics
        peak_pressure = self.calculate_peak_pressure(matrix)
        contact_area = self.calculate_contact_area(matrix)
        mean_pressure = self.calculate_mean_pressure(matrix)

        # Detect high-pressure region
        high_pressure_region = self.detect_high_pressure_region(matrix)

        # Determine if alert should be generated
        alert_generated = high_pressure_region is not None
        alert_severity = None

        if alert_generated:
            alert_severity = self.determine_alert_severity(
                peak_pressure,
                high_pressure_region["area"]
            )

        # Calculate distribution statistics
        distribution = self.calculate_pressure_distribution(matrix)

        return {
            "peak_pressure": peak_pressure,
            "contact_area_percent": contact_area,
            "high_pressure_region": high_pressure_region,
            "alert_generated": alert_generated,
            "alert_severity": alert_severity,
            "mean_pressure": mean_pressure,
            "distribution": distribution
        }

    def analyze_matrix_quality(self, matrix: np.ndarray) -> Dict:
        """
        Analyze data quality of a pressure matrix.

        Args:
            matrix: 32x32 numpy array of pressure values (uint8)

        Returns:
            Dict with quality metrics:
            {
                "valid": bool,
                "has_contact": bool,
                "contact_pixels": int,
                "saturated_pixels": int,  # Pixels at max value (255)
                "zero_pixels": int
            }
        """
        total_pixels = 1024
        contact_pixels = int(np.sum(matrix > self.contact_threshold))
        saturated_pixels = int(np.sum(matrix == 255))
        zero_pixels = int(np.sum(matrix == 0))

        # Matrix is valid if it has some contact and isn't completely saturated
        valid = contact_pixels > 0 and saturated_pixels < total_pixels * 0.5

        return {
            "valid": valid,
            "has_contact": contact_pixels > 0,
            "contact_pixels": contact_pixels,
            "saturated_pixels": saturated_pixels,
            "zero_pixels": zero_pixels
        }
