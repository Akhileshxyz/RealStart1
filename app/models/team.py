from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Optional
from enum import Enum
from beanie import Document
from pydantic import Field

class DeveloperTeamMember(Document):
    id: UUID = Field(default_factory=uuid4)
    developer_id: UUID  # The main developer's User ID (or Developer ID if separate)
    user_id: UUID       # The team member's User ID
    role: str           # e.g., "Marketing", "Sales"
    permissions: List[str] = [] # e.g., ["view_leads", "manage_visits"]
    
    invited_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Settings:
        name = "developer_team_members"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class StaffTask(Document):
    id: UUID = Field(default_factory=uuid4)
    assigned_to: UUID # User ID of staff
    assigned_by: UUID # Admin ID
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    due_date: Optional[datetime] = None
    
    related_client_id: Optional[UUID] = None # Optional link to a client/developer
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "staff_tasks"

class SharedClient(Document):
    id: UUID = Field(default_factory=uuid4)
    member_id: UUID
    client_id: UUID
    permissions: List[str] = [] # e.g. ["view_contact", "view_financials"]
    shared_by: UUID # Admin ID
    purpose: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "shared_clients"
