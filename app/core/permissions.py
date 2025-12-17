from enum import Enum

class TeamProjectsPermission(str, Enum):
    VIEW_PROJECTS = "projects:view"
    EDIT_PROJECTS = "projects:edit"
    
class TeamLeadsPermission(str, Enum):
    VIEW_LEADS_BASIC = "leads:view_basic" # Name redacted?
    VIEW_LEADS_FULL = "leads:view_full"   # Name, email, phone visible
    MANAGE_LEADS = "leads:manage"         # Update status, add notes

class TeamVisitsPermission(str, Enum):
    VIEW_VISITS = "visits:view"
    MANAGE_VISITS = "visits:manage"       # Reschedule, Cancel

class TeamDashboardPermission(str, Enum):
    VIEW_DASHBOARD = "dashboard:view"

# Aggregated list for validation
ALL_PERMISSIONS = {
    *[p.value for p in TeamProjectsPermission],
    *[p.value for p in TeamLeadsPermission],
    *[p.value for p in TeamVisitsPermission],
    *[p.value for p in TeamDashboardPermission],
}
