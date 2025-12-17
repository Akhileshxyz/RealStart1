import requests
import sys
import os
import json

sys.path.append(os.getcwd())

BASE_URL = "http://localhost:8000/api/v1"

def verify_optimization():
    print("1. Fetching Landmark List (Summary)...")
    try:
        resp = requests.get(f"{BASE_URL}/public/landmarks")
        if resp.status_code != 200:
            print(f"Failed to fetch list: {resp.status_code}")
            return
        
        data = resp.json()
        if not isinstance(data, list):
            print("Response is not a list")
            return
        
        if len(data) == 0:
            print("No landmarks found to verify.")
            return

        first_item = data[0]
        print(f"First item keys: {list(first_item.keys())}")
        
        # Check for summary fields
        if "median_price" in first_item and "nearby_amenities" not in first_item:
            print("SUCCESS: List endpoint returned Summary object.")
        else:
            print("FAILURE: List endpoint returned Detail object (or missing fields).")
            print(f"Keys present: {list(first_item.keys())}")

        # 2. Fetch Detail
        lm_id = first_item["id"]
        print(f"2. Fetching Landmark Detail for {lm_id}...")
        detail_resp = requests.get(f"{BASE_URL}/public/landmarks/{lm_id}")
        if detail_resp.status_code == 200:
            detail = detail_resp.json()
            if "nearby_amenities" in detail and "nearby_projects" in detail:
                 print("SUCCESS: Detail endpoint returned Full object.")
            else:
                 print("FAILURE: Detail endpoint missing detailed fields.")
        else:
            print(f"Failed to fetch detail: {detail_resp.status_code}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    verify_optimization()
