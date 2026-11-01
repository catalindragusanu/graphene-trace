import requests
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

BASE_URL = "http://localhost:8000/api"

def test_clinician_dashboard():
    # 1. Login as clinician
    print("Logging in as clinician...")
    response = requests.post(f"{BASE_URL}/auth/login", data={
        "username": "test_clinician@example.com",
        "password": "password123"
    })
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
        
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Fetch patients
    print("\nFetching patients for dashboard...")
    response = requests.get(f"{BASE_URL}/users/patients", headers=headers)
    
    if response.status_code == 200:
        patients = response.json()
        print(f"✓ Success! Found {len(patients)} patients.")
        for p in patients:
            print(f"  - {p['name']} (ID: {p['id']})")
            print(f"    Risk: {p['risk_level']}")
            print(f"    Max Pressure: {p['max_pressure']}")
            print(f"    Last Updated: {p['last_updated']}")
    else:
        print(f"✗ Failed to fetch patients: {response.text}")

if __name__ == "__main__":
    test_clinician_dashboard()
