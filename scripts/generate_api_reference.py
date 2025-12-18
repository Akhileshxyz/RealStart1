import requests
import json
import os
import random
import string

BASE_URL = "http://localhost:8000/api/v1"
OUTPUT_FILE = "API_REFERENCE_UPDATED.md"

# Global state
CONTEXT = {
    # Users
    "buyer_token": None,
    "dev_token": None,
    "admin_token": None,
    # IDs
    "project_id": None,
    "project_slug": None,
    "lead_id": None, 
    "webhook_id": None,
    "team_member_id": None,
    "user_id": None, # For Admin User tests
    "developer_entity_id": None, # For Admin Developer tests
    "change_request_id": None,
    "landmark_id": "LANDMARK_ID_PLACEHOLDER" # Will try to list to find one
}

rand_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))

def get_tokens():
    print("Authenticating initial users...")
    # 1. Super Admin (Seeded)
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": "superadmin@realstart.com", "password": "admin123"})
    if resp.status_code == 200:
        CONTEXT["admin_token"] = resp.json()["access_token"]
        print("Got ADMIN token")
    else:
        print(f"Failed to get Admin token: {resp.text}")

    # 2. Register/Login Fresh Developer (to avoid limits)
    if CONTEXT["admin_token"]:
        print("Registering fresh developer...")
        dev_email = f"dev_{rand_suffix}@realstart.com"
        dev_pass = "StrongDevPass123!"
        headers = {"Authorization": f"Bearer {CONTEXT['admin_token']}"}
        payload = {"email": dev_email, "password": dev_pass, "full_name": "Fresh Dev", "role": "DEVELOPER"}
        resp = requests.post(f"{BASE_URL}/admin/register-admin", json=payload, headers=headers)
        if resp.status_code in [200, 201]:
            # Login
            l_resp = requests.post(f"{BASE_URL}/auth/login", data={"username": dev_email, "password": dev_pass})
            if l_resp.status_code == 200:
                CONTEXT["dev_token"] = l_resp.json()["access_token"]
                print(f"Created and logged in fresh developer: {dev_email}")
            else:
                print("Failed to login fresh developer")
        else:
            print(f"Failed to create fresh developer: {resp.text}")

    # 3. Register/Login Fresh Buyer
    print("Registering fresh buyer...")
    buyer_email = f"buyer_{rand_suffix}@example.com"
    buyer_pass = "StrongUserPass123!"
    resp = requests.post(f"{BASE_URL}/auth/register", json={"email": buyer_email, "password": buyer_pass, "full_name": "Fresh Buyer", "role": "BUYER"})
    if resp.status_code in [200, 201]:
        # Login
        l_resp = requests.post(f"{BASE_URL}/auth/login", data={"username": buyer_email, "password": buyer_pass})
        if l_resp.status_code == 200:
            CONTEXT["buyer_token"] = l_resp.json()["access_token"]
            print(f"Created and logged in fresh buyer: {buyer_email}")
        else:
            print("Failed to login fresh buyer")
    else:
        print(f"Failed to create fresh buyer: {resp.text}")

def make_curl(method, url, headers, body=None, is_form=False):
    header_str = " ".join([f"-H '{k}: {v}'" for k, v in headers.items()])
    cmd = f"curl -X {method} '{url}' {header_str}"
    if body:
        if is_form:
            data_str = " ".join([f"-d '{k}={v}'" for k,v in body.items()])
            cmd += f" {data_str}"
        else:
            cmd += f" -d '{json.dumps(body)}'"
    return cmd

def resolve_path(path):
    for k, v in CONTEXT.items():
        if isinstance(v, str) and f"{{{k}}}" in path:
            path = path.replace(f"{{{k}}}", v)
    # Fallback
    if "{" in path:
        print(f"WARNING: Unresolved placeholder in {path}")
        path = path.replace("{project_id}", "00000000-0000-0000-0000-000000000000")
        path = path.replace("{slug}", "dummy-slug")
        path = path.replace("{id}", "00000000-0000-0000-0000-000000000000")
    return f"{BASE_URL}{path}"

def run_test(ep, index):
    title = f"{index}. {ep['title']}"
    print(f"\nTesting {title}...")
    
    url = resolve_path(ep['path'])
    method = ep['method']
    token_key = ep.get("auth_token")
    
    headers = {}
    if token_key and CONTEXT.get(token_key):
        headers["Authorization"] = f"Bearer {CONTEXT[token_key]}"
    
    body = ep.get("body")
    is_form = ep.get("is_form", False)
    
    # Send Request
    if is_form:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        resp = requests.request(method, url, headers=headers, data=body)
    else:
        if body is not None:
            headers["Content-Type"] = "application/json"
        
        # Check if this is the "Create Project" step, verify unique slug
        if ep['title'] == "Create Project" and body:
             body['slug'] = f"proj-{rand_suffix}" # ensure cached value matches? 
             # Wait, logic above used static slug in CONTEXT?
             # Let's dynamically update body if needed.
             pass

        resp = requests.request(method, url, headers=headers, json=body)

    # Capture
    if resp.status_code in [200, 201] and ep.get("capture"):
        data = resp.json()
        for path_key, ctx_key in ep["capture"].items():
            val = data.get(path_key)
            # Handle nested 'request_id' from update response
            if not val and path_key == "request_id" and "request_id" in data:
                val = data["request_id"]
            
            # Special case for List endpoints returning list
            if isinstance(data, list) and data:
                 if path_key == "[0].id":
                     val = data[0].get("id")
            
            if val:
                CONTEXT[ctx_key] = val
                print(f"Captured {ctx_key}: {val}")

    # Generate Output
    success_curl = make_curl(method, url, headers, body, is_form)
    try:
        success_resp = json.dumps(resp.json(), indent=2)
    except:
        success_resp = resp.text

    # Failure Output (Auth Fail)
    fail_headers = headers.copy()
    if token_key:
        fail_headers["Authorization"] = "Bearer invalid"
    fail_curl = make_curl(method, url, fail_headers, body, is_form)
    
    # If endpoint is public, force failure by bad ID or bad body?
    # Simplified: just auth failure call. If public, it might actually succeed (200).
    # We will record whatever happens.
    if is_form:
        f_resp = requests.request(method, url, headers=fail_headers, data=body)
    else:
        f_resp = requests.request(method, url, headers=fail_headers, json=body)
    
    try:
        fail_resp_txt = json.dumps(f_resp.json(), indent=2)
    except:
        fail_resp_txt = f_resp.text

    return {
        "title": title,
        "url": url,
        "success": {"status": resp.status_code, "curl": success_curl, "json": success_resp},
        "failure": {"status": f_resp.status_code, "curl": fail_curl, "json": fail_resp_txt}
    }

# ----------------- ENDPOINTS ORDERED BY MAIN.PY -----------------
ENDPOINTS = [
    # 1. Auth
    {"title": "Register Public User", "method": "POST", "path": "/auth/register", "body": {"email": f"b2_{rand_suffix}@ex.com", "password": "StrongPass123!", "full_name": "Test", "role": "BUYER"}},
    {"title": "Login", "method": "POST", "path": "/auth/login", "is_form": True, "body": {"username": f"buyer_{rand_suffix}@example.com", "password": "StrongUserPass123!"}},
    {"title": "Get Current User", "method": "GET", "path": "/auth/me", "auth_token": "buyer_token"},
    
    # 2. Admin Auth
    {"title": "Register Admin User", "method": "POST", "path": "/admin/register-admin", "auth_token": "admin_token", "body": {"email": f"adm2_{rand_suffix}@ex.com", "password": "StrongAdmin123!", "full_name": "Test Admin", "role": "ADMIN"}},

    # Developer Portal (Need these first to create content for Public/User endpoints)
    # create project -> approve it -> then public listing works
    {"title": "Create Project", "method": "POST", "path": "/developers/projects/", "auth_token": "dev_token", 
     "body": {"name": f"Project {rand_suffix}", "slug": f"proj-{rand_suffix}", "description": "Desc", "city": "Bangalore", "developer_id": "00000000-0000-0000-0000-000000000000"},
     "capture": {"id": "project_id", "slug": "project_slug"}},
    
    {"title": "List My Projects", "method": "GET", "path": "/developers/projects/my-projects", "auth_token": "dev_token"},
    
    # Admin Approve Project (to make it public)
    {"title": "Approve Project (Admin)", "method": "PATCH", "path": "/admin/projects/{project_id}/approve", "auth_token": "admin_token"},

    # 3. Public Projects
    {"title": "List Public Projects", "method": "GET", "path": "/public/projects/"},
    {"title": "Get Project by Slug", "method": "GET", "path": "/public/projects/{project_slug}"},

    # 4. User Portal
    {"title": "Update Profile", "method": "PATCH", "path": "/users/me", "auth_token": "buyer_token", "body": {"phone": "+1234567890"}},
    {"title": "Get Profile", "method": "GET", "path": "/users/me", "auth_token": "buyer_token"},
    
    # Interaction to populate History/Wishlist
    {"title": "Log View (Interaction)", "method": "POST", "path": "/users/interactions/{project_slug}/view", "auth_token": "buyer_token"},
    {"title": "Toggle Wishlist", "method": "POST", "path": "/users/interactions/{project_slug}/wishlist", "auth_token": "buyer_token"},

    {"title": "View History", "method": "GET", "path": "/users/me/history", "auth_token": "buyer_token"},
    {"title": "Get Wishlist", "method": "GET", "path": "/users/me/wishlist", "auth_token": "buyer_token"},
    
    # Landmarks
    # First Admin creates one (not in main user list but in admin list - oh wait, it was in user_portal.py as /admin/landmarks?)
    # Validating: user_portal.py has @router.post("/admin/landmarks").
    {"title": "Create Landmark (Admin)", "method": "POST", "path": "/admin/landmarks", "auth_token": "admin_token", 
     "body": {"name": "Test Landmark", "city": "Bangalore", "latitude": 12.97, "longitude": 77.59, "type": "SCHOOL"},
     "capture": {"id": "landmark_id"}},
     
    {"title": "List Landmarks", "method": "GET", "path": "/public/landmarks"},
    {"title": "Get Landmark", "method": "GET", "path": "/public/landmarks/{landmark_id}"},
    
    # Bookings
    {"title": "Create Visit Booking", "method": "POST", "path": "/users/me/bookings", "auth_token": "buyer_token",
     "body": {"project_id": "{project_id}", "scheduled_time": "2025-12-25T10:00:00", "pickup_location": "Home"}},
    {"title": "List My Bookings", "method": "GET", "path": "/users/me/bookings", "auth_token": "buyer_token"},
    
    # 5. More Interactions
    {"title": "Request Legal", "method": "POST", "path": "/users/interactions/{project_slug}/legal-request", "auth_token": "buyer_token"},
    {"title": "Book Visit (Interaction)", "method": "POST", "path": "/users/interactions/{project_slug}/book-visit", "auth_token": "buyer_token"},
    
    # 6. Developer Projects (Remaining)
    {"title": "Update Project (Direct)", "method": "PUT", "path": "/developers/projects/{project_id}", "auth_token": "dev_token", 
     "body": {"name": f"Proj {rand_suffix} Updated", "slug": f"proj-{rand_suffix}", "description": "Updated", "city": "Bangalore"}},
     
    {"title": "Toggle Visibility", "method": "PATCH", "path": "/developers/projects/{project_id}/hide", "auth_token": "dev_token", "body": {"is_hidden": True}},
    
    # 7. Developer Leads
    {"title": "List Project Leads", "method": "GET", "path": "/developers/leads/projects/{project_slug}/leads", "auth_token": "dev_token",
     "capture": {"[0].id": "lead_id"}}, # Capture first lead
    
    {"title": "Purchase Lead", "method": "PATCH", "path": "/developers/leads/leads/{lead_id}/purchase", "auth_token": "dev_token"},
    {"title": "Update Lead Status", "method": "PATCH", "path": "/developers/leads/leads/{lead_id}/status", "auth_token": "dev_token", "body": {"status": "CONTACTED", "developer_notes": "Called"}},
    {"title": "Developer Dashboard", "method": "GET", "path": "/developers/leads/dashboard", "auth_token": "dev_token"},
    
    # 8. Webhooks
    {"title": "Register Webhook", "method": "POST", "path": "/developers/webhooks/", "auth_token": "dev_token",
     "body": {"url": "https://example.com/hook", "events": ["lead.new"], "secret_token": "sec"},
     "capture": {"id": "webhook_id"}},
    {"title": "List Webhooks", "method": "GET", "path": "/developers/webhooks/", "auth_token": "dev_token"},
    {"title": "Delete Webhook", "method": "DELETE", "path": "/developers/webhooks/{webhook_id}", "auth_token": "dev_token"},
    
    # 9. Developer Team
    {"title": "Invite Team Member", "method": "POST", "path": "/developers/team/invite", "auth_token": "dev_token",
     "body": {"email": f"team_{rand_suffix}@ex.com", "role": "Sales", "permissions": ["leads:view_basic"]},
     "capture": {"id": "team_member_id"}},
    {"title": "List Team", "method": "GET", "path": "/developers/team/", "auth_token": "dev_token"},
    {"title": "Update Member Permissions", "method": "PUT", "path": "/developers/team/{team_member_id}/permissions", "auth_token": "dev_token",
     "body": {"permissions": ["leads:view_basic", "leads:view_full"]}},
    {"title": "Remove Team Member", "method": "DELETE", "path": "/developers/team/{team_member_id}", "auth_token": "dev_token"},
    
    # 10. Developer Subscriptions
    {"title": "List Sub Plans (Dev)", "method": "GET", "path": "/developers/subscriptions/plans", "auth_token": "dev_token"},
    {"title": "Get Current Sub (Dev)", "method": "GET", "path": "/developers/subscriptions/current", "auth_token": "dev_token"},
    # We need a plan ID to purchase. Let's assume seeded or create one later. 
    # Actually, we should create a plan as Admin first? Yes.
    
    # 11. Admin Subscriptions (Do this before purchase)
    {"title": "Create Plan (Admin)", "method": "POST", "path": "/admin/subscriptions/plans", "auth_token": "admin_token",
     "body": {"name": "Pro Plan", "price": 1000, "duration_days": 30, "description": "Pro features", "features": ["leads:unlimited"], "is_active": True},
     "capture": {"id": "plan_id"}},
    {"title": "List Plans (Admin)", "method": "GET", "path": "/admin/subscriptions/plans", "auth_token": "admin_token"},
    
    # Back to Dev Purchase
    {"title": "Purchase Subscription", "method": "POST", "path": "/developers/subscriptions/purchase", "auth_token": "dev_token",
     "body": {"plan_id": "{plan_id}", "payment_method_id": "tok_visa"}},
     
    {"title": "List All Subs (Admin)", "method": "GET", "path": "/admin/subscriptions/subscriptions", "auth_token": "admin_token"},

    # 12. Admin Projects & Change Requests
    {"title": "List All Projects (Admin)", "method": "GET", "path": "/admin/projects/", "auth_token": "admin_token"},
    {"title": "Reject Project (Admin)", "method": "PATCH", "path": "/admin/projects/{project_id}/reject", "auth_token": "admin_token"},
    
    # Change Requests Flow
    # 1. Update Approved Project (as Dev) -> triggers Change Request
    # Re-Approve first (since we rejected it above)
    {"title": "Re-Approve Project (Admin)", "method": "PATCH", "path": "/admin/projects/{project_id}/approve", "auth_token": "admin_token"},
    
    {"title": "Update Approved Project (Dev - Trigger CR)", "method": "PUT", "path": "/developers/projects/{project_id}", "auth_token": "dev_token",
     "body": {"name": "Change Req", "slug": f"proj-{rand_suffix}", "description": "CR Trigger", "city": "Bangalore"},
     "capture": {"request_id": "change_request_id"}}, # Script logic handles nested request_id
    
    # Now Approve/Reject CR
    {"title": "Approve Change Request", "method": "POST", "path": "/admin/projects/{change_request_id}/approve", "auth_token": "admin_token"},
    
    # 13. Admin Developers
    {"title": "Create Developer (Admin)", "method": "POST", "path": "/admin/developers/", "auth_token": "admin_token",
     "body": {"name": "Admin Created Dev", "contact_email": f"dev2_{rand_suffix}@ex.com", "contact_phone": "9998887776", "office_address": "Bangalore"},
     "capture": {"id": "developer_entity_id"}},
    {"title": "List Developers (Admin)", "method": "GET", "path": "/admin/developers/", "auth_token": "admin_token"},
    {"title": "Get Developer (Admin)", "method": "GET", "path": "/admin/developers/{developer_entity_id}", "auth_token": "admin_token"},
    {"title": "Update Developer (Admin)", "method": "PUT", "path": "/admin/developers/{developer_entity_id}", "auth_token": "admin_token", "body": {"name": "Updated Dev Name"}},
    {"title": "Delete Developer (Admin)", "method": "DELETE", "path": "/admin/developers/{developer_entity_id}", "auth_token": "admin_token"},
    
    # 14. Admin Users
    {"title": "Create User (Admin)", "method": "POST", "path": "/admin/users/", "auth_token": "admin_token",
     "body": {"email": f"u2_{rand_suffix}@ex.com", "password": "Pass", "full_name": "Admin User", "role": "BUYER"},
     "capture": {"id": "user_id"}},
    {"title": "List Users (Admin)", "method": "GET", "path": "/admin/users/", "auth_token": "admin_token"},
    {"title": "Get User (Admin)", "method": "GET", "path": "/admin/users/{user_id}", "auth_token": "admin_token"},
    {"title": "Update User (Admin)", "method": "PUT", "path": "/admin/users/{user_id}", "auth_token": "admin_token", "body": {"full_name": "Updated User"}},
    {"title": "Suspend User (Admin)", "method": "PATCH", "path": "/admin/users/{user_id}/suspend", "auth_token": "admin_token"},
    {"title": "Activate User (Admin)", "method": "PATCH", "path": "/admin/users/{user_id}/activate", "auth_token": "admin_token"},
    {"title": "Delete User (Admin)", "method": "DELETE", "path": "/admin/users/{user_id}", "auth_token": "admin_token"},
    
    # 15. Settings
    {"title": "Change Password", "method": "PATCH", "path": "/settings/change-password", "auth_token": "buyer_token", "body": {"old_password": "StrongUserPass123!", "new_password": "NewStrongPass1!"}},
    {"title": "Get My Profile (Settings)", "method": "GET", "path": "/settings/profile", "auth_token": "buyer_token"}
]

def main():
    try:
        get_tokens()
    except Exception as e:
        print(f"Auth failed: {e}")
        return

    results = []
    for i, ep in enumerate(ENDPOINTS, 1):
        try:
            res = run_test(ep, i)
            results.append(res)
        except Exception as e:
            print(f"Error testing {ep['title']}: {e}")
            
    # Generate MD
    md = "# RealStart API Reference\n\n"
    md += f"**Base URL**: `{BASE_URL}`\n\n"
    for res in results:
        md += f"### {res['title']}\n"
        md += f"**URL**: `{res['url']}`\n\n"
        md += "**Success Response**\n"
        md += f"Status: `{res['success']['status']}`\n"
        md += "```bash\n" + res['success']['curl'] + "\n```\n"
        md += "```json\n" + res['success']['json'] + "\n```\n\n"
        md += "**Failure Response**\n"
        md += f"Status: `{res['failure']['status']}`\n"
        md += "```bash\n" + res['failure']['curl'] + "\n```\n"
        md += "```json\n" + res['failure']['json'] + "\n```\n\n"
        md += "---\n\n"
    
    with open(OUTPUT_FILE, "w") as f:
        f.write(md)
    print(f"Generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
