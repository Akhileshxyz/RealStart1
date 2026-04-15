import requests
import random
import string

BASE_URL = "http://localhost:8002/api/v1"
rand_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))

def reproduce_vulnerability():
    print("--- Attempting to exploit Public Registration Vulnerability ---")
    
    email = f"attacker_{rand_suffix}@evil.com"
    payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Attacker",
        "role": "LAWYER"  # Trying to register as LAWYER
    }
    
    print(f"Registering user {email} with role LAWYER...")
    resp = requests.post(f"{BASE_URL}/auth/register", json=payload)
    
    if resp.status_code == 200:
        user_data = resp.json()
        print(f"Registration Successful.")
        print(f"Registered Role: {user_data.get('role')}")
        
        if user_data.get('role') == "LAWYER":
            print("❌ VULNERABILITY CONFIRMED: User successfully registered as LAWYER.")
        else:
            print(f"✅ Safe: User registered as {user_data.get('role')} despite requesting LAWYER.")
    else:
        print(f"Registration Failed: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    reproduce_vulnerability()
