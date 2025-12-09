import asyncio
import httpx
from uuid import uuid4
from app.core.config import settings

BASE_URL = f"http://localhost:8000{settings.API_V1_STR}"
ADMIN_EMAIL = "admin@realstart.com"
ADMIN_PASSWORD = "admin"

async def verify_project_workflow():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        print("🚀 Starting Project Verification Workflow...")

        # 1. Login as Admin
        print("\n1. Logging in as Admin...")
        resp = await client.post("/auth/login", data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        assert resp.status_code == 200
        admin_token = resp.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print("   ✅ Admin logged in")

        # 2. Create a Developer User (Using Admin API)
        print("\n2. Creating Developer User...")
        dev_email = f"dev_{uuid4().hex[:8]}@example.com"
        dev_password = "password123"
        dev_data = {
            "email": dev_email,
            "password": dev_password,
            "full_name": "Test Developer",
            "role": "DEVELOPER"
        }
        resp = await client.post("/admin/users/", json=dev_data, headers=admin_headers)
        if resp.status_code == 400: # Already exists
            pass
        else:
            assert resp.status_code == 200
        print("   ✅ Developer User Created")

        # 3. Login as Developer
        print("\n3. Logging in as Developer...")
        resp = await client.post("/auth/login", data={"username": dev_email, "password": dev_password})
        assert resp.status_code == 200, f"Dev login failed: {resp.text}"
        dev_token = resp.json()["access_token"]
        dev_headers = {"Authorization": f"Bearer {dev_token}"}
        print("   ✅ Developer logged in")

        # 4. Create a Project (Status should be PENDING)
        print("\n4. Developer creating a Project...")
        project_slug = f"luxury-homes-{uuid4().hex[:6]}"
        project_data = {
            "name": "Luxury Homes",
            "slug": project_slug,
            "description": "High end villas",
            "address": "123 Rich St",
            "developer_id": str(uuid4())
        }
        resp = await client.post("/developers/projects/", json=project_data, headers=dev_headers)
        assert resp.status_code == 200, f"Create project failed: {resp.text}"
        project_id = resp.json()["id"]
        status = resp.json()["status"]
        assert status == "PENDING"
        print(f"   ✅ Project created. Status: {status}")

        # 5. Public User Checks (Should NOT see it)
        print("\n5. Public User checking for project...")
        resp = await client.get("/public/projects/")
        projects = resp.json()
        found = any(p["slug"] == project_slug for p in projects)
        assert not found, "Project should NOT be visible to public yet"
        
        resp = await client.get(f"/public/projects/{project_slug}")
        assert resp.status_code == 404, "Direct link should also 404"
        print("   ✅ Project NOT visible to public")

        # 6. Admin Approves Project
        print("\n6. Admin approving project...")
        resp = await client.patch(f"/admin/projects/{project_id}/approve", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "APPROVED"
        print("   ✅ Project Approved")

        # 7. Public User Checks (Should SEE it)
        print("\n7. Public User checking again...")
        resp = await client.get("/public/projects/")
        projects = resp.json()
        found = any(p["slug"] == project_slug for p in projects)
        assert found, "Project SHOULD be visible now"
        
        resp = await client.get(f"/public/projects/{project_slug}")
        assert resp.status_code == 200
        print("   ✅ Project IS visible to public")
        
        print("\n🎉 Verification Workflow SUCCESS!")

if __name__ == "__main__":
    asyncio.run(verify_project_workflow())
