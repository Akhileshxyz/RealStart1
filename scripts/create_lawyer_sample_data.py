import asyncio
import os
import sys
import random
from datetime import datetime, timedelta
from uuid import uuid4

# Add project root to path
sys.path.append(os.getcwd())

from app.db.mongodb import init_db
from app.models.user import User, UserRole
from app.models.lawyer import LawyerProfile, LawyerLead, LawyerLeadStatus, LawyerPaymentStatus, LawyerSubscription, LawyerSubscriptionPlan
from app.models.project import Project, ProjectStatus, PropertyType
from app.models.legal_call import LegalCallRequest, LegalCallStatus
from app.core import security

# Constants
LAWYER_COUNT = 5
CLIENT_COUNT = 10
PROJECT_COUNT = 5
LEAD_COUNT = 15
CALL_REQUEST_COUNT = 5

SPECIALIZATIONS = ["Property Verification", "RERA Compliance", "Litigation", "Family Law", "Corporate Law"]
CITIES = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai"]
LANGUAGES = ["English", "Hindi", "Kannada", "Tamil", "Telugu"]
SERVICE_TYPES = ["Document Review", "Legal Consultation", "Property Registration", "Dispute Resolution"]
PRIORITIES = ["HIGH", "MEDIUM", "LOW"]

async def create_lawyer_sample_data():
    print("Initializing Database...")
    await init_db()

    print("--- Creating Lawyers ---")
    lawyers = []
    for i in range(LAWYER_COUNT):
        email = f"lawyer{i+1}@realstart.com"
        password = "password123"
        
        # Check if exists
        user = await User.find_one(User.email == email)
        if not user:
            user = User(
                email=email,
                hashed_password=security.get_password_hash(password),
                full_name=f"Lawyer {i+1} Name",
                phone=f"+91987654320{i}",
                role=UserRole.LAWYER,
                is_active=True
            )
            await user.insert()
            
            profile = LawyerProfile(
                user_id=user.id,
                bio=f"Experienced lawyer specializing in {random.choice(SPECIALIZATIONS)}.",
                specialization=random.sample(SPECIALIZATIONS, k=2),
                bar_council_id=f"KAR/{random.randint(1000, 9999)}/20{random.randint(10, 23)}",
                experience_years=random.randint(3, 20),
                is_online=random.choice([True, False]),
                cities=random.sample(CITIES, k=1),
                languages=random.sample(LANGUAGES, k=2),
                rating=round(random.uniform(3.5, 5.0), 1),
                review_count=random.randint(0, 50)
            )
            await profile.insert()
            
            user.lawyer_profile_id = profile.id
            await user.save()
            
            # Create Subscription
            sub = LawyerSubscription(
                lawyer_id=profile.id,
                plan_name=random.choice(list(LawyerSubscriptionPlan)),
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                is_active=True
            )
            await sub.insert()
            
            print(f"Created Lawyer: {email} (ID: {user.id})")
        else:
            print(f"Lawyer {email} already exists.")
            # Fetch profile if exists for usage later
            if user.lawyer_profile_id:
                profile = await LawyerProfile.get(user.lawyer_profile_id)
            else:
                 # Should not happen based on logic, but handle it
                 continue

        lawyers.append({"user": user, "profile": profile})

    print("--- Creating Clients ---")
    clients = []
    for i in range(CLIENT_COUNT):
        email = f"client{i+1}@example.com"
        password = "password123"
        
        user = await User.find_one(User.email == email)
        if not user:
            user = User(
                email=email,
                hashed_password=security.get_password_hash(password),
                full_name=f"Client {i+1} Name",
                phone=f"+91900000000{i}",
                role=UserRole.BUYER,
                is_active=True
            )
            await user.insert()
            print(f"Created Client: {email} (ID: {user.id})")
        else:
            print(f"Client {email} already exists.")
        clients.append(user)

    print("--- Creating Projects ---")
    projects = []
    for i in range(PROJECT_COUNT):
        slug = f"project-sample-{i+1}"
        project = await Project.find_one(Project.slug == slug)
        if not project:
            # Need a developer ID? We can use uuid4() for now or fetch one if strictly needed. 
            # Assuming loose coupling or we don't check FKey constraints strictly in app code here.
            # But better to use a random UUID since we don't have developers in this script.
            developer_id = uuid4() 
            
            project = Project(
                developer_id=developer_id,
                name=f"Sample Project {i+1}",
                slug=slug,
                description="A beautiful sample project.",
                status=ProjectStatus.APPROVED,
                address="123 Sample St, Bangalore",
                property_type=random.choice(list(PropertyType)),
                min_price=5000000,
                max_price=15000000,
                total_units=100,
                available_units=50
            )
            await project.insert()
            print(f"Created Project: {project.name} (ID: {project.id})")
        else:
            print(f"Project {slug} already exists.")
        projects.append(project)

    print("--- Creating Lawyer Leads ---")
    # Distribute leads among lawyers
    if lawyers and clients:
        for i in range(LEAD_COUNT):
            lawyer_data = random.choice(lawyers)
            client = random.choice(clients)
            
            # Basic lead info
            lead = LawyerLead(
                lawyer_id=lawyer_data["profile"].id,
                client_name=client.full_name,
                client_phone=client.phone,
                client_email=client.email,
                client_city=random.choice(CITIES),
                service_type=random.choice(SERVICE_TYPES),
                priority=random.choice(PRIORITIES),
                service_fee=random.choice([0.0, 500.0, 1000.0, 5000.0]),
                status=random.choice(list(LawyerLeadStatus)),
                payment_status=random.choice(list(LawyerPaymentStatus)),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            await lead.insert()
    print(f"Created {LEAD_COUNT} Lawyer Leads.")

    print("--- Creating Legal Call Requests ---")
    if projects and clients and lawyers:
        for i in range(CALL_REQUEST_COUNT):
            client = random.choice(clients)
            project = random.choice(projects)
            
            call_req = LegalCallRequest(
                user_id=client.id,
                project_id=project.id,
                topics=["Title Check", "Agreement Review"],
                status=random.choice(list(LegalCallStatus)),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 10))
            )
            await call_req.insert()
    print(f"Created {CALL_REQUEST_COUNT} Legal Call Requests.")

    print("\nSample Data Generation Complete!")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(create_lawyer_sample_data())
