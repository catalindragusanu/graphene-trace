"""Create a single test user profile"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.user import User, UserRole
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


def create_test_profile():
    """Create a test user profile."""
    db = SessionLocal()

    email = "test_profile@example.com"
    password = "password123"
    name = "Test Profile"
    role = "patient" # unused in ORM mode logic below (we access UserRole.patient directly)

    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User {email} already exists.")
            return

        print(f"Creating user {email}...")
        
        # Create user using ORM to verify Enum working correctly
        user = User(
            email=email,
            password_hash=hash_password(password),
            role=UserRole.patient,
            name=name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✓ User created/verified successfully!")
        print(f"  - ID: {user.id}")
        print(f"  - Email: {user.email}")
        print(f"  - Password: {password}")
        print(f"  - Role: {user.role}")

    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_profile()
