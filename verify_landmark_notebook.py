import requests
import sys
import os

sys.path.append(os.getcwd())

BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin@realtech.in"
PASSWORD = "admin"

def verify_landmark_notebook():
    print("1. Logging in...")
    login_resp = requests.post(f"{BASE_URL}/auth/login", data={"username": USERNAME, "password": PASSWORD})
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.text}")
        return
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create Dummy Landmark (e.g. Center of Bangalore)
    print("2. Creating Dummy Landmark...")
    landmark_data = {
        "name": "Central Park",
        "city": "Bangalore",
        "latitude": 12.9716, 
        "longitude": 77.5946,
        "median_price": 8500.50,
        "growth_forecast_5yr": 12.5,
        "price_trend_3m": "+4.2%",
        "active_layouts_count": 5,
        "rera_projects_count": 3
    }
    lm_resp = requests.post(f"{BASE_URL}/admin/landmarks", headers=headers, json=landmark_data)
    if lm_resp.status_code not in [200, 201]:
        print(f"Failed to create landmark: {lm_resp.text}")
        return
    landmark_id = lm_resp.json()["id"]
    print(f"Landmark created: {landmark_id}")
    
    # 3. Create Dummy Project NEARBY (e.g. 1km away)
    # 1 deg lat approx 111km. 0.01 deg approx 1.1km.
    print("3. Creating Nearby Project...")
    dev_resp = requests.get(f"{BASE_URL}/admin/developers", headers=headers)
    if len(dev_resp.json()) > 0:
        dev_id = dev_resp.json()[0]["id"]
    else:
        # Create dev if missing... skipping for brevity assuming previous steps created one
        print("No developers found, cannot create project.")
        return

    project_data = {
        "name": "Park View Residency",
        "developer_id": dev_id,
        "city": "Bangalore",
        "slug": "park-view-residency-v2",
        "latitude": 12.9780,  # Slightly north
        "longitude": 77.5946
    }
    proj_resp = requests.post(f"{BASE_URL}/developers/projects", headers=headers, json=project_data)
    if proj_resp.status_code in [200, 201]:
        print(f"Project created: {proj_resp.json()['slug']}")
    else:
        # Maybe slug exists
        print(f"Project creation response: {proj_resp.text}")

    # 4. Fetch Landmark Details
    print("4. Fetching Landmark Details (Notebook View)...")
    get_resp = requests.get(f"{BASE_URL}/public/landmarks/{landmark_id}")
    
    # DEBUG: Check all projects
    print("DEBUG: Checking all projects in DB...")
    all_proj_resp = requests.get(f"{BASE_URL}/admin/projects", headers=headers)
    if all_proj_resp.status_code == 200:
        for p in all_proj_resp.json():
            print(f"Project: {p['slug']} ({p.get('latitude')}, {p.get('longitude')})")
    
    if get_resp.status_code == 200:
        data = get_resp.json()
        print(f"Landmark Coords: {data.get('latitude')}, {data.get('longitude')}")
        print("Landmark Details Fetched.")
        # Check new fields
        print(f"Median Price: {data.get('median_price')}")
        print(f"Nearby Projects Count: {len(data.get('nearby_projects', []))}")
        
        if len(data.get('nearby_projects', [])) > 0:
            print("SUCCESS: Nearby project found in landmark details.")
        else:
            print("FAILURE: No nearby projects found.")
    else:
        print(f"Failed to get landmark: {get_resp.status_code}")

if __name__ == "__main__":
    verify_landmark_notebook()
