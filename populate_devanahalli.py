import requests
import json
import sys
import os

sys.path.append(os.getcwd())

BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin@realtech.in"
PASSWORD = "admin"

def populate_devanahalli():
    # 1. Login
    print("Logging in...")
    login_resp = requests.post(f"{BASE_URL}/auth/login", data={"username": USERNAME, "password": PASSWORD})
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.text}")
        return
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Prepare Data
    amenities = {
        "Healthcare": ["Akash Hospital & Medical College", "Manipal Hospital (near airport road)"],
        "Education": ["Akash International School", "Canadian International School", "GITAM University"],
        "Retail_Leisure": ["Devanahalli Town Market", "RMZ Galleria Mall", "Devanahalli Fort", "Upcoming Town Center"],
        "Infrastructure": ["Namma Metro (Blue Line Extension phase 2B)", "Satellite Town Ring Road (STRR)", "BIAL IT Investment Region", "Devanahalli Business Park"]
    }

    landmark_data = {
        "name": "Devanahalli - Bus Stand Road Area",
        "city": "Devanahalli",
        "zone": "North Bengaluru",
        # Approx coords for Devanahalli Bus Stand
        "latitude": 13.2489, 
        "longitude": 77.7137,
        
        # Real Estate Data
        "avg_price_per_sqft": 5750.0, # Avg of 3500-8000 for plots
        "median_price": 5750.0,
        "growth_forecast_5yr": 20.0, # 15-25%
        "price_trend": "rising",
        "price_trend_3m": "+4.2% (Est. based on annual)", 
        
        "total_projects": 12, # Placeholder based on "Active Layouts"
        "active_layouts_count": 8,
        "rera_projects_count": 5,

        "description": "Devanahalli is evolving from an airport suburb into a self-sustained Smart City. Its growth is mandated by large-scale government and private investments. The Bus Stand Road is the historic town center, providing local market convenience and easy access to the main highways.",
        "nearby_amenities": amenities
    }

    # 3. Create Landmark
    print("Creating Landmark...")
    resp = requests.post(f"{BASE_URL}/admin/landmarks", headers=headers, json=landmark_data)
    if resp.status_code in [200, 201]:
        print("Successfully created Landmark: Devanahalli - Bus Stand Road Area")
        print(json.dumps(resp.json(), indent=2))
    else:
        print(f"Failed to create landmark. Status: {resp.status_code}")
        print(resp.text)

if __name__ == "__main__":
    populate_devanahalli()
