
import requests
import sys

BASE_URL = "http://localhost:8004/api/v1"

try:
    print("Requesting landmarks...")
    resp = requests.get(f"{BASE_URL}/public/landmarks?city=Devanahalli")
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
