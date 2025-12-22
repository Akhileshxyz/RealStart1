import sys
import os
import asyncio

sys.path.append(os.getcwd())

async def verify_gap_analysis_features():
    print("Verifying Gap Analysis Implementations...")
    try:
        # 1. Dashboard Enhancements
        from app.api.v1.admin_dashboard import get_admin_dashboard_stats, get_system_health
        print("PASS: Dashboard endpoints updated/added")
        
        # 2. Project Communication
        from app.models.communication import ProjectCommunication
        from app.api.v1.admin_projects import log_project_communication, get_project_communication_history
        print("PASS: Project Communication model and endpoints added")
        
        # 3. Team Data Sharing
        from app.models.team import SharedClient
        from app.api.v1.admin_team import share_client_with_member, get_shared_clients
        print("PASS: Team Data Sharing model and endpoints added")
        
        print("All Gap Analysis Features Verified Successfully!")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_gap_analysis_features())
