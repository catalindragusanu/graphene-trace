"""Utilities for encoding/decoding pressure matrices"""
import numpy as np
from typing import List


def encode_matrix(matrix: np.ndarray) -> bytes:
    """
    Convert 32x32 numpy array to bytes for BYTEA storage.

    Args:
        matrix: NumPy array of shape (32, 32) with dtype uint8

    Returns:
        bytes: Raw bytes representation (1024 bytes)

    Raises:
        ValueError: If matrix is not 32x32 or not uint8
    """
    if matrix.shape != (32, 32):
        raise ValueError(f"Matrix must be 32x32, got shape {matrix.shape}")

    if matrix.dtype != np.uint8:
        raise ValueError(f"Matrix must be uint8 dtype, got {matrix.dtype}")

    return matrix.tobytes()


def decode_matrix(data: bytes) -> np.ndarray:
    """
    Convert BYTEA bytes back to 32x32 numpy array.

    Args:
        data: Raw bytes from database (1024 bytes)

    Returns:
        np.ndarray: 32x32 matrix with dtype uint8

    Raises:
        ValueError: If data is not exactly 1024 bytes
    """
    if len(data) != 1024:
        raise ValueError(f"Data must be exactly 1024 bytes, got {len(data)}")

    return np.frombuffer(data, dtype=np.uint8).reshape(32, 32)


def matrix_to_list(matrix: np.ndarray) -> List[List[int]]:
    """
    Convert 32x32 numpy array to nested list for JSON serialization.

    Args:
        matrix: NumPy array of shape (32, 32)

    Returns:
        List[List[int]]: 32x32 nested list
    """
    return matrix.tolist()


def list_to_matrix(data: List[List[int]]) -> np.ndarray:
    """
    Convert nested list to 32x32 numpy array.

    Args:
        data: 32x32 nested list of integers

    Returns:
        np.ndarray: 32x32 matrix with dtype uint8

    Raises:
        ValueError: If data is not 32x32
    """
    matrix = np.array(data, dtype=np.uint8)

    if matrix.shape != (32, 32):
        raise ValueError(f"Data must represent a 32x32 matrix, got shape {matrix.shape}")

    return matrix


def flatten_matrix(matrix: np.ndarray) -> List[int]:
    """
    Flatten 32x32 matrix to 1D list (1024 elements) for CSV export.

    Args:
        matrix: NumPy array of shape (32, 32)

    Returns:
        List[int]: Flattened list of 1024 integers
    """
    if matrix.shape != (32, 32):
        raise ValueError(f"Matrix must be 32x32, got shape {matrix.shape}")

    return matrix.flatten().tolist()


def unflatten_matrix(data: List[int]) -> np.ndarray:
    """
    Convert flat list (1024 elements) to 32x32 matrix from CSV import.

    Args:
        data: List of 1024 integers

    Returns:
        np.ndarray: 32x32 matrix with dtype uint8

    Raises:
        ValueError: If data is not exactly 1024 elements
    """
    if len(data) != 1024:
        raise ValueError(f"Data must contain exactly 1024 elements, got {len(data)}")

    return np.array(data, dtype=np.uint8).reshape(32, 32)
