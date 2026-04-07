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
from app.models.ad import Ad
from app.models.video import Video
from app.models.team import DeveloperTeamMember, StaffTask, SharedClient
from app.models.review import Review
from app.models.subscription import SubscriptionPlan, DeveloperSubscription
from app.models.lawyer import LawyerProfile, LawyerLead, LawyerSubscription, LawyerEvent
from app.models.lawyer_consultation import LawyerConsultation
import app.models.legal_call as legal_call_module
from app.models.property_transaction import PropertyTransaction
from app.models.society import Society
from app.models.locality_review import LocalityReview
from app.models.price_history import PriceHistory
from app.models.market_intelligence import MarketIntelligence
from app.models.user_preferences import UserNotificationPreferences
from app.models.notification import Notification
from app.models.blog import Blog
from app.models.reel import Reel, ReelLike, ReelComment, ReelSave
from app.models.city import City


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
            StaffTask,
            SharedClient,
            SubscriptionPlan,
            DeveloperSubscription,
            legal_call_module.LegalCallRequest,
            Ad,
            Video,
            Review,
            LawyerProfile,
            LawyerLead,
            LawyerSubscription,
            LawyerEvent,
            LawyerConsultation,
            PropertyTransaction,
            Society,
            LocalityReview,
            PriceHistory,
            UserNotificationPreferences,
            MarketIntelligence,
            Notification,
            Blog,
            Reel,
            ReelLike,
            ReelComment,
            ReelSave,
            City,
        ]

    )

    return client
