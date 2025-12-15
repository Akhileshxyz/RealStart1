import requests
import json

# Adjust URL to an endpoint that definitely exists and is protected.
# Based on main.py: /api/v1/auth/me usually exists or similar.
# Let's check api/v1/users/me or admin endpoints.
# main.py includes admin_projects at /api/v1/admin/projects
# Let's try to hit a likely protected endpoint.

URL = "http://localhost:8000/api/v1/admin/developers" 

try:
    response = requests.get(URL)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Length: {response.headers.get('content-length')}")
    print(f"Body: {response.text}")
    print(f"Body Length: {len(response.text)}")
except Exception as e:
    print(f"Error: {e}")
