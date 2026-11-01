"""Test all user credentials to verify login works"""
import httpx
import json

# Test credentials
test_users = [
    ("test_profile@example.com", "Patient", "Test Profile"),
    ("patient1@example.com", "Patient", "John Doe"),
    ("patient2@example.com", "Patient", "Jane Smith"),
    ("patient3@example.com", "Patient", "Bob Johnson"),
    ("test_clinician@example.com", "Clinician", "Dr. Test Clinician"),
    ("clinician1@example.com", "Clinician", "Dr. Sarah Williams"),
    ("clinician2@example.com", "Clinician", "Dr. Michael Chen"),
]

password = "password123"
login_url = "http://localhost:8000/api/auth/login"

print("=" * 70)
print("Testing All User Logins")
print("=" * 70)
print()

success_count = 0
fail_count = 0

for email, role, name in test_users:
    try:
        response = httpx.post(
            login_url,
            json={"email": email, "password": password},
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            print(f"[+] SUCCESS: {name} ({email})")
            print(f"    Role: {data['role']}")
            print(f"    Token: {data['access_token'][:50]}...")
            success_count += 1
        else:
            print(f"[-] FAILED: {name} ({email})")
            print(f"    Status: {response.status_code}")
            print(f"    Response: {response.text}")
            fail_count += 1
    except Exception as e:
        print(f"[-] ERROR: {name} ({email})")
        print(f"    Error: {str(e)}")
        fail_count += 1

    print()

print("=" * 70)
print(f"Results: {success_count} successful, {fail_count} failed")
print("=" * 70)

if fail_count == 0:
    print()
    print("All login tests passed!")
else:
    print()
    print(f"WARNING: {fail_count} login(s) failed!")
