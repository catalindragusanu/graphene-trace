import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.models.user import UserRole
import enum

print(f"UserRole.PATIENT: {UserRole.PATIENT}")
print(f"UserRole.PATIENT.value: {UserRole.PATIENT.value}")
print(f"str(UserRole.PATIENT): {str(UserRole.PATIENT)}")
