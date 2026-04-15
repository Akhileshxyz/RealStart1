"""
Test script for Admin Subscription APIs
Run this to verify the new subscription endpoints work correctly
"""
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# Add the app directory to the path
sys.path.insert(0, 'f:/github/Realstart')

from app.models.subscription import SubscriptionPlan, DeveloperSubscription, SubscriptionStatus
from app.models.developer import Developer
from app.models.user import User, UserRole
from app.db.mongodb import init_db


async def test_subscription_apis():
    """Test the subscription API functionality"""
    
    print("🚀 Testing Admin Subscription APIs\n")
    
    # Initialize database
    print("1. Initializing database...")
    await init_db()
    print("✅ Database initialized\n")
    
    # Test 1: Create test data
    print("2. Creating test data...")
    
    # Create a test plan
    test_plan = SubscriptionPlan(
        name="Test Annual Plan",
        duration_days=365,
        price=25000.0,
        features={"max_projects": 10, "team_access": True},
        is_active=True
    )
    await test_plan.insert()
    print(f"✅ Created test plan: {test_plan.name} (₹{test_plan.price})")
    
    # Create a test developer
    test_developer = Developer(
        name="Test Developer Inc",
        legal_name="Test Developer Private Limited",
        owner_name="Test Owner",
        contact_email="test@developer.com",
        contact_phone="+91-9876543210",
        is_verified=True,
        is_active=True
    )
    await test_developer.insert()
    print(f"✅ Created test developer: {test_developer.name}")
    
    # Create a test user linked to developer
    test_user = User(
        email="testdev@example.com",
        hashed_password="test_hash",
        full_name="Test Developer",
        role=UserRole.DEVELOPER,
        developer_id=test_developer.id,
        is_active=True
    )
    await test_user.insert()
    print(f"✅ Created test user: {test_user.email}")
    
    # Create test subscriptions
    now = datetime.now(timezone.utc)
    
    # Active subscription
    active_sub = DeveloperSubscription(
        developer_id=test_developer.id,
        plan_id=test_plan.id,
        start_date=now - timedelta(days=30),
        end_date=now + timedelta(days=335),  # 335 days left
        status=SubscriptionStatus.ACTIVE,
        auto_renewal=True
    )
    await active_sub.insert()
    print(f"✅ Created active subscription")
    
    # Expiring soon subscription
    expiring_sub = DeveloperSubscription(
        developer_id=test_developer.id,
        plan_id=test_plan.id,
        start_date=now - timedelta(days=360),
        end_date=now + timedelta(days=5),  # Expires in 5 days
        status=SubscriptionStatus.ACTIVE,
        auto_renewal=False
    )
    await expiring_sub.insert()
    print(f"✅ Created expiring subscription (5 days left)")
    
    # Expired subscription
    expired_sub = DeveloperSubscription(
        developer_id=test_developer.id,
        plan_id=test_plan.id,
        start_date=now - timedelta(days=395),
        end_date=now - timedelta(days=30),  # Expired 30 days ago
        status=SubscriptionStatus.EXPIRED,
        auto_renewal=False
    )
    await expired_sub.insert()
    print(f"✅ Created expired subscription\n")
    
    # Test 2: Calculate statistics
    print("3. Testing statistics calculation...")
    
    all_subs = await DeveloperSubscription.find_all().to_list()
    plans = await SubscriptionPlan.find_all().to_list()
    plan_price_map = {p.id: p.price for p in plans}
    
    total_active = 0
    expiring_soon = 0
    expired = 0
    total_revenue = 0.0
    
    seven_days_later = now + timedelta(days=7)
    
    for sub in all_subs:
        price = plan_price_map.get(sub.plan_id, 0.0)
        
        if sub.status == SubscriptionStatus.ACTIVE:
            total_active += 1
            total_revenue += price
            
            end_date_aware = sub.end_date.replace(tzinfo=timezone.utc) if sub.end_date.tzinfo is None else sub.end_date
            if end_date_aware <= seven_days_later:
                expiring_soon += 1
        
        elif sub.status == SubscriptionStatus.EXPIRED:
            expired += 1
            total_revenue += price
    
    print(f"✅ Statistics calculated:")
    print(f"   - Total Active: {total_active}")
    print(f"   - Expiring Soon: {expiring_soon}")
    print(f"   - Expired: {expired}")
    print(f"   - Total Revenue: ₹{total_revenue:,.2f}\n")
    
    # Test 3: Detailed subscription info
    print("4. Testing detailed subscription info...")
    
    active_subs = await DeveloperSubscription.find({"status": SubscriptionStatus.ACTIVE}).to_list()
    
    for sub in active_subs:
        developer = await Developer.get(sub.developer_id)
        user = await User.find_one({"developer_id": sub.developer_id})
        plan = plan_price_map.get(sub.plan_id, 0.0)
        
        end_date_aware = sub.end_date.replace(tzinfo=timezone.utc) if sub.end_date.tzinfo is None else sub.end_date
        days_left = (end_date_aware - now).days
        
        print(f"✅ Subscription Details:")
        print(f"   - Developer: {developer.name if developer else 'Unknown'}")
        print(f"   - Email: {user.email if user else 'N/A'}")
        print(f"   - Plan: {test_plan.name}")
        print(f"   - Price: ₹{test_plan.price:,.2f}")
        print(f"   - Days Left: {days_left}")
        print(f"   - Status: {sub.status}")
        print(f"   - Auto Renewal: {sub.auto_renewal}")
        print()
    
    # Cleanup test data
    print("5. Cleaning up test data...")
    await active_sub.delete()
    await expiring_sub.delete()
    await expired_sub.delete()
    await test_user.delete()
    await test_developer.delete()
    await test_plan.delete()
    print("✅ Test data cleaned up\n")
    
    print("🎉 All tests completed successfully!")
    print("\n📝 Next Steps:")
    print("1. Start your FastAPI server: uvicorn app.main:app --reload")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Test the endpoints:")
    print("   - GET /api/v1/admin/subscriptions/stats")
    print("   - GET /api/v1/admin/subscriptions/details")
    print("   - GET /api/v1/admin/subscriptions/details?status=ACTIVE")


if __name__ == "__main__":
    asyncio.run(test_subscription_apis())
