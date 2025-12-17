import asyncio
import httpx
from uuid import uuid4

BASE_URL = "http://localhost:8000/api/v1"

# Utils
async def login(client, email, password):
    resp = await client.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    if resp.status_code != 200:
        print(f"Login failed for {email}: {resp.text}")
        return None
    return resp.json()["access_token"]

async def run_verification():
    async with httpx.AsyncClient() as client:
        print("--- JOINING REALSTART VERIFICATION ---")
        
        # 1. Setup Users
        dev_email = f"dev_{uuid4().hex[:6]}@example.com"
        admin_email = "admin@realstart.com" # Assuming exists or we create
        password = "Password123!"
        
        # Register Developer
        print(f"\n[1] Registering Developer: {dev_email}")
        resp = await client.post(f"{BASE_URL}/auth/register", json={
            "email": dev_email, "password": password, "full_name": "Test Dev", "phone": "1234567890", "role": "DEVELOPER"
        })
        if resp.status_code != 200:
            print(f"Registration failed: {resp.text}")
            # If exists, try login
        
        dev_token = await login(client, dev_email, password)
        headers = {"Authorization": f"Bearer {dev_token}"}
        
        # 2. Test Project Limits (Default: 1)
        print("\n[2] Testing Default Subscription Limits")
        
        # Create Project 1 (Should Succeed)
        slug1 = f"proj-{uuid4().hex[:6]}"
        print(f"Creating Project 1 ({slug1})...")
        resp = await client.post(f"{BASE_URL}/developers/projects/", json={
            "name": "Project 1", "slug": slug1, "developer_id": str(uuid4()) # ID ignored by logic usually
        }, headers=headers)
        if resp.status_code == 200:
            print("✅ Project 1 Created")
            proj1_id = resp.json()["id"]
        else:
            print(f"❌ Project 1 Failed: {resp.text}")
            return

        # Create Project 2 (Should Fail - Limit 1)
        slug2 = f"proj-{uuid4().hex[:6]}"
        print(f"Creating Project 2 ({slug2}) [Expected Failure]...")
        resp = await client.post(f"{BASE_URL}/developers/projects/", json={
            "name": "Project 2", "slug": slug2
        }, headers=headers)
        if resp.status_code == 403:
            print(f"✅ Blocked Correctly: {resp.json()['detail']}")
        else:
            print(f"❌ Limits Failed! Code: {resp.status_code}")

        # Invite Team Member (Should Fail - Limit 0)
        print("Inviting Team Member [Expected Failure]...")
        resp = await client.post(f"{BASE_URL}/developers/team/invite", json={
            "email": "sales@team.com", "role": "Sales", "permissions": ["leads:view_basic"]
        }, headers=headers)
        if resp.status_code == 403:
             print(f"✅ Blocked Correctly: {resp.json()['detail']}")
        else:
             print(f"❌ Limits Failed! Code: {resp.status_code}")

        # 3. Upgrade Plan
        # Login as Admin (Need valid admin creds, usually setup in seeding)
        # For this test, we might fail if admin doesn't exist.
        # Let's assume we can register an admin or use one.
        # Workaround: Use existing admin token if known, or register new generic one if allowed (unlikely).
        # We'll try registering a Super Admin just in case (usually blocked).
        # If we can't be admin, we can't Create Plan. 
        # But we can verify strict enforcement which is good.
        
        # NOTE: If verification stops here, it proves Limits work.
        # To test upgrade, we'd need Admin access.
        
        # 4. Test Visibility (On Project 1)
        print("\n[3] Testing Visibility Toggle")
        print("Hiding Project 1...")
        resp = await client.patch(f"{BASE_URL}/developers/projects/{proj1_id}/hide", json={"is_hidden": True}, headers=headers)
        if resp.status_code == 200 and resp.json()["is_hidden"]:
            print("✅ Project Hidden")
        else:
            print(f"❌ Hide Failed: {resp.text}")

        print("--- VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(run_verification())
