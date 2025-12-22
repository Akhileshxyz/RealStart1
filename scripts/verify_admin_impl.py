import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.getcwd())

async def verify_imports():
    print("Verifying imports...")
    try:
        from app.main import app
        print("PASS app.main imported successfully")
        
        # explicit check for new modules
        from app.api.v1 import (
            admin_dashboard,
            admin_analytics,
            admin_ads,
            admin_team,
            admin_landmarks,
            admin_videos,
            developers,
            admin_subscriptions
        )
        print("PASS New admin modules imported successfully")
        
        from app.models.ad import Ad
        from app.models.team import StaffTask
        from app.models.user import Gender 
        from app.models.video import Video
        print("PASS New models imported successfully")

        # Check developers enhancements
        from app.api.v1.developers import impersonate_developer, get_developer_projects_by_location
        print("PASS Developer endpoints imported successfully")
        
        # Check subscription enhancements
        from app.api.v1.admin_subscriptions import get_expiring_subscriptions, get_subscription_revenue
        print("PASS Subscription endpoints imported successfully")
        
        print("All verification checks passed!")
    except Exception as e:
        print(f"FAILED Verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_imports())
