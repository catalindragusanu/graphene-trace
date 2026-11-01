"""Seed database with test users"""
import sys
import os

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


def seed_users():
    """Create test users in the database."""
    db = SessionLocal()

    try:
        # Check if users already exist
        existing_count = db.query(User).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} users.")
            response = input("Do you want to clear existing users and reseed? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborting.")
                return

            # Delete existing groups and users (groups reference users)
            db.execute(group_membership.delete())
            db.query(UserGroup).delete()
            db.query(User).delete()
            db.commit()
            print("Existing users cleared.")

        print("Creating test users...")

        # Create patients
        patients = []
        for i in range(1, 6):  # Users 1-5
            patient = User(
                id=i,
                email=f"patient{i}@example.com",
                password_hash=hash_password("password123"),
                role=UserRole.patient,
                name=f"Patient {i}"
            )
            patients.append(patient)
            db.add(patient)

        # Create clinicians
        clinicians = []
        for i in range(1, 3):  # 2 clinicians
            clinician = User(
                id=i + 10,  # IDs 11, 12
                email=f"clinician{i}@example.com",
                password_hash=hash_password("password123"),
                role=UserRole.clinician,
                name=f"Dr. Clinician {i}"
            )
            clinicians.append(clinician)
            db.add(clinician)

        # Commit all users
        db.commit()

        # Assign patients to clinicians via groups (clinician access is group-based)
        assignments = {clinicians[0]: patients[:3], clinicians[1]: patients[3:]}
        for clinician, assigned in assignments.items():
            group = UserGroup(name=f"{clinician.name}'s patients", clinician_id=clinician.id)
            group.patients = assigned
            db.add(group)
        db.commit()

        print()
        print("✓ Test users created successfully!")
        print()
        print("Patients:")
        for patient in patients:
            print(f"  - {patient.email} (password: password123)")

        print()
        print("Clinicians:")
        for clinician in clinicians:
            print(f"  - {clinician.email} (password: password123)")

        print()
        print(f"Total users created: {len(patients) + len(clinicians)}")
        print("Groups: clinician1 -> patients 1-3, clinician2 -> patients 4-5")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Database Seeding Tool")
    print("=" * 60)
    print()

    seed_users()

    print()
    print("Database seeded successfully!")
    print("You can now run the CSV import script to load pressure data.")
