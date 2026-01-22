import json
import os
from pathlib import Path
from copy import deepcopy

# Configuration
OPENAPI_PATH = "openapi.json"
OUTPUT_PATH = "testsprite_tests/tmp/code_summary.json"
PROJECT_ROOT = "."

# Tech Stack
TECH_STACK = ["Python", "FastAPI", "MongoDB", "Beanie", "Redis", "Razorpay"]

# Coarse-grained Feature Mapping (Prefix -> (Name, List of Files, Description))
# Note: Using lists of files to aggregate multiple modules.
FEATURE_GROUPS = [
    (
        ["/api/v1/auth", "/api/v1/public", "/api/v1/users"],
        "Public User Portal",
        [
            "app/api/v1/public_auth.py",
            "app/api/v1/public_projects.py",
            "app/api/v1/user_portal.py",
            "app/api/v1/user_interactions.py"
        ],
        "Public access, user authentication, profile, and project interactions."
    ),
    (
        ["/api/v1/developers"],
        "Developer Portal",
        [
            "app/api/v1/developer_auth.py",
            "app/api/v1/developer_projects.py",
            "app/api/v1/developer_leads.py",
            "app/api/v1/developer_webhooks.py",
            "app/api/v1/developer_team.py",
            "app/api/v1/developer_subscriptions.py",
            "app/api/v1/developer_uploads.py"
        ],
        "Developer dashboard, project management, leads, and team tools."
    ),
    (
        ["/api/v1/admin"],
        "Admin Portal",
        [
            "app/api/v1/admin_auth.py",
            "app/api/v1/admin_projects.py",
            "app/api/v1/developers.py",
            "app/api/v1/users.py",
            "app/api/v1/admin_change_requests.py",
            "app/api/v1/admin_subscriptions.py",
            "app/api/v1/admin_dashboard.py",
            "app/api/v1/admin_analytics.py",
            "app/api/v1/admin_ads.py",
            "app/api/v1/admin_team.py",
            "app/api/v1/admin_landmarks.py",
            "app/api/v1/admin_videos.py"
        ],
        "Administrative controls for users, developers, projects, and system settings."
    ),
    (
        ["/api/v1/lawyer"],
        "Lawyer Portal",
        [
            "app/api/v1/lawyer_auth.py",
            "app/api/v1/lawyer_dashboard.py",
            "app/api/v1/lawyer_cases.py",
            "app/api/v1/lawyer_clients.py",
            "app/api/v1/lawyer_schedule.py",
            "app/api/v1/lawyer_analytics.py",
            "app/api/v1/lawyer_settings.py"
        ],
        "Lawyer interface for case management and legal requests."
    ),
    (
        ["/api/v1/locality"],
        "Locality Intelligence",
        ["app/api/v1/locality.py"],
        "Map-based locality data and market intelligence."
    ),
    (
        ["/api/v1/settings"],
        "General Settings",
        ["app/api/v1/admin_settings.py"],
        "General settings shared across user types."
    )
]

def generate():
    if not os.path.exists(OPENAPI_PATH):
        print(f"Error: {OPENAPI_PATH} not found.")
        return

    with open(OPENAPI_PATH, 'r') as f:
        openapi_spec = json.load(f)

    features = []
    
    assigned_paths = set()
    
    for prefixes, name, filepaths, description in FEATURE_GROUPS:
        feature_paths = {}
        for path, path_item in openapi_spec.get('paths', {}).items():
            # Check if path starts with any of the prefixes for this group
            if any(path.startswith(p) for p in prefixes) and path not in assigned_paths:
                feature_paths[path] = path_item
                assigned_paths.add(path)
        
            # Create a mini OpenAPI spec for this feature - SIMPLIFIED TO EMPTY to avoid backend 500
            feature_api_doc = {} 
            # feature_api_doc = deepcopy(openapi_spec)
            # feature_api_doc['paths'] = feature_paths
            
            features.append({
                "name": name,
                "description": description,
                "files": filepaths,
                "api_doc": feature_api_doc
            })

    output = {
        "tech_stack": TECH_STACK,
        "features": features
    }

    # Ensure output dir exists
    Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Successfully generated coarse-grained code summary at {OUTPUT_PATH}")

if __name__ == "__main__":
    generate()
