
import sys
import os
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

# Add app to path
sys.path.append(os.getcwd())

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.subscription import SubscriptionPlan, DeveloperSubscription, SubscriptionStatus
from app.core.security import create_access_token

# Mock Redis
from app.core.redis_client import redis_client
redis_client.client = MagicMock()
redis_client.get = AsyncMock(return_value=None)
redis_client.set = AsyncMock()

async def setup_db_and_test():
    from app.db.mongodb import init_db
    await init_db()

    # Create Dev User
    dev_email = "test_razorpay_dev@example.com"
    dev = await User.find_one(User.email == dev_email)
    if not dev:
        dev = User(email=dev_email, hashed_password="pw", full_name="Test Dev", role=UserRole.DEVELOPER)
        await dev.insert()
    
    # Create Plan
    plan = await SubscriptionPlan.find_one(SubscriptionPlan.name == "Razorpay Test Plan")
    if not plan:
        plan = SubscriptionPlan(name="Razorpay Test Plan", duration_days=30, price=999.0, features={})
        await plan.insert()

    # Generate Token
    token = create_access_token(str(dev.id))
    headers = {"Authorization": f"Bearer {token}"}

    # Use AsyncClient
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        
        # PATCH Razorpay Client
        with patch("app.api.v1.developer_subscriptions.razorpay_client") as mock_razorpay:
            # Mock Order Create
            mock_order = {"id": "order_mock_123", "amount": 99900, "currency": "INR"}
            mock_razorpay.order.create.return_value = mock_order
            
            # Mock Verify Signature
            mock_razorpay.utility.verify_payment_signature.return_value = None

            print("--- Testing Create Order ---")
            resp = await ac.post("/api/v1/developers/subscriptions/orders", 
                               json={"plan_id": str(plan.id)},
                               headers=headers)
            
            if resp.status_code == 200:
                print("Order Created:", resp.json())
                order_id = resp.json()["order_id"]
                assert order_id == "order_mock_123"
            else:
                print("Order Failed:", resp.text)
                return

            print("\n--- Testing Verify Payment ---")
            verify_payload = {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": "pay_mock_abc",
                "razorpay_signature": "sig_mock_xyz"
            }
            
            resp = await ac.post("/api/v1/developers/subscriptions/verify",
                               json=verify_payload,
                               headers=headers)
            
            if resp.status_code == 200:
                print("Verification Success:", resp.json())
                sub_data = resp.json()
                assert sub_data["status"] == "ACTIVE"
                print("Subscription Logic Verified!")
            else:
                print("Verification Failed:", resp.text)

if __name__ == "__main__":
    asyncio.run(setup_db_and_test())
