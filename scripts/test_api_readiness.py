import requests
import json
import os
import random
import string
import datetime
import time

BASE_URL = "http://localhost:8000/api/v1"
OUTPUT_FILE = "API_READINESS_REPORT.md"

# Global state to hold tokens and dynamic IDs
CONTEXT = {
    # Users & Tokens
    "admin_token": None,
    "dev_token": None,
    "buyer_token": None,
    "lawyer_token": None,
    
    # Dynamic IDs captured during testing
    "project_id": None,
    "project_slug": None,
    "lead_id": None, 
    "webhook_id": None,
    "team_member_id": None,
    "user_id": None, # For Admin User tests
    "developer_entity_id": None, # For Admin Developer tests
    "change_request_id": None,
    "landmark_id": None, 
    "plan_id": None,
    "video_id": None,
    "legal_call_id": None, # Mock if needed or capture
    "doc_id": "00000000-0000-0000-0000-000000000000" # Placeholder until we have docs
}

rand_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))

def get_tokens():
    print("Authenticating users for all roles...")
    
    # 1. Super Admin (Seeded)
    resp = requests.post(f"{BASE_URL}/admin/login", data={"username": "admin@realstart.com", "password": "admin"}, timeout=10)
    if resp.status_code == 200:
        CONTEXT["admin_token"] = resp.json()["access_token"]
        print("[OK] Admin Authenticated")
    else:
        print(f"[FAIL] Admin Auth Failed: {resp.text}")

    # 2. Register/Login Fresh Developer
    if CONTEXT["admin_token"]:
        dev_email = f"dev_{rand_suffix}@realstart.com"
        dev_pass = "StrongDevPass123!"
        headers = {"Authorization": f"Bearer {CONTEXT['admin_token']}"}
        payload = {"email": dev_email, "password": dev_pass, "full_name": "Fresh Dev", "role": "DEVELOPER"}
        resp = requests.post(f"{BASE_URL}/admin/register-admin", json=payload, headers=headers)
        if resp.status_code in [200, 201]:
            # Login
            l_resp = requests.post(f"{BASE_URL}/admin/login", data={"username": dev_email, "password": dev_pass}, timeout=10)
            if l_resp.status_code == 200:
                CONTEXT["dev_token"] = l_resp.json()["access_token"]
                print(f"[OK] Developer Created & Authenticated ({dev_email})")
            else:
                print("[FAIL] Developer Login Failed")
        else:
            print(f"[FAIL] Developer Creation Failed: {resp.text}")

    # 3. Register/Login Fresh Buyer
    buyer_email = f"buyer_{rand_suffix}@example.com"
    buyer_pass = "StrongUserPass123!"
    resp = requests.post(f"{BASE_URL}/auth/register", json={"email": buyer_email, "password": buyer_pass, "full_name": "Fresh Buyer", "role": "BUYER"}, timeout=10)
    if resp.status_code in [200, 201]:
        l_resp = requests.post(f"{BASE_URL}/auth/login", data={"username": buyer_email, "password": buyer_pass}, timeout=10)
        if l_resp.status_code == 200:
            CONTEXT["buyer_token"] = l_resp.json()["access_token"]
            print(f"[OK] Buyer Created & Authenticated ({buyer_email})")
        else:
             print("[FAIL] Buyer Login Failed")
    else:
        print(f"[FAIL] Buyer Creation Failed: {resp.text}")

    # 4. Create/Login Lawyer (Using Admin to create specialized role)
    if CONTEXT["admin_token"]:
        lawyer_email = f"lawyer_{rand_suffix}@realstart.com"
        lawyer_pass = "StrongLawyerPass123!"
        headers = {"Authorization": f"Bearer {CONTEXT['admin_token']}"}
        # Assuming admin/register-admin or similar allows creating LAWYER role if logic permits, 
        # or we use admin/users/ endpoint to create it.
        # Let's try admin/register-admin first as it seems to handle internal roles
        payload = {"email": lawyer_email, "password": lawyer_pass, "full_name": "Fresh Lawyer", "role": "LAWYER"}
        resp = requests.post(f"{BASE_URL}/admin/register-admin", json=payload, headers=headers)
        if resp.status_code in [200, 201]:
            # Login
            l_resp = requests.post(f"{BASE_URL}/admin/login", data={"username": lawyer_email, "password": lawyer_pass}, timeout=10)
            if l_resp.status_code == 200:
                CONTEXT["lawyer_token"] = l_resp.json()["access_token"]
                print(f"[OK] Lawyer Created & Authenticated ({lawyer_email})")
            else:
                print("[FAIL] Lawyer Login Failed")
        else:
            print(f"[FAIL] Lawyer Creation Failed: {resp.text}")

def resolve_path(path):
    # Resolve captured IDs
    for k, v in CONTEXT.items():
        if isinstance(v, str) and f"{{{k}}}" in path:
            path = path.replace(f"{{{k}}}", v)
    
    # Fallback for unresolved
    if "{" in path:
        # Default UUIDs
        path = path.replace("{project_id}", "00000000-0000-0000-0000-000000000000")
        path = path.replace("{project_slug}", "dummy-slug")
        path = path.replace("{lead_id}", "00000000-0000-0000-0000-000000000000")
        path = path.replace("{webhook_id}", "00000000-0000-0000-0000-000000000000")
        path = path.replace("{team_member_id}", "00000000-0000-0000-0000-000000000000")
        path = path.replace("{user_id}", "00000000-0000-0000-0000-000000000000")
        path = path.replace("{developer_entity_id}", "00000000-0000-0000-0000-000000000000")
        path = path.replace("{change_request_id}", "00000000-0000-0000-0000-000000000000")
        path = path.replace("{landmark_id}", "00000000-0000-0000-0000-000000000000")
        path = path.replace("{video_id}", "00000000-0000-0000-0000-000000000000")
        path = path.replace("{doc_id}", "00000000-0000-0000-0000-000000000000")
        path = path.replace("{plan_id}", "00000000-0000-0000-0000-000000000000")
        path = path.replace("{request_id}", "00000000-0000-0000-0000-000000000000")
        
    return f"{BASE_URL}{path}"

def resolve_body(body):
    if not body: return None
    if isinstance(body, dict):
        new_body = body.copy()
        for k, v in new_body.items():
            if isinstance(v, str):
                for ctx_k, ctx_v in CONTEXT.items():
                    if isinstance(ctx_v, str) and f"{{{ctx_k}}}" in v:
                        v = v.replace(f"{{{ctx_k}}}", ctx_v)
                new_body[k] = v
        return new_body
    return body

def run_test(ep, index):
    url = resolve_path(ep['path'])
    method = ep['method']
    token_key = ep.get("auth_token")
    
    headers = {}
    if token_key and CONTEXT.get(token_key):
        headers["Authorization"] = f"Bearer {CONTEXT[token_key]}"
    
    raw_body = ep.get("body")
    body = resolve_body(raw_body)
    is_form = ep.get("is_form", False)
    
    # Construct Request
    if is_form:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        resp = requests.request(method, url, headers=headers, data=body, timeout=10)
    else:
        if body is not None:
             headers["Content-Type"] = "application/json"
        
        # Unique constraints fix (slugs etc)
        if ep['title'] == "Create Project" and body:
             body['slug'] = f"proj-{rand_suffix}" 
        if ep['title'] == "Update Project (Trigger CR)" and body:
             body['slug'] = f"proj-cr-{rand_suffix}"

        resp = requests.request(method, url, headers=headers, json=body, timeout=10)
        
    status = resp.status_code
    is_success = status in [200, 201]
    
    # Capture Data on Success
    if is_success and ep.get("capture"):
        try:
            data = resp.json()
            for path_key, ctx_key in ep["capture"].items():
                val = None
                if path_key.startswith("[0]"):
                    # List handling
                    if isinstance(data, list) and len(data) > 0:
                        sub_key = path_key.replace("[0].", "")
                        val = data[0].get(sub_key)
                else:
                    # Dict handling
                    val = data.get(path_key)
                    # Backup check for nested keys like request_id which might be at root
                    if val is None and path_key in data:
                        val = data[path_key]

                if val:
                    CONTEXT[ctx_key] = str(val)
                    # print(f"   > Captured {ctx_key}: {val}")
        except:
            pass

    # Simplified Response for Report
    try:
        resp_json = resp.json()
        resp_snippet = json.dumps(resp_json)[:200] + "..." if len(str(resp_json)) > 200 else json.dumps(resp_json)
    except:
        resp_snippet = resp.text[:200]

    return {
        "id": index,
        "title": ep["title"],
        "method": method,
        "url": url,
        "role": token_key.replace("_token", "").upper() if token_key else "PUBLIC",
        "status": status,
        "success": is_success,
        "response_snippet": resp_snippet
    }

# -------------------------- ENDPOINTS DEFINITION --------------------------
ENDPOINTS = [
    # --- 1. Authenticaton & Public ---
    {"title": "Register Public User", "method": "POST", "path": "/auth/register", "body": {"email": f"b2_{rand_suffix}@ex.com", "password": "StrongPass123!", "full_name": "Test", "role": "BUYER"}},
    {"title": "Login Public User", "method": "POST", "path": "/auth/login", "is_form": True, "body": {"username": f"buyer_{rand_suffix}@example.com", "password": "StrongUserPass123!"}},
    {"title": "Get My Profile", "method": "GET", "path": "/auth/me", "auth_token": "buyer_token"},

    # --- 2. Developer Flow (Project Creation) ---
    {"title": "Create Project", "method": "POST", "path": "/developers/projects/", "auth_token": "dev_token", 
     "body": {"name": f"Project {rand_suffix}", "slug": f"proj-{rand_suffix}", "description": "Desc", "city": "Bangalore", "developer_id": "00000000-0000-0000-0000-000000000000"},
     "capture": {"id": "project_id", "slug": "project_slug"}},
    {"title": "List My Projects", "method": "GET", "path": "/developers/projects/my-projects", "auth_token": "dev_token"},
    
    # --- 3. Admin Project Approval ---
    {"title": "Approve Project (Admin)", "method": "PATCH", "path": "/admin/projects/{project_id}/approve", "auth_token": "admin_token"},
    {"title": "List All Projects (Admin)", "method": "GET", "path": "/admin/projects/", "auth_token": "admin_token"},
    
    # --- 4. Public Access (Now valid) ---
    {"title": "List Public Projects", "method": "GET", "path": "/public/projects/"},
    {"title": "Get Project by Slug", "method": "GET", "path": "/public/projects/{project_slug}"},

    # --- 5. User Interactions ---
    {"title": "Log View", "method": "POST", "path": "/users/interactions/{project_slug}/view", "auth_token": "buyer_token"},
    {"title": "Toggle Wishlist", "method": "POST", "path": "/users/interactions/{project_slug}/wishlist", "auth_token": "buyer_token"},
    {"title": "View History", "method": "GET", "path": "/users/me/history", "auth_token": "buyer_token"},
    {"title": "Get Wishlist", "method": "GET", "path": "/users/me/wishlist", "auth_token": "buyer_token"},
    {"title": "Book Visit", "method": "POST", "path": "/users/me/bookings", "auth_token": "buyer_token",
     "body": {"project_id": "{project_id}", "scheduled_time": "2025-12-25T10:00:00", "pickup_location": "Home"}},
    
    # --- 6. Admin Landmarks ---
    {"title": "Create Landmark (Admin)", "method": "POST", "path": "/admin/landmarks/", "auth_token": "admin_token", 
     "body": {"name": f"Landmark {rand_suffix}", "city": "Bangalore", "latitude": 12.97, "longitude": 77.59, "type": "SCHOOL"},
     "capture": {"id": "landmark_id"}},
    {"title": "List Landmarks (Admin)", "method": "GET", "path": "/admin/landmarks/", "auth_token": "admin_token"},
    {"title": "Update Landmark", "method": "PUT", "path": "/admin/landmarks/{landmark_id}", "auth_token": "admin_token", "body": {"name": f"Landmark Updated {rand_suffix}"}},
    
    # --- 7. Locality Intelligence (Public) ---
    {"title": "Resolve Locality", "method": "POST", "path": "/locality/resolve", 
     "body": {"place_name": "Indiranagar", "latitude": 12.9784, "longitude": 77.6408}},
    # We can try to use captured landmark_id but let's test the public list too if available.
    # Actually public landmarks list is in public_projects? No, main.py says /public/landmarks... wait, check main.py again.
    # Ah, User Portal Router usually has public/landmarks. Let's assume it exists or use Admin created one.
    {"title": "Get Locality Details", "method": "GET", "path": "/locality/{landmark_id}"}, # Public
    {"title": "Get Price Insights", "method": "GET", "path": "/locality/price-insights?landmark_id={landmark_id}"}, # Note: parameter passing might be query param? 
    # Viewing locality.py: @router.get("/{landmark_id}") is detail.
    # @router.get("/price-insights") expects landmark_id? No, look at code: 
    # @router.get("/price-insights", response_model=Any) async def get_price_insights(landmark_id: UUID)
    # This implies query param in FastAPI default if not in path.
    # Let's fix the path to use query param format if needed, OR the router might be nested?
    # Actually code was: @router.get("/price-insights")... def get_price_insights(landmark_id: UUID).
    # This means ?landmark_id=... is correct.
    
    # --- 8. Admin Ads ---
    {"title": "Create Internal Ad", "method": "POST", "path": "/admin/ads/internal", "auth_token": "admin_token",
     "body": {"title": "Promo", "image_url": "http://img", "target_url": "http://site", "start_date": "2025-01-01", "end_date": "2025-01-10"}},
    {"title": "List Internal Ads", "method": "GET", "path": "/admin/ads/internal", "auth_token": "admin_token"},
    {"title": "Get Meta Ads Info", "method": "GET", "path": "/admin/ads/meta", "auth_token": "admin_token"},

    # --- 9. Admin Analytics & Dashboard ---
    {"title": "Get Admin Dashboard", "method": "GET", "path": "/admin/dashboard", "auth_token": "admin_token"},
    {"title": "Get Growth Analytics", "method": "GET", "path": "/admin/analytics/growth", "auth_token": "admin_token"},
    {"title": "Get Demographics", "method": "GET", "path": "/admin/analytics/demographics", "auth_token": "admin_token"},
    
    # --- 10. Admin Team ---
    {"title": "Create Team Member", "method": "POST", "path": "/admin/team/", "auth_token": "admin_token",
     "body": {"email": f"sales_{rand_suffix}@realstart.com", "password": "StrongTeamPass123!", "full_name": "Sales Guy", "role": "SALES"},
     "capture": {"id": "team_member_id"}},
    {"title": "List Team Members", "method": "GET", "path": "/admin/team/", "auth_token": "admin_token"},
    {"title": "Assign Task", "method": "POST", "path": "/admin/team/{team_member_id}/tasks", "auth_token": "admin_token",
     "body": {"title": "Call Leads", "description": "Urgent", "due_date": "2025-12-30", "priority": "HIGH"}},
    
    # --- 11. Admin Videos ---
    {"title": "Upload Video Meta", "method": "POST", "path": "/admin/videos/", "auth_token": "admin_token",
     "body": {"title": "Intro", "url": "http://vid", "duration_seconds": 60, "format": "mp4"},
     "capture": {"id": "video_id"}},
    {"title": "List Videos", "method": "GET", "path": "/admin/videos/", "auth_token": "admin_token"},
    
    # --- 12. Developer Leads & Webhooks ---
    {"title": "List Leads (Dev)", "method": "GET", "path": "/developers/leads/projects/{project_slug}/leads", "auth_token": "dev_token"},
    # Need to have a lead first? Leads are created via Interactions or manually? 
    # Usually logged via interaction.
    {"title": "Register Webhook", "method": "POST", "path": "/developers/webhooks/", "auth_token": "dev_token",
     "body": {"url": "https://hook.site", "events": ["lead.new"], "secret_token": "xy"},
     "capture": {"id": "webhook_id"}},
    
    # --- 13. Lawyer Portal ---
    # Need to simulate a document existing? Create project creates docs automatically? 
    # If not, list might be empty.
    {"title": "List Incoming Items (Lawyer)", "method": "GET", "path": "/lawyer/incoming-items", "auth_token": "lawyer_token"},
    {"title": "List Legal Calls (Lawyer)", "method": "GET", "path": "/lawyer/legal-calls", "auth_token": "lawyer_token"},
    
    # --- 14. Admin Subscriptions ---
    {"title": "Create Plan", "method": "POST", "path": "/admin/subscriptions/plans", "auth_token": "admin_token",
     "body": {"name": "Test Plan", "price": 999, "duration_days": 30, "features": {"all": True}, "is_active": True},
     "capture": {"id": "plan_id"}},
    {"title": "List Plans", "method": "GET", "path": "/admin/subscriptions/plans", "auth_token": "admin_token"},
    
    # --- 15. Developer Purchase Subscription ---
    {"title": "Purchase Sub", "method": "POST", "path": "/developers/subscriptions/purchase", "auth_token": "dev_token",
     "body": {"plan_id": "{plan_id}", "payment_method_id": "pm_card_visa"}},
     
    # --- 16. Admin Change Request ---
    # Trigger CR
    {"title": "Update Project (Trigger CR)", "method": "PUT", "path": "/developers/projects/{project_id}", "auth_token": "dev_token",
     "body": {"name": "Changed Name", "description": "Changed"},
     "capture": {"request_id": "change_request_id"}},
    {"title": "View Change Requests (Admin)", "method": "GET", "path": "/admin/projects/change-requests/", "auth_token": "admin_token"},
    # Warning: The path might be different, checking admin_change_requests.py...
    # It says @router... but prefix in main.py is /admin/projects. 
    # If admin_change_requests.py has @router.get("/change-requests"), then path is /admin/projects/change-requests.
    # If it has @router.get("/requests"), then /admin/projects/requests.
    # Assumption: /admin/projects/change-requests based on common naming or verify later. 
    # Validating file content of admin_change_requests.py... (I did not read it fully, only listed dir).
    # Let's assume standard REST. If fails, we'll know.
    
    {"title": "Approve CR", "method": "POST", "path": "/admin/projects/change-requests/{change_request_id}/approve", "auth_token": "admin_token"}
]

def main():
    print("----------------------------------------------------------------")
    print("  REALSTART API READINESS TEST")
    print("  Time: " + str(datetime.datetime.now()))
    print("----------------------------------------------------------------\n")
    
    # 1. Auth
    try:
        get_tokens()
    except Exception as e:
        print(f"FATAL: Critical Auth Failure - {e}")
        return

    # 2. Run Tests
    results = []
    print("\nRunning Endpoint Tests...\n")
    
    for i, ep in enumerate(ENDPOINTS, 1):
        try:
            res = run_test(ep, i)
            status_tag = "[PASS]" if res['success'] else "[FAIL]"
            print(f"{i}. {status_tag} {ep['title']} ({res['status']})")
            results.append(res)
        except Exception as e:
            print(f"{i}. [ERR] {ep['title']} - {e}")
            results.append({
                "id": i, "title": ep['title'], "method": ep['method'], "url": "N/A", 
                "role": "N/A", "status": 0, "success": False, "response_snippet": str(e)
            })

    # 3. Report Generation
    total = len(results)
    passed = len([r for r in results if r['success']])
    failed = total - passed
    score = (passed / total) * 100 if total > 0 else 0
    readiness = "READY" if score > 90 else "NEEDS WORK"
    
    md = f"# API Readiness Report\n\n"
    md += f"**Date:** {datetime.datetime.now()}\n"
    md += f"**Overall Status:** {readiness} ({score:.1f}% Passing)\n"
    md += f"**Total Endpoints Tested:** {total}\n"
    md += f"**Passed:** {passed} | **Failed:** {failed}\n\n"
    
    md += "## Detailed Results\n| ID | Title | Method | Role | Status | Result | Payload Snippet |\n|---|---|---|---|---|---|---|\n"
    for r in results:
        icon = "✅" if r['success'] else "❌"
        # Escaping pipes in snippet
        clean_snip = r['response_snippet'].replace("|", "\|").replace("\n", " ")
        md += f"| {r['id']} | {r['title']} | {r['method']} | {r['role']} | {r['status']} | {icon} | `{clean_snip}` |\n"
        
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(md)
        
    print(f"\n----------------------------------------------------------------")
    print(f"Report Generated: {OUTPUT_FILE}")
    print(f"Score: {score:.1f}%")
    print("----------------------------------------------------------------")

if __name__ == "__main__":
    main()
