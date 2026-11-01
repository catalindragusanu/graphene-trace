from passlib.context import CryptContext
import sys

print("Testing password hash...")
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed = pwd_context.hash("password123")
    print(f"Hash success: {hashed[:20]}...")
except Exception as e:
    print(f"Hash failed: {e}")
    sys.exit(1)
