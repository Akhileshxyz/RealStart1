from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings

from app.models.user import User
from app.models.developer import Developer
from app.models.project import Project
from app.models.lead import ProjectLead
from app.models.webhook import WebhookSubscription
from app.models.change_request import ProjectChangeRequest
from app.models.landmark import Landmark
from app.models.visit import VisitBooking
from app.models.team import DeveloperTeamMember
from app.models.subscription import SubscriptionPlan, DeveloperSubscription
from app.models.legal_call import LegalCallRequest

async def init_db():
    client = AsyncIOMotorClient(settings.MONGODB_URL)

    # Initialize Beanie with all document models
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[
            User,
            Developer,
            Project,
            ProjectLead,
            WebhookSubscription,
            ProjectChangeRequest,
            Landmark,
            VisitBooking,
            DeveloperTeamMember,
            SubscriptionPlan,
            DeveloperSubscription,
            LegalCallRequest
        ]
    )

    return client
