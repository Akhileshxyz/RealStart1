from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Optional
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
