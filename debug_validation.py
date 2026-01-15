import asyncio
import httpx
from app.db.mongodb import init_db
from app.models.project import Project

async def test_validation():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzY5NjAzMzcsInN1YiI6ImJmMzUxN2JkLWUxZGItNGNiOS04OWExLWQzOWRmMTllNmFlMSJ9.7xN_9sN7Gf9iP1vF69-GK9V95sgRuaRzfyYB7wt41BalPBE"
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        # 1. Try to hit the endpoint
        response = client.get("http://localhost:8000/api/v1/admin/projects/?skip=0&limit=25", headers=headers)
        # response is a coroutine here, wait for it
        response = await response
        print(f"Status Code: {response.status_code}")
        if response.status_code == 500:
            print("Response:", response.text)
        
        # 2. Check DB content
        await init_db()
        projects = await Project.find_all().limit(25).to_list()
        for i, p in enumerate(projects):
            print(f"Project {i} type(legal_compliance): {type(p.legal_compliance)}")
            print(f"Project {i} value: {p.legal_compliance}")

if __name__ == "__main__":
    asyncio.run(test_validation())
