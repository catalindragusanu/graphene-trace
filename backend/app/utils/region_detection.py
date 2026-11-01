"""High-pressure region detection using connected component labeling"""
import numpy as np
from scipy import ndimage
from typing import Optional, Dict


def find_largest_region(binary_mask: np.ndarray) -> Optional[Dict]:
    """
    Find the largest connected component in a binary mask and return its bounding box.

    Uses connected component labeling (scipy.ndimage.label) to identify contiguous
    regions of high pressure, then returns the bounding box of the largest region.

    Args:
        binary_mask: 2D binary array (0 or 1) where 1 indicates high pressure

    Returns:
        Dict with bounding box coordinates and area, or None if no regions found:
        {
            "x1": int,  # Top-left x coordinate
            "y1": int,  # Top-left y coordinate
            "x2": int,  # Bottom-right x coordinate
            "y2": int,  # Bottom-right y coordinate
            "area": int  # Number of pixels in the region
        }
    """
    # Label connected components
    labeled, num_features = ndimage.label(binary_mask)

    if num_features == 0:
        return None

    # Find the largest component
    component_sizes = [(labeled == i).sum() for i in range(1, num_features + 1)]
    largest_label = np.argmax(component_sizes) + 1
    largest_region = (labeled == largest_label)

    # Compute bounding box
    rows, cols = np.where(largest_region)

    return {
        "x1": int(cols.min()),
        "y1": int(rows.min()),
        "x2": int(cols.max()),
        "y2": int(rows.max()),
        "area": int(component_sizes[largest_label - 1])
    }


def find_all_regions(binary_mask: np.ndarray, min_area: int = 4) -> list:
    """
    Find all connected components in a binary mask above a minimum area threshold.

    Args:
        binary_mask: 2D binary array (0 or 1) where 1 indicates high pressure
        min_area: Minimum number of pixels for a region to be included (default: 4)

    Returns:
        List of dicts, each containing:
        {
            "x1": int,
            "y1": int,
            "x2": int,
            "y2": int,
            "area": int
        }
        Sorted by area (largest first)
    """
    # Label connected components
    labeled, num_features = ndimage.label(binary_mask)

    if num_features == 0:
        return []

    regions = []

    # Process each component
    for i in range(1, num_features + 1):
        component = (labeled == i)
        area = component.sum()

        # Skip if below minimum area
        if area < min_area:
            continue

        # Compute bounding box
        rows, cols = np.where(component)

        regions.append({
            "x1": int(cols.min()),
            "y1": int(rows.min()),
            "x2": int(cols.max()),
            "y2": int(rows.max()),
            "area": int(area)
        })

    # Sort by area (largest first)
    regions.sort(key=lambda r: r["area"], reverse=True)

    return regions


def calculate_region_centroid(binary_mask: np.ndarray, region: Dict) -> Dict:
    """
    Calculate the centroid (center of mass) of a region.

    Args:
        binary_mask: 2D binary array (0 or 1)
        region: Region dict with x1, y1, x2, y2 coordinates

    Returns:
        Dict with centroid coordinates:
        {
            "cx": float,  # Center x coordinate
            "cy": float   # Center y coordinate
        }
    """
    # Extract region
    y1, y2 = region["y1"], region["y2"] + 1
    x1, x2 = region["x1"], region["x2"] + 1
    region_mask = binary_mask[y1:y2, x1:x2]

    # Calculate centroid
    rows, cols = np.where(region_mask)
    cy = float(rows.mean() + y1)
    cx = float(cols.mean() + x1)

    return {"cx": cx, "cy": cy}


def merge_overlapping_regions(regions: list, overlap_threshold: float = 0.3) -> list:
    """
    Merge overlapping bounding boxes.

    Args:
        regions: List of region dicts with x1, y1, x2, y2
        overlap_threshold: IoU threshold for merging (default: 0.3)

    Returns:
        List of merged regions
    """
    if not regions:
        return []

    def calculate_iou(region1, region2):
        """Calculate Intersection over Union for two bounding boxes."""
        x1_inter = max(region1["x1"], region2["x1"])
        y1_inter = max(region1["y1"], region2["y1"])
        x2_inter = min(region1["x2"], region2["x2"])
        y2_inter = min(region1["y2"], region2["y2"])

        if x2_inter < x1_inter or y2_inter < y1_inter:
            return 0.0

        intersection = (x2_inter - x1_inter + 1) * (y2_inter - y1_inter + 1)

        area1 = (region1["x2"] - region1["x1"] + 1) * (region1["y2"] - region1["y1"] + 1)
        area2 = (region2["x2"] - region2["x1"] + 1) * (region2["y2"] - region2["y1"] + 1)

        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0.0

    merged = []
    used = set()

    for i, region1 in enumerate(regions):
        if i in used:
            continue

        # Start with current region
        current = region1.copy()

        # Check for overlaps with remaining regions
        for j in range(i + 1, len(regions)):
            if j in used:
                continue

            if calculate_iou(current, regions[j]) >= overlap_threshold:
                # Merge bounding boxes
                current = {
                    "x1": min(current["x1"], regions[j]["x1"]),
                    "y1": min(current["y1"], regions[j]["y1"]),
                    "x2": max(current["x2"], regions[j]["x2"]),
                    "y2": max(current["y2"], regions[j]["y2"]),
                    "area": current["area"] + regions[j]["area"]
                }
                used.add(j)

        merged.append(current)

    return merged
