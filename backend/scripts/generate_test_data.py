"""Generate test data for test_profile user"""
import sys
import os
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.frame import Frame
from app.utils.pressure_matrix import encode_matrix

def generate_pressure_matrix(include_alert: bool = False) -> np.ndarray:
    """
    Generate a realistic 32x32 pressure matrix with Gaussian hotspots.
    Copied from generate_sample_data.py for standalone execution.
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

def generate_test_data():
    """Generate pressure frames for test profile."""
    db = SessionLocal()
    email = "test_profile@example.com"
    
    try:
        # Get user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"Error: User {email} not found. Please run create_test_user.py first.")
            return

        print(f"Generating data for {user.name} ({user.email})...")

        # Generate 50 frames (last 2 hours)
        num_frames = 50
        start_time = datetime.utcnow() - timedelta(hours=2)
        
        frames_added = 0
        
        for i in range(num_frames):
            timestamp = start_time + timedelta(minutes=i*2) # Every 2 minutes
            
            # Generate matrix
            include_alert = np.random.random() < 0.2 # 20% chance of alert
            matrix = generate_pressure_matrix(include_alert=include_alert)
            encoded_data = encode_matrix(matrix)
            
            frame = Frame(
                user_id=user.id,
                captured_at=timestamp,
                data=encoded_data
            )
            db.add(frame)
            frames_added += 1
            
        db.commit()
        print(f"✓ Successfully added {frames_added} frames for user {user.email}")
        
    except Exception as e:
        print(f"Error generating data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_test_data()
