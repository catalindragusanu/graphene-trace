"""
Create 3 additional test patients with realistic profiles and pressure data.

Creates:
- Patient 2: Emma Wilson (elderly, high risk)
- Patient 3: James Chen (post-surgery)
- Patient 4: Sarah Martinez (spinal injury)

Each patient gets:
- User profile with medical details
- 100 frames of pressure data (last 2 hours)
- Varied pressure patterns based on condition
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta
import numpy as np
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.frame import Frame
from app.services.auth_service import AuthService
from app.utils.pressure_matrix import encode_matrix

def create_patient_with_data(
    email: str,
    password: str,
    name: str,
    date_of_birth: str,
    medical_condition: str,
    photo_url: str,
    risk_profile: str  # 'low', 'medium', 'high'
):
    """Create a patient user and generate pressure data"""
    print(f"\nAttempting to create patient: {name}")
    print(f"  Email: {email}")
    
    db = SessionLocal()
    
    try:
        print("  -> Database connection established")
        
        # Check if user already exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"  [X] User {email} already exists (ID: {existing.id})")
            return existing.id
        
        print("  -> Creating user record...")
        # Create user
        user = User(
            email=email,
            password_hash=AuthService.hash_password(password),
            role=UserRole.patient,
            name=name,
            date_of_birth=datetime.strptime(date_of_birth, "%Y-%m-%d").date(),
            medical_condition=medical_condition,
            photo_url=photo_url
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"  [OK] Created patient: {name} (ID: {user.id})")
        
        # Generate 100 frames over last 2 hours
        print("  -> Generating pressure frames...")
        now = datetime.utcnow()
        frames_created = 0
        
        for i in range(100):
            # Time spacing: ~1.2 minutes apart
            captured_at = now - timedelta(minutes=120 - (i * 1.2))
            
            # Generate pressure matrix based on risk profile
            matrix = generate_pressure_matrix(risk_profile, i)
            
            # Create frame
            frame = Frame(
                user_id=user.id,
                captured_at=captured_at,
                data=encode_matrix(matrix)
            )
            db.add(frame)
            frames_created += 1
        
        db.commit()
        print(f"  -> Generated {frames_created} pressure frames")
        
        return user.id
        
    except Exception as e:
        db.rollback()
        print(f"[X] Error creating patient {name}: {e}")
        raise
    finally:
        db.close()


def generate_pressure_matrix(risk_profile: str, frame_index: int) -> np.ndarray:
    """
    Generate a 32x32 pressure matrix with realistic patterns.
    
    Args:
        risk_profile: 'low', 'medium', or 'high'
        frame_index: Frame number (0-99) for temporal variation
    """
    matrix = np.zeros((32, 32), dtype=np.uint8)
    
    # Base pressure patterns
    if risk_profile == 'low':
        # Well-distributed pressure, frequent repositioning
        # Simulate good movement every ~20 frames
        position_offset = (frame_index // 20) * 5
        create_pressure_hotspot(matrix, 16 + position_offset % 10, 16, intensity=120, spread=8)
        
    elif risk_profile == 'medium':
        # Moderate pressure, some repositioning
        # Simulate movement every ~30 frames
        position_offset = (frame_index // 30) * 8
        create_pressure_hotspot(matrix, 16, 16 + position_offset % 12, intensity=160, spread=6)
        create_pressure_hotspot(matrix, 20, 20, intensity=140, spread=5)
        
    else:  # high risk
        # High concentrated pressure, minimal movement
        # Very infrequent repositioning (every ~50 frames)
        position_offset = (frame_index // 50) * 3
        create_pressure_hotspot(matrix, 16 + position_offset, 16, intensity=220, spread=4)
        create_pressure_hotspot(matrix, 18, 18, intensity=200, spread=4)
    
    # Add some random noise
    noise = np.random.randint(0, 30, (32, 32), dtype=np.uint8)
    matrix = np.clip(matrix.astype(int) + noise, 0, 255).astype(np.uint8)
    
    return matrix


def create_pressure_hotspot(matrix: np.ndarray, center_x: int, center_y: int, intensity: int, spread: int):
    """Create a Gaussian-like pressure hotspot"""
    for i in range(32):
        for j in range(32):
            distance = np.sqrt((i - center_x)**2 + (j - center_y)**2)
            if distance < spread:
                value = int(intensity * np.exp(-(distance**2) / (2 * (spread/2)**2)))
                matrix[i, j] = max(matrix[i, j], value)


def main():
    print("="*60)
    print("Creating 3 additional test patients...")
    print("="*60)
    
    try:
        # Patient 2: Emma Wilson (elderly, high risk)
        print("\n[1/3] Creating Emma Wilson...")
        patient2_id = create_patient_with_data(
            email="emma.wilson@example.com",
            password="password123",
            name="Emma Wilson",
            date_of_birth="1945-03-15",
            medical_condition="Elderly patient with limited mobility. History of diabetes and peripheral neuropathy. High risk for pressure ulcers.",
            photo_url="https://i.pravatar.cc/150?img=47",
            risk_profile="high"
        )
        
        # Patient 3: James Chen (post-surgery, medium risk)
        print("\n[2/3] Creating James Chen...")
        patient3_id = create_patient_with_data(
            email="james.chen@example.com",
            password="password123",
            name="James Chen",
            date_of_birth="1978-11-22",
            medical_condition="Post-operative hip replacement. Recovering from surgery, limited mobility for 6 weeks. Moderate risk.",
            photo_url="https://i.pravatar.cc/150?img=12",
            risk_profile="medium"
        )
        
        # Patient 4: Sarah Martinez (spinal injury, low risk - good care)
        print("\n[3/3] Creating Sarah Martinez...")
        patient4_id = create_patient_with_data(
            email="sarah.martinez@example.com",
            password="password123",
            name="Sarah Martinez",
            date_of_birth="1992-07-08",
            medical_condition="T6 spinal cord injury. Paraplegic. Excellent self-care and repositioning compliance. Low current risk.",
            photo_url="https://i.pravatar.cc/150?img=45",
            risk_profile="low"
        )
        
        print("\n" + "="*60)
        print("[OK] Successfully created 3 additional test patients!")
        print("="*60)
        print("\nLogin credentials (all use password: password123):")
        print("  - emma.wilson@example.com (High Risk)")
        print("  - james.chen@example.com (Medium Risk)")
        print("  - sarah.martinez@example.com (Low Risk)")
        print("\nEach patient has 100 frames of pressure data over the last 2 hours.")
        
    except Exception as e:
        print(f"\n[X] ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Make sure the backend server is NOT running (it locks the database)")
        print("2. Check that the database exists and is accessible")
        print("3. Verify that the 'users' and 'frames' tables exist")


if __name__ == "__main__":
    main()
