import asyncio
import httpx
from uuid import UUID

async def test_apis():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000/api/v1/locality") as client:
        # 1. Get Cities
        print("--- GET /market-intelligence (Cities) ---")
        resp = await client.get("/market-intelligence")
        cities = resp.json()
        print(f"Status: {resp.status_code}")
        print(f"Cities count: {len(cities)}")
        
        doddaballapura_id = None
        for c in cities:
            if c.get("name") == "Doddaballapura":
                doddaballapura_id = c.get("landmark_id")
                
        if not doddaballapura_id:
            print("Doddaballapura not found!")
            return
            
        # 2. City detail includes embedded areas (same as GET /market-intelligence/{id}?include_areas=true)
        print(f"\n--- GET /market-intelligence/{doddaballapura_id} (city + areas) ---")
        resp = await client.get(f"/market-intelligence/{doddaballapura_id}")
        city = resp.json()
        areas = city.get("areas") or []
        print(f"Status: {resp.status_code}")
        print(f"Areas count: {len(areas)}")
        
        bus_stand_id = None
        for a in areas:
            print(f"- {a.get('name')}")
            if a.get("name") == "Near Doddaballapura Bus Stand":
                bus_stand_id = a.get("landmark_id")
                
        if not bus_stand_id:
            print("Bus stand area not found!")
            return
            
        # 3. Get Individual Area View
        print(f"\n--- GET /market-intelligence/{bus_stand_id} (Individual Area View) ---")
        resp = await client.get(f"/market-intelligence/{bus_stand_id}")
        area_details = resp.json()
        print(f"Status: {resp.status_code}")
        print(f"Name expected: Near Doddaballapura Bus Stand")
        print(f"Overview snippet: {area_details.get('overview')[:50]}...")
        box = area_details.get("box_content") or {}
        print(f"Avg Comm Price: {box.get('avg_commercial_plot_price')}")

if __name__ == "__main__":
    asyncio.run(test_apis())
