from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from enum import Enum

# --- Enums (Indian context) ---


class CaseStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ON_HOLD = "ON_HOLD"


class CasePriority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ServiceType(str, Enum):
    DOCUMENT_REVIEW = "Document Review"
    TITLE_SEARCH = "Title Search"
    LEGAL_CONSULTATION = "Legal Consultation"
    RERA_VERIFICATION = "RERA Verification"
    AGREEMENT_DRAFT = "Agreement Draft"
    OTHER = "Other"


class EventType(str, Enum):
    COURT = "Court"
    MEETING = "Meeting"
    TASK = "Task"
    SITE_VISIT = "Site Visit"


# --- Utility Formatters ---


def format_indian_currency(amount: float) -> str:
    """Format amount as Indian currency string with rupee symbol and proper grouping."""
    if amount < 0:
        return f"-₹{format_indian_currency(abs(amount))[1:]}"
    rupee = "₹"
    amount_paise = int(round(amount * 100))
    if amount_paise < 100:
        return f"{rupee}{amount_paise / 100:.2f}"
    number = str(amount_paise // 100)
    last_three = number[-3:]
    rest = number[:-3]
    if rest:
        parts = []
        while len(rest) > 2:
            parts.append(rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.append(rest)
        parts.reverse()
        formatted = f"{','.join(parts)},{last_three}"
    else:
        formatted = last_three
    return f"{rupee}{formatted}"


def format_indian_datetime(dt: datetime) -> Dict[str, str]:
    """Return ISO datetime + Indian display strings."""
    iso = dt.isoformat() + "Z" if dt.tzinfo is None else dt.isoformat()
    display_date = dt.strftime("%d %b %Y")  # e.g., 21 Jan 2026
    display_time = dt.strftime("%I:%M %p")  # e.g., 10:00 AM
    return {"iso": iso, "display_date": display_date, "display_time": display_time}


# --- Models ---


class LawyerDashboardStats(BaseModel):
    active_cases: int
    active_cases_delta: str
    total_clients: int
    total_clients_delta: str
    pending_reviews: int
    pending_reviews_delta: str
    completed_cases: int
    completed_cases_delta: str


class EarningsBreakdownItem(BaseModel):
    category: str
    amount: str


class LawyerDashboardEarnings(BaseModel):
    total_earnings: str  # Indian formatted string, e.g., "₹1,45,000"
    delta_text: str
    breakdown: List[EarningsBreakdownItem]


class LawyerDashboardAlert(BaseModel):
    text: str
    severity: str  # "high", "medium", "low"
    action_link: Optional[str] = (
        None  # Internal ID/Path if needed, but keeping data pure
    )


class LawyerDashboardData(BaseModel):
    stats: LawyerDashboardStats
    earnings: LawyerDashboardEarnings
    recent_cases: List["LawyerCase"]
    todays_schedule: List["LawyerScheduleEvent"]
    alerts: List[LawyerDashboardAlert]


class LawyerCasesStats(BaseModel):
    total_cases: int
    pending_cases: int
    in_progress_cases: int
    completed_cases: int
    on_hold_cases: int


class LawyerCasesData(BaseModel):
    stats: LawyerCasesStats
    filters: Dict[str, List[str]]
    cases: List["LawyerCase"]


class LawyerCase(BaseModel):
    id: str  # UUID
    client_initials: str
    client_name: str
    project_name: Optional[str] = None
    service_type: ServiceType
    status: CaseStatus
    priority: CasePriority
    location: Optional[str] = None
    date: Dict[str, str]  # {"iso": "...", "display_date": "...", "display_time": "..."}
    # derived/internal fields
    project_id: Optional[str] = None
    lead_id: Optional[str] = None


class LawyerClientStats(BaseModel):
    total_cases: int
    active_cases: int
    completed_cases: int


class LawyerClient(BaseModel):
    id: str  # UUID or Lead ID
    initials: str
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    stats: LawyerClientStats


class LawyerClientsStatsSummary(BaseModel):
    total_clients: int
    active_clients: int
    cases_completed: int
    new_this_month: int


class LawyerClientsData(BaseModel):
    stats: LawyerClientsStatsSummary
    clients: List["LawyerClient"]


class LawyerScheduleEvent(BaseModel):
    id: str
    title: str
    date: Dict[str, str]  # {"iso": "...", "display_date": "...", "display_time": "..."}
    time_str: str  # "10:00 AM" - for UI display if needed, or just use date
    location: Optional[str] = None
    client_name: Optional[str] = None
    type: EventType


class LawyerScheduleData(BaseModel):
    today: List[LawyerScheduleEvent]
    upcoming: List[LawyerScheduleEvent]


class LawyerAnalyticsMetric(BaseModel):
    id: str
    title: str
    value: Any
    delta: str
    delta_label: str


class LawyerAnalyticsData(BaseModel):
    metrics: List[LawyerAnalyticsMetric]
    charts: List[Dict[str, Any]]  # flexible for various chart configs


class NotificationPreference(BaseModel):
    id: str
    label: str
    description: str
    enabled: bool


class LawyerProfileData(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    bar_council_number: Optional[str] = None
    specialization: List[str] = []
    experience: int = 0
    city: Optional[str] = None
    office_address: Optional[str] = None
    bio: Optional[str] = None
    working_days: List[Dict[str, Any]] = []  # {"day": "Mon", "enabled": True}
    working_hours: Dict[str, str] = {}  # {"start": "09:00", "end": "18:00"}


class ClientLeadCreate(BaseModel):
    client_name: str
    client_phone: str
    client_email: Optional[EmailStr] = None
    client_city: Optional[str] = None
    property_id: Optional[UUID] = None
    service_fee: Optional[float] = 0.0
    project_name: Optional[str] = None
    service_type: Optional[str] = None
    priority: Optional[str] = None
    fee_amount: Optional[float] = None
    notes: Optional[str] = None


class LawyerSettingsData(BaseModel):
    profile: LawyerProfileData
    notification_preferences: List[NotificationPreference]


LawyerDashboardData.update_forward_refs()
LawyerCasesData.update_forward_refs()
LawyerClientsData.update_forward_refs()
