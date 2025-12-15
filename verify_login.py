import requests
import json
import base64

URL = "http://localhost:8000/api/v1/auth/login"
# User credentials
USERNAME = "admin@realtech.in"
PASSWORD = "admin"

print(f"Attempting login to {URL} with username={USERNAME}...")

try:
    # OAuth2PasswordRequestForm expects FORM data, not JSON
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    response = requests.post(URL, data=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Body: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")
