import asyncio
from uuid import UUID
from app.db.mongodb import init_db
from app.models.landmark import Landmark
from app.models.project import Project
from app.schemas.landmark import LandmarkSelection
from app.schemas.project import ProjectSelection

async def test():
    await init_db()
    
    print("Testing Landmark Selection...")
    landmarks = await Landmark.find().limit(5).project(LandmarkSelection).to_list()
    for l in landmarks:
        print(f"ID: {l.id}, Name: {l.name}, City: {l.city_id}")
        
    print("\nTesting Project Selection...")
    projects = await Project.find().limit(5).project(ProjectSelection).to_list()
    for p in projects:
        print(f"ID: {p.id}, Name: {p.name}, Status: {p.status}")

if __name__ == "__main__":
    asyncio.run(test())
