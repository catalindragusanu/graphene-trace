"""ETL script to import CSV pressure data into PostgreSQL database"""
import csv
import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
# Import all models to ensure relationships are properly initialized
from app.models import User, Frame, Metric, Alert, Comment, UserGroup, MovementEvent, RiskScore, PostureLabel
from app.utils.pressure_matrix import encode_matrix


def import_csv_file(filepath: Path, db_session):
    """
    Import a single CSV file into the database.

    Args:
        filepath: Path to CSV file
        db_session: SQLAlchemy database session
    """
    print(f"Importing {filepath.name}... ", end="", flush=True)

    # Read CSV file
    df = pd.read_csv(filepath)

    frames_imported = 0
    frames_skipped = 0

    # Process each row
    for _, row in df.iterrows():
        try:
            # Extract metadata
            timestamp = pd.to_datetime(row['timestamp'])
            user_id = int(row['user_id'])

            # Extract pressure values (columns 2 onwards, should be 1024 values)
            pressure_values = row.iloc[2:].values

            if len(pressure_values) != 1024:
                print(f"Warning: Expected 1024 values, got {len(pressure_values)}. Skipping.")
                frames_skipped += 1
                continue

            # Convert to 32x32 matrix
            matrix = pressure_values.reshape(32, 32).astype(np.uint8)

            # Encode matrix to bytes
            encoded_data = encode_matrix(matrix)

            # Create Frame object
            frame = Frame(
                user_id=user_id,
                captured_at=timestamp,
                data=encoded_data
            )

            db_session.add(frame)
            frames_imported += 1

            # Commit in batches of 100 for performance
            if frames_imported % 100 == 0:
                db_session.commit()

        except Exception as e:
            print(f"\nError processing row: {e}")
            frames_skipped += 1
            continue

    # Final commit
    db_session.commit()

    print(f"✓ {frames_imported} frames imported, {frames_skipped} skipped")
    return frames_imported, frames_skipped


def import_all_csv_files(data_dir: str = "../database/sample_data"):
    """
    Import all CSV files from the data directory.

    Args:
        data_dir: Directory containing CSV files
    """
    data_path = Path(__file__).parent / data_dir

    if not data_path.exists():
        print(f"Error: Data directory not found: {data_path.absolute()}")
        print("Please run generate_sample_data.py first to create sample data.")
        return

    # Find all CSV files
    csv_files = list(data_path.glob("*.csv"))

    if not csv_files:
        print(f"Error: No CSV files found in {data_path.absolute()}")
        return

    print(f"Found {len(csv_files)} CSV files to import")
    print(f"Data directory: {data_path.absolute()}")
    print()

    # Create database session
    db = SessionLocal()

    total_imported = 0
    total_skipped = 0

    try:
        # Import each CSV file
        for csv_file in sorted(csv_files):
            imported, skipped = import_csv_file(csv_file, db)
            total_imported += imported
            total_skipped += skipped

    except Exception as e:
        print(f"\nError during import: {e}")
        db.rollback()
        raise

    finally:
        db.close()

    print()
    print(f"Import complete!")
    print(f"  Total frames imported: {total_imported:,}")
    print(f"  Total frames skipped: {total_skipped:,}")
    print(f"  Files processed: {len(csv_files)}")


def verify_import():
    """Verify the import by checking database counts."""
    db = SessionLocal()

    try:
        from sqlalchemy import func
        from app.models.user import User

        # Count total frames
        frame_count = db.query(func.count(Frame.id)).scalar()
        print(f"\nVerification:")
        print(f"  Total frames in database: {frame_count:,}")

        # Count frames per user
        user_frame_counts = db.query(
            Frame.user_id,
            func.count(Frame.id).label('count')
        ).group_by(Frame.user_id).all()

        print(f"  Frames per user:")
        for user_id, count in user_frame_counts:
            print(f"    User {user_id}: {count:,} frames")

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import CSV pressure data into database")
    parser.add_argument("--data-dir", type=str, default="../database/sample_data",
                        help="Directory containing CSV files")
    parser.add_argument("--verify", action="store_true", help="Verify import after completion")

    args = parser.parse_args()

    print("=" * 60)
    print("CSV Data Import Tool")
    print("=" * 60)
    print()

    import_all_csv_files(data_dir=args.data_dir)

    if args.verify:
        verify_import()
