import asyncio
import httpx
from uuid import uuid4
from app.db.mongodb import init_db
from app.models.landmark import Landmark
from app.models.market_intelligence import MarketIntelligence

async def test_apis():
    # 1. Setup - Create a mock landmark
    await init_db()
    test_landmark = Landmark(
        name="Test City",
        city="Test State",
        zone="Test Zone",
        latitude=0.0,
        longitude=0.0
    )
    await test_landmark.insert()
    landmark_id = str(test_landmark.id)
    print(f"Created test landmark: {landmark_id}")

    # 2. Test Public API (Expect 404 since no intelligence yet)
    async with httpx.AsyncClient(timeout=10.0) as client:
        url = f"http://localhost:8000/api/v1/locality/market-intelligence/{landmark_id}"
        resp = await client.get(url)
        print(f"Public API (Pre-seed) Status: {resp.status_code}")
        assert resp.status_code == 404

        # Note: We can't easily test Admin API here without a login token.
        # But we can test the internal logic by inserting directly via model.
        
        # 3. Insert Intelligence Data
        intelligence_data = {
            "landmark_id": test_landmark.id,
            "overview": "Test Overview",
            "avg_commercial_plot_price": 100,
            "avg_residential_plot_price": 50,
            "avg_rental_2bhk": 10,
            "economic_output": "1B",
            "population": "1M",
            "appreciation_potential_5yr": "10%",
            "growth_history": [],
            "growth_prediction": [],
            "political_agenda": {"mla": "A", "mp": "B", "governance": "C", "focus": []},
            "amenities": [],
            "upcoming_projects": [],
            "investment_landmarks": [],
            "map_landmarks": []
        }
        intelligence = MarketIntelligence(**intelligence_data)
        await intelligence.insert()
        print("Inserted test market intelligence.")

        # 4. Test List API
        list_url = f"http://localhost:8000/api/v1/locality/market-intelligence"
        resp = await client.get(list_url)
        print(f"List API Status: {resp.status_code}")
        assert resp.status_code == 200
        list_data = resp.json()
        assert len(list_data) >= 1
        assert any(item["landmark_id"] == landmark_id for item in list_data)
        print("List API Verification Successful.")

        # 5. Test Single City Public API (Expect 200)
        resp = await client.get(url)
        print(f"Public API (Post-seed) Status: {resp.status_code}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["overview"] == "Test Overview"
        print("Public API Verification Successful.")

    # 5. Cleanup
    await MarketIntelligence.find_one(MarketIntelligence.landmark_id == test_landmark.id).delete()
    await test_landmark.delete()
    print("Cleanup successful.")

if __name__ == "__main__":
    asyncio.run(test_apis())
