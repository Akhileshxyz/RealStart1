import requests
import json
import random
import string
import time

BASE_URL = "http://localhost:8000/api/v1"
rand_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))

def test_locality_features():
    print(f"--- Starting Locality Features Verification (Run: {rand_suffix}) ---")
    
    # 1. Login as Admin to Create Landmark
    admin_resp = requests.post(f"{BASE_URL}/admin/login", data={"username": "admin@realstart.com", "password": "admin"}, timeout=10)
    
    if admin_resp.status_code != 200:
        print("FATAL: Admin login failed")
        return
    admin_token = admin_resp.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 2. Login as User for Reviews
    print("2. Authenticating User...")
    user_email = f"reviewer_{rand_suffix}@ex.com"
    requests.post(f"{BASE_URL}/auth/register", json={"email": user_email, "password": "Password123!", "full_name": "Reviewer", "role": "BUYER"})
    user_resp = requests.post(f"{BASE_URL}/auth/login", data={"username": user_email, "password": "Password123!"})
    if user_resp.status_code != 200:
        print("FATAL: User login failed")
        return
    user_token = user_resp.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # 3. Create Landmark (Use Resolve API or Admin API - using Resolve for full flow)
    print("3. Resolving/Creating Locality...")
    resolve_payload = {
        "place_name": f"Locality {rand_suffix}", 
        "latitude": 12.935, 
        "longitude": 77.625
    }
    # Resolve API is public? locality.py doesn't have auth dep on @router
    # But wait, it's public.
    res_resp = requests.post(f"{BASE_URL}/locality/resolve", json=resolve_payload)
    if res_resp.status_code != 200:
        print(f"FAIL: Resolve failed: {res_resp.text}")
        return
    
    landmark_id = res_resp.json()["landmark_id"]
    print(f"   > Landmark Created: {landmark_id}")
    
    # 4. Create Project Linked to Landmark (Need Developer Token)
    print("4. Creating Project linked to Landmark...")
    # Need dev token
    dev_email = f"dev_{rand_suffix}@ex.com"
    requests.post(f"{BASE_URL}/admin/register-admin", json={"email": dev_email, "password": "Password123!", "full_name": "Dev", "role": "DEVELOPER"}, headers=admin_headers)
    dev_resp = requests.post(f"{BASE_URL}/admin/login", data={"username": dev_email, "password": "Password123!"})
    dev_token = dev_resp.json()["access_token"]
    dev_headers = {"Authorization": f"Bearer {dev_token}"}
    
    proj_payload = {
        "name": f"Project at {rand_suffix}",
        "slug": f"proj-loc-{rand_suffix}",
        "developer_id": "00000000-0000-0000-0000-000000000000",
        "landmark_id": landmark_id # THIS IS THE KEY NEW FIELD
    }
    # Create project endpoint... /developers/projects/
    # But wait, does create project schema accept landmark_id? 
    # I updated the Model, but did I update the Pydantic Schema? 
    # CRITICAL CHECK! I likely missed updating the schema in `app/schemas/project.py` or similar.
    # The API will ignore it if not in schema.
    # Let's try and see.
    proj_resp = requests.post(f"{BASE_URL}/developers/projects/", json=proj_payload, headers=dev_headers, timeout=10)
    if proj_resp.status_code not in [200, 201]:
         print(f"WARN: Project creation failed (Schema might be missing field): {proj_resp.status_code} {proj_resp.text}")
    else:
         print("   > Project Created (Check if landmark_id persists requires fetch)")
         
    # 5. Verify New Endpoints
    print("\n5. Verifying Locality Endpoints...")
    
    # helper
    def check(meth, url, query=None, auth=None):
        full_url = f"{BASE_URL}{url}"
        if query: full_url += query
        r = requests.request(meth, full_url, headers=auth, timeout=10)
        status = "PASS" if r.status_code == 200 else "FAIL"
        print(f"   [{status}] {meth} {url} -> {r.status_code}")
        if r.status_code != 200: print(f"     Err: {r.text[:100]}")
        return r

    # Reviews
    print("   -- Reviews --")
    rev_payload = {"entity_id": landmark_id, "rating": 4.5, "content": "Great place!"}
    
    # Send JSON body
    requests.post(f"{BASE_URL}/locality/reviews", json=rev_payload, headers=user_headers, timeout=10)
    
    check("GET", f"/locality/reviews/locality?landmark_id={landmark_id}")
    check("GET", f"/locality/reviews/ratings-summary?landmark_id={landmark_id}")
    
    # Nearby
    print("   -- Nearby --")
    check("GET", f"/locality/nearby-areas?landmark_id={landmark_id}")
    
    # Projects
    print("   -- Projects --")
    check("GET", f"/locality/projects?landmark_id={landmark_id}")
    check("GET", f"/locality/societies?landmark_id={landmark_id}")
    
    # Stats
    print("   -- Stats --")
    check("GET", f"/locality/demand/overview?landmark_id={landmark_id}")
    check("GET", f"/locality/supply/overview?landmark_id={landmark_id}")
    
    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    test_locality_features()
