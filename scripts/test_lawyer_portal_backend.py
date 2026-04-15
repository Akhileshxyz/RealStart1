import asyncio
import requests
import json
import random
import string
import sys
import os

# Add parent dir to sys.path to allow imports from app
sys.path.append(os.getcwd())

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.lawyer import LawyerProfile, LawyerLead, LawyerSubscription

BASE_URL = "http://localhost:8000/api/v1"
rand_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
LAWYER_EMAIL = f"lawyer_test_{rand_suffix}@legal.com"
LAWYER_PASS = "TestPass123"

TOKENS = {}

async def seed_data():
    print("--- Seeding Data ---")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    # Minimal init for User and Lawyer models
    await init_beanie(database=client[settings.DATABASE_NAME], document_models=[User, LawyerProfile, LawyerLead, LawyerSubscription])
    
    # Create Lawyer
    existing = await User.find_one({"email": LAWYER_EMAIL})
    if not existing:
        lawyer = User(
            email=LAWYER_EMAIL,
            hashed_password=get_password_hash(LAWYER_PASS),
            full_name="Test Lawyer Direct",
            role=UserRole.LAWYER,
            is_active=True
        )
        await lawyer.insert()
        print(f"Created Lawyer: {LAWYER_EMAIL}")
    else:
        print(f"Lawyer already exists: {LAWYER_EMAIL}")

def login_lawyer():
    print("\n--- Logging in Lawyer ---")
    resp = requests.post(f"{BASE_URL}/admin/login", data={"username": LAWYER_EMAIL, "password": LAWYER_PASS})
    # Note: Login endpoint is /admin/login for privileged users (including Lawyers) based on admin_auth.py
    # Wait, /admin/login is mapped to login_admin_access_token in admin_auth.py
    # Let's check api/v1/auth/login too? No, admin_auth is for admin/login.
    # Actually public_auth might have login too. Let's try /auth/login first which is usually public_auth.
    
    # Trying public login first as per previous script
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": LAWYER_EMAIL, "password": LAWYER_PASS})
    
    if resp.status_code == 200:
        TOKENS["LAWYER"] = resp.json()["access_token"]
        print("Login Successful")
        return True
    
    # Try Admin login endpoint if public fails (though Lawyer should be able to use public login?)
    # Based on admin_auth.py: "OAuth2 compatible token login for Privileged Users... restricted: BUYER role cannot login here"
    # So Lawyer SHOULD use /admin/login ?
    print(f"Public login failed ({resp.status_code}), trying Admin login...")
    resp = requests.post(f"{BASE_URL}/admin/login", data={"username": LAWYER_EMAIL, "password": LAWYER_PASS})
    if resp.status_code == 200:
        TOKENS["LAWYER"] = resp.json()["access_token"]
        print("Admin Login Successful")
        return True
        
    print(f"Login Failed: {resp.text}")
    return False

def test_profile():
    print("\n--- Testing Profile ---")
    headers = {"Authorization": f"Bearer {TOKENS['LAWYER']}"}
    
    # Get Profile
    resp = requests.get(f"{BASE_URL}/lawyer/profile", headers=headers)
    if resp.status_code != 200:
        print(f"Get Profile Failed: {resp.text}")
        return
    print("Profile fetched")
    
    # Update Profile
    update_data = {
        "bio": "Seeded Lawyer Bio",
        "specialization": ["Corporate"],
        "is_online": True,
        "cities": ["Mumbai"]
    }
    resp = requests.patch(f"{BASE_URL}/lawyer/profile", headers=headers, json=update_data)
    if resp.status_code == 200:
        print("Profile updated verified")
    else:
        print(f"Update Profile Failed: {resp.text}")

def test_crm_and_dashboard():
    print("\n--- Testing CRM & Dashboard ---")
    headers = {"Authorization": f"Bearer {TOKENS['LAWYER']}"}
    
    # Create Lead
    lead_payload = {
        "client_name": "Direct Client",
        "client_phone": "+919988776655",
        "notes": "Direct Seeding Test"
    }
    resp = requests.post(f"{BASE_URL}/lawyer/leads", headers=headers, json=lead_payload)
    if resp.status_code != 200:
        print(f"Create Lead Failed: {resp.text}")
        return
    print(f"Create Lead Response: {resp.text}")
    lead_id = resp.json().get("id") or resp.json().get("_id")
    print(f"Lead created: {lead_id}")
    
    # List Leads
    resp = requests.get(f"{BASE_URL}/lawyer/leads", headers=headers)
    if resp.status_code == 200:
        print(f"Leads listed: {len(resp.json())}")
    
    # Dashboard
    resp = requests.get(f"{BASE_URL}/lawyer/dashboard/analytics", headers=headers)
    if resp.status_code == 200:
        print(f"Analytics: {resp.json()}")

def test_subscription():
    print("\n--- Testing Subscription ---")
    headers = {"Authorization": f"Bearer {TOKENS['LAWYER']}"}
    resp = requests.get(f"{BASE_URL}/lawyer/subscription", headers=headers)
    print(f"Subscription Status: {resp.status_code}")

if __name__ == "__main__":
    # Run async setup
    asyncio.run(seed_data())
    
    # Run HTTP tests
    if login_lawyer():
        test_profile()
        test_crm_and_dashboard()
        test_subscription()
