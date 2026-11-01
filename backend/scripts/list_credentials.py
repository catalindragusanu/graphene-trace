"""List all test user credentials in the database"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.user import User, UserRole

# Import all models to ensure SQLAlchemy can resolve relationships
from app.models.frame import Frame  # noqa: F401
from app.models.metric import Metric  # noqa: F401
from app.models.alert import Alert  # noqa: F401
from app.models.comment import Comment  # noqa: F401
from app.models.group import UserGroup, group_membership  # noqa: F401
from app.models.movement_event import MovementEvent  # noqa: F401
from app.models.risk_score import RiskScore  # noqa: F401
from app.models.posture_label import PostureLabel  # noqa: F401


def list_credentials():
    """List all user credentials."""
    db = SessionLocal()

    try:
        # Get all users
        users = db.query(User).order_by(User.role, User.id).all()

        if not users:
            print("No users found in database.")
            print()
            print("Run: python scripts/seed_database.py")
            print("to create test users.")
            return

        print("=" * 70)
        print("TEST CREDENTIALS")
        print("=" * 70)
        print()

        # Separate by role
        patients = [u for u in users if u.role == UserRole.patient]
        clinicians = [u for u in users if u.role == UserRole.clinician]

        if patients:
            print("PATIENTS:")
            print("-" * 70)
            for user in patients:
                print(f"  Email:    {user.email}")
                print(f"  Password: password123")
                print(f"  Name:     {user.name}")
                if user.date_of_birth:
                    print(f"  DOB:      {user.date_of_birth}")
                if user.medical_condition:
                    print(f"  Condition: {user.medical_condition}")
                print()

        if clinicians:
            print()
            print("CLINICIANS:")
            print("-" * 70)
            for user in clinicians:
                print(f"  Email:    {user.email}")
                print(f"  Password: password123")
                print(f"  Name:     {user.name}")
                print()

        print("=" * 70)
        print(f"Total users: {len(users)} ({len(patients)} patients, {len(clinicians)} clinicians)")
        print("=" * 70)
        print()
        print("NOTE: All test users use the password: password123")
        print()

    except Exception as e:
        print(f"Error listing credentials: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    list_credentials()
