import asyncio
import httpx
from app.core.config import settings

# Configuration
BASE_URL = f"http://localhost:8000{settings.API_V1_STR}"
ADMIN_EMAIL = "admin@realstart.com"
ADMIN_PASSWORD = "admin"

async def verify_rbac():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # 1. Login as Admin
        print("1. Logging in as Admin...")
        login_data = {
            "username": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        response = await client.post("/auth/login", data=login_data)
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return
        
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print("   Login successful.")

        # 2. Create a Test User (Buyer)
        print("\n2. Creating Test User (Buyer)...")
        test_user_email = "test_buyer_rbac@example.com"
        user_data = {
            "email": test_user_email,
            "password": "password123",
            "full_name": "Test Buyer",
            "role": "BUYER"
        }
        
        # Check if exists and delete first if needed (cleanup from previous runs)
        # But we need ID to delete, so we rely on create failure or just try create
        
        response = await client.post("/admin/users/", json=user_data, headers=headers)
        if response.status_code == 400 and "already exists" in response.text:
            print("   User already exists. Skipping create.")
            # Get the user to proceed
            users_res = await client.get("/admin/users/", headers=headers)
            users = users_res.json()
            created_user = next((u for u in users if u["email"] == test_user_email), None)
        elif response.status_code == 200:
            created_user = response.json()
            print(f"   User created: {created_user['id']}")
        else:
            print(f"   Failed to create user: {response.text}")
            return

        user_id = created_user["id"]

        # 3. Read User
        print("\n3. Reading User details...")
        response = await client.get(f"/admin/users/{user_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["role"] == "BUYER"
        print("   User details verified.")

        # 4. Update User Role (to MANAGER)
        print("\n4. Updating User Role to MANAGER...")
        update_data = {
            "role": "MANAGER",
            "full_name": "Test Manager"
        }
        response = await client.put(f"/admin/users/{user_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["role"] == "MANAGER"
        assert updated_user["full_name"] == "Test Manager"
        print("   User role updated verified.")

        # 5. Suspend User
        print("\n5. Suspending User...")
        response = await client.patch(f"/admin/users/{user_id}/suspend", headers=headers)
        assert response.status_code == 200
        assert response.json()["is_active"] == False
        print("   User suspended.")

        # 6. Delete User
        print("\n6. Deleting User...")
        response = await client.delete(f"/admin/users/{user_id}", headers=headers)
        assert response.status_code == 200
        print("   User deleted.")

        # 7. Verify Deletion
        print("\n7. Verifying Deletion...")
        response = await client.get(f"/admin/users/{user_id}", headers=headers)
        assert response.status_code == 404
        print("   User successfully removed.")
        
        print("\n✅ RBAC Verification Complete: Success!")

if __name__ == "__main__":
    try:
        asyncio.run(verify_rbac())
    except ImportError:
        print("httpx not installed. Please install it: pip install httpx")
    except Exception as e:
        print(f"Verification Failed: {e}")
