import sys
import os
import random
import string
import asyncio
from fastapi.testclient import TestClient

# Ensure we can import app
sys.path.append(os.getcwd())

from app.main import app
from app.db.mongodb import init_db

# We need to ensure DB is initialized if TestClient doesn't trigger lifespan fully in the way we expect with async,
# but TestClient with 'with' context manager handles lifespan.
# However, init_db is async. Beanie init is async. 
# TestClient is synchronous by default but supports async apps.
# The lifespan is async. TestClient handles it.

def test_security_fix():
    print("--- Testing Security Fix with TestClient ---")
    
    rand_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    email = f"attacker_local_{rand_suffix}@evil.com"
    
    with TestClient(app) as client:
        payload = {
            "email": email,
            "password": "Password123!",
            "full_name": "Attacker",
            "role": "LAWYER"
        }
        
        print(f"Attempting to register {email} as LAWYER...")
        response = client.post("/api/v1/auth/register", json=payload)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"Registration Successful.")
            print(f"Registered Role: {user_data.get('role')}")
            
            if user_data.get('role') == "LAWYER":
                print("FAIL: VULNERABILITY PERSISTS. User registered as LAWYER.")
                sys.exit(1)
            elif user_data.get('role') == "BUYER":
                print("PASS: SUCCESS! User registered as BUYER despite requesting LAWYER.")
                sys.exit(0)
            else:
                print(f"UNKNOWN: User registered as {user_data.get('role')}")
                sys.exit(1)
        else:
            print(f"Registration Failed: {response.text}")
            # If it fails for some other reason (like DB not connected), we need to know.
            sys.exit(1)

if __name__ == "__main__":
    try:
        test_security_fix()
    except Exception as e:
        print(f"Error: {e}")
        # Async/Loop issues might occur if we don't handle the loop carefully, 
        # but TestClient usually handles this. If not, we might need a different approach.
