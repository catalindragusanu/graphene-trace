"""Shared helpers for tests"""
import numpy as np
from app.utils.pressure_matrix import encode_matrix


def blank_frame_bytes() -> bytes:
    """A valid, all-zero 32x32 frame payload"""
    return encode_matrix(np.zeros((32, 32), dtype=np.uint8))
