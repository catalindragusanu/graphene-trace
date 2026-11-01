"""Generate realistic sample pressure data for testing"""
import numpy as np
import csv
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def generate_pressure_matrix(include_alert: bool = False) -> np.ndarray:
    """
    Generate a realistic 32x32 pressure matrix with Gaussian hotspots.

    Args:
        include_alert: If True, occasionally generate high-pressure regions (>200)

    Returns:
        np.ndarray: 32x32 matrix with dtype uint8 (values 0-255)
    """
    # Start with base noise (low background pressure)
    matrix = np.random.randint(0, 30, (32, 32), dtype=np.uint8)

    # Add 2-4 Gaussian pressure hotspots
    num_hotspots = np.random.randint(2, 5)

    for i in range(num_hotspots):
        # Random center position (avoid edges)
        center_x = np.random.randint(5, 27)
        center_y = np.random.randint(5, 27)

        # Random intensity (higher if we want alerts)
        if include_alert and i == 0 and np.random.random() < 0.3:
            # 30% chance of high-pressure alert region
            intensity = np.random.randint(200, 250)
        else:
            # Normal pressure hotspot
            intensity = np.random.randint(80, 180)

        # Random spread (how wide the hotspot is)
        spread = np.random.uniform(40, 80)

        # Create meshgrid for Gaussian calculation
        xx, yy = np.meshgrid(np.arange(32), np.arange(32))

        # Calculate Gaussian blob
        gaussian = intensity * np.exp(
            -((xx - center_x)**2 + (yy - center_y)**2) / spread
        )

        # Add to matrix, clipping to valid range
        matrix = np.clip(matrix + gaussian.astype(np.uint8), 0, 255)

    return matrix


def generate_sample_data(num_users: int = 5, num_days: int = 3, output_dir: str = "../database/sample_data"):
    """
    Generate sample pressure data for multiple users over multiple days.

    Args:
        num_users: Number of users to generate data for
        num_days: Number of days of data to generate
        output_dir: Directory to save CSV files
    """
    # Create output directory if it doesn't exist
    output_path = Path(__file__).parent / output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    # Calculate total frames: 288 frames per day (one every 5 minutes)
    frames_per_day = 288
    total_frames = num_users * num_days * frames_per_day

    print(f"Generating sample pressure data...")
    print(f"  Users: {num_users}")
    print(f"  Days: {num_days}")
    print(f"  Frames per day: {frames_per_day}")
    print(f"  Total frames: {total_frames:,}")
    print(f"  Output directory: {output_path.absolute()}")
    print()

    # Generate data for each user
    for user_id in range(1, num_users + 1):
        filename = output_path / f"pressure_data_user{user_id}.csv"

        print(f"Generating data for User {user_id}... ", end="", flush=True)

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write header
            header = ['timestamp', 'user_id'] + [f'p_{i}_{j}' for i in range(32) for j in range(32)]
            writer.writerow(header)

            # Start time: 3 days ago
            start_time = datetime.now() - timedelta(days=num_days)

            frame_count = 0

            # Generate data for each day
            for day in range(num_days):
                # Generate data for each 5-minute interval
                for hour in range(24):
                    for minute in range(0, 60, 5):
                        # Calculate timestamp
                        timestamp = start_time + timedelta(days=day, hours=hour, minutes=minute)

                        # Generate pressure matrix
                        # Occasionally include high-pressure regions for alerts
                        include_alert = np.random.random() < 0.15  # 15% chance
                        matrix = generate_pressure_matrix(include_alert=include_alert)

                        # Flatten matrix to 1D list
                        flat_data = matrix.flatten().tolist()

                        # Write row: timestamp, user_id, followed by 1024 pressure values
                        row = [timestamp.isoformat(), user_id] + flat_data
                        writer.writerow(row)

                        frame_count += 1

        print(f"✓ {frame_count} frames written to {filename.name}")

    print()
    print(f"Sample data generation complete!")
    print(f"Total files created: {num_users}")
    print(f"Total data points: {total_frames * 1024:,}")


if __name__ == "__main__":
    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="Generate sample pressure data")
    parser.add_argument("--users", type=int, default=5, help="Number of users (default: 5)")
    parser.add_argument("--days", type=int, default=3, help="Number of days (default: 3)")
    parser.add_argument("--output", type=str, default="../database/sample_data", help="Output directory")

    args = parser.parse_args()

    generate_sample_data(
        num_users=args.users,
        num_days=args.days,
        output_dir=args.output
    )
