import requests
import json

# Test the corrected endpoint
BASE_URL = "http://127.0.0.1:8000/api/v1"
LANDMARK_ID = "30fa0039-a3fc-4b15-935f-ca8850dbb875"

print("Testing Market Intelligence API...")
print(f"Endpoint: {BASE_URL}/locality/market-intelligence/{LANDMARK_ID}")
print()

try:
    response = requests.get(f"{BASE_URL}/locality/market-intelligence/{LANDMARK_ID}")
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Success! API returned valid data")
        print()
        print("Data summary:")
        print(f"  - market_overview: {data.get('market_overview', '')[:100]}...")
        print(f"  - Location Type: {data.get('location_type')}")
        print(f"  - Appreciation Potential: {data.get('appreciation_potential_5yr')}")
        print(f"  - Growth History Records: {len(data.get('growth_history', []))}")
        print(f"  - Growth Prediction Records: {len(data.get('growth_prediction', []))}")
        print(f"  - Amenities: {len(data.get('amenities', []))}")
        print(f"  - Investment Landmarks: {len(data.get('investment_landmarks', []))}")
        print(f"  - Map Landmarks: {len(data.get('map_landmarks', []))}")
    else:
        print(f"✗ Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("✗ Error: Could not connect to server. Is it running?")
except Exception as e:
    print(f"✗ Error: {e}")
