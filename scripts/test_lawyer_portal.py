import requests
import json
import random
import string
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8002/api/v1"
rand_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))

# State
TOKENS = {}
IDS = {}

def setup_users():
    print("--- Setting up Users ---")
    # 1. Admin Login
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": "superadmin@realstart.com", "password": "admin123"})
    TOKENS["ADMIN"] = resp.json()["access_token"]
    
    # 2. Create Lawyer
    lawyer_email = f"lawyer_{rand_suffix}@legal.com"
    resp = requests.post(f"{BASE_URL}/admin/users/", headers={"Authorization": f"Bearer {TOKENS['ADMIN']}"}, 
                         json={"email": lawyer_email, "password": "LawyerPass123!", "full_name": "Test Lawyer", "role": "LAWYER"})
    if resp.status_code not in [200, 201]:
        print(f"Create Lawyer Failed: {resp.text}")
    
    # Login Lawyer
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": lawyer_email, "password": "LawyerPass123!"})
    TOKENS["LAWYER"] = resp.json()["access_token"]
    print(f"Lawyer created: {lawyer_email}")

    # 3. Create Developer
    dev_email = f"dev_{rand_suffix}@build.com"
    resp = requests.post(f"{BASE_URL}/admin/register-admin", headers={"Authorization": f"Bearer {TOKENS['ADMIN']}"},
                  json={"email": dev_email, "password": "DevPass123!", "full_name": "Dev", "role": "DEVELOPER"})
    if resp.status_code not in [200, 201]:
        print(f"Create Developer Failed: {resp.text}")

    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": dev_email, "password": "DevPass123!"})
    if resp.status_code != 200:
        print(f"Login Developer Failed: {resp.text}")
    TOKENS["DEV"] = resp.json()["access_token"]
    
    # 4. Create Buyer
    buyer_email = f"buyer_{rand_suffix}@buy.com"
    resp = requests.post(f"{BASE_URL}/auth/register", json={"email": buyer_email, "password": "BuyPass123!", "full_name": "Buyer", "role": "BUYER"})
    if resp.status_code not in [200, 201]:
        print(f"Create Buyer Failed: {resp.text}")

    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": buyer_email, "password": "BuyPass123!"})
    TOKENS["BUYER"] = resp.json()["access_token"]

def test_incoming_items():
    print("\n--- Testing Incoming Items ---")
    # 1. Developer creates project with docs
    docs = [{"name": "RTC", "file_url": "http://s3/rtc.pdf"}, {"name": "EC", "file_url": "http://s3/ec.pdf"}]
    payload = {
        "name": f"Legal Proj {rand_suffix}", 
        "slug": f"legal-proj-{rand_suffix}", 
        "description": "Verify me",
        "documents": docs
    }
    resp = requests.post(f"{BASE_URL}/developers/projects/", headers={"Authorization": f"Bearer {TOKENS['DEV']}"}, json=payload)
    if resp.status_code != 200:
        print(f"Create Project Failed: {resp.text}")
        return
    project = resp.json()
    IDS["PROJECT_ID"] = project["id"]
    IDS["SLUG"] = project["slug"]
    print(f"Project Created with {len(project['documents'])} docs.")

    # 2. Lawyer lists incoming items
    resp = requests.get(f"{BASE_URL}/lawyer/incoming-items", headers={"Authorization": f"Bearer {TOKENS['LAWYER']}"})
    items = resp.json()
    found = next((i for i in items if i["project_id"] == IDS["PROJECT_ID"]), None)
    if found:
        print("Success: Project found in Lawyer Incoming Items")
        print(f"Pending Docs: {found['pending_docs']}")
    else:
        print("Failure: Project NOT found in Incoming Items")
        return

    # 3. Lawyer reviews document
    # Get IDs
    resp = requests.get(f"{BASE_URL}/lawyer/projects/{IDS['PROJECT_ID']}/documents", headers={"Authorization": f"Bearer {TOKENS['LAWYER']}"})
    docs = resp.json()
    doc_id = docs[0]["id"]
    
    # Verify
    payload = {"status": "VERIFIED", "lawyer_notes": "All good"}
    resp = requests.patch(f"{BASE_URL}/lawyer/projects/{IDS['PROJECT_ID']}/documents/{doc_id}", 
                          headers={"Authorization": f"Bearer {TOKENS['LAWYER']}"}, json=payload)
    if resp.status_code == 200:
        print("Success: Document Verified")
        print(resp.json())
    else:
        print(f"Failure: Verify Doc {resp.text}")

def test_legal_calls():
    print("\n--- Testing Legal Calls ---")
    # 1. Buyer requests legal call
    payload = {
        "topics": ["Title Check", "Loan"],
        "scheduled_time": (datetime.utcnow() + timedelta(days=1)).isoformat()
    }
    resp = requests.post(f"{BASE_URL}/users/interactions/{IDS['SLUG']}/legal-request", 
                         headers={"Authorization": f"Bearer {TOKENS['BUYER']}"}, json=payload)
    if resp.status_code == 200:
        print("Success: Legal Request Created")
    else:
        print(f"Failure Create Request: {resp.text}")
        return

    # 2. Lawyer Lists Calls
    resp = requests.get(f"{BASE_URL}/lawyer/legal-calls?status=OPEN", headers={"Authorization": f"Bearer {TOKENS['LAWYER']}"})
    calls = resp.json()
    # Find our call (by project id or just take latest)
    my_call = next((c for c in calls if c["project_id"] == IDS["PROJECT_ID"]), None)
    
    if my_call:
        print("Success: Call found in Lawyer Dashboard")
        IDS["CALL_ID"] = my_call["id"]
    else:
        print("Failure: Call NOT found")
        return

    # 3. Lawyer Completes Call
    payload = {
        "lawyer_notes": "Spoke to client, clear title.", 
        "opinion_file_url": "http://s3/opinion.pdf"
    }
    resp = requests.patch(f"{BASE_URL}/lawyer/legal-calls/{IDS['CALL_ID']}/complete",
                          headers={"Authorization": f"Bearer {TOKENS['LAWYER']}"}, json=payload)
    if resp.status_code == 200:
        print("Success: Call Completed")
        print(resp.json())
    else:
        print(f"Failure Complete Call: {resp.text}")

if __name__ == "__main__":
    try:
        setup_users()
        test_incoming_items()
        test_legal_calls()
    except Exception as e:
        print(f"Error: {e}")
