import sys
import os
from fastapi.testclient import TestClient
import asyncio

# Ensure app in path
sys.path.append(os.getcwd())

from app.main import app
from app.api.v1.public_auth import router as public_router
from app.api.v1.admin_auth import router as admin_router

def test_auth_separation():
    print("--- Testing Auth Separation ---")
    
    # We assume 'superadmin@realstart.com/admin123' exists (Admin)
    # We assume 'user@realstart.com/user123' exists (Buyer)
    # These are default seeds. If not present, this test might fail or need setup.
    # For now, let's assume they exist from setup_test_data.py
    
    with TestClient(app) as client:
        # 1. Test Public Login (Expected: Buyer Success, Admin Fail)
        print("\n[TEST 1] Public Login (/auth/login)")
        
        # Buyer Login
        resp = client.post("/api/v1/auth/login", data={"username": "user@realstart.com", "password": "user123"})
        if resp.status_code == 200:
            print("PASS: Buyer logged in successfully.")
        else:
            print(f"FAIL: Buyer login failed: {resp.status_code} {resp.text}")

        # Admin Login
        resp = client.post("/api/v1/auth/login", data={"username": "superadmin@realstart.com", "password": "admin123"})
        if resp.status_code == 403:
             print("PASS: Admin login correctly forbidden on public portal.")
        elif resp.status_code == 200:
             print("FAIL: Admin logged in on public portal! (Security Issue)")
        else:
             print(f"INFO: Admin login returned {resp.status_code} (Expected 403)")

        # 2. Test Admin Login (Expected: Admin Success, Buyer Fail)
        print("\n[TEST 2] Admin Login (/admin/login)")
        
        # Admin Login
        resp = client.post("/api/v1/admin/login", data={"username": "superadmin@realstart.com", "password": "admin123"})
        if resp.status_code == 200:
            print("PASS: Admin logged in successfully on admin portal.")
        else:
            print(f"FAIL: Admin login failed: {resp.status_code} {resp.text}")

        # Buyer Login
        resp = client.post("/api/v1/admin/login", data={"username": "user@realstart.com", "password": "user123"})
        if resp.status_code == 403:
             print("PASS: Buyer login correctly forbidden on admin portal.")
        elif resp.status_code == 200:
             print("FAIL: Buyer logged in on admin portal! (Security Issue)")
        else:
             print(f"INFO: Buyer login returned {resp.status_code} (Expected 403)")

if __name__ == "__main__":
    test_auth_separation()
