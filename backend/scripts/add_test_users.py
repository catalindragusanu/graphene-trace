"""Add more test users without clearing existing data"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.user import User, UserRole
from passlib.context import CryptContext

# Import all models to ensure SQLAlchemy can resolve relationships
from app.models.frame import Frame  # noqa: F401
from app.models.metric import Metric  # noqa: F401
from app.models.alert import Alert  # noqa: F401
from app.models.comment import Comment  # noqa: F401
from app.models.group import UserGroup, group_membership  # noqa: F401
from app.models.movement_event import MovementEvent  # noqa: F401
from app.models.risk_score import RiskScore  # noqa: F401
from app.models.posture_label import PostureLabel  # noqa: F401

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


def add_test_users():
    """Add test users to the database without clearing existing ones."""
    db = SessionLocal()

    try:
        print("=" * 70)
        print("Adding Test Users")
        print("=" * 70)
        print()

        # Define users to create
        users_to_create = [
            {
                "email": "patient1@example.com",
                "password": "password123",
                "role": UserRole.patient,
                "name": "John Doe",
                "date_of_birth": date(1950, 3, 15),
                "medical_condition": "Spinal Cord Injury"
            },
            {
                "email": "patient2@example.com",
                "password": "password123",
                "role": UserRole.patient,
                "name": "Jane Smith",
                "date_of_birth": date(1965, 7, 22),
                "medical_condition": "Multiple Sclerosis"
            },
            {
                "email": "patient3@example.com",
                "password": "password123",
                "role": UserRole.patient,
                "name": "Bob Johnson",
                "date_of_birth": date(1978, 11, 8),
                "medical_condition": "Elderly, Limited Mobility"
            },
            {
                "email": "clinician1@example.com",
                "password": "password123",
                "role": UserRole.clinician,
                "name": "Dr. Sarah Williams"
            },
            {
                "email": "clinician2@example.com",
                "password": "password123",
                "role": UserRole.clinician,
                "name": "Dr. Michael Chen"
            }
        ]

        created_count = 0
        skipped_count = 0

        for user_data in users_to_create:
            # Check if user already exists
            existing = db.query(User).filter(User.email == user_data["email"]).first()

            if existing:
                print(f"[-] Skipped {user_data['email']} (already exists)")
                skipped_count += 1
                continue

            # Create new user
            user = User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
                name=user_data["name"],
                date_of_birth=user_data.get("date_of_birth"),
                medical_condition=user_data.get("medical_condition")
            )
            db.add(user)
            print(f"[+] Created {user_data['email']}")
            created_count += 1

        db.commit()

        print()
        print("=" * 70)
        print(f"Summary: {created_count} users created, {skipped_count} skipped")
        print("=" * 70)
        print()

        if created_count > 0:
            print("Run: python scripts/list_credentials.py")
            print("to see all available credentials")

    except Exception as e:
        print(f"Error adding users: {e}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    add_test_users()
