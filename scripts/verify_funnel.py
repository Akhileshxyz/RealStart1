import sys
import os
import asyncio

sys.path.append(os.getcwd())

async def verify():
    print("Verifying Dashboard and Funnel...")
    try:
        from app.api.v1.admin_dashboard import get_admin_dashboard_stats
        from app.api.v1.admin_analytics import get_funnel_analytics, get_site_visits_analytics
        print("PASS: Endpoints imported successfully")
        
        # Check specific model imports used in the new funnel code
        from app.models.lead import ProjectLead
        print("PASS: ProjectLead model imported")
        
        print("Verification Successful!")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify())
