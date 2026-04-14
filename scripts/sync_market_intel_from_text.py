import asyncio
import re
import os
import sys
from pathlib import Path
from datetime import datetime
from uuid import uuid4, UUID
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, Document
from pydantic import Field
from typing import Optional, Dict, Any, List

# Ensure we can import from app
sys.path.append(os.getcwd())

# --- Models ---
from app.models.landmark import Landmark, GeoJSONLocation
from app.models.market_intelligence import MarketIntelligence
from app.models.city import City

# --- Utils ---

def parse_price(price_str):
    if not price_str: return 0.0
    # Clean string and find numbers
    price_str = price_str.replace(',', '').replace('(', '').replace(')', '')
    match = re.search(r'₹?\s*([\d.]+)\s*(L|Lakhs|Cr|Crores)?', price_str, re.IGNORECASE)
    if not match: 
        # try simple number
        m = re.search(r'([\d.]+)', price_str)
        return float(m.group(1)) if m else 0.0
    
    val = float(match.group(1))
    suffix = match.group(2)
    if suffix:
        suffix = suffix.lower()
        if 'cr' in suffix: val *= 10000000
        elif 'l' in suffix: val *= 100000
    return val

def clean_text(text):
    if not text: return ""
    return text.strip().replace('_', '').replace('________________________________________', '').strip()

# --- Parsers ---

async def parse_lat(file_path):
    coords = {}
    print(f"Parsing coordinates from {file_path}...")
    try:
        content = Path(file_path).read_text(encoding='utf-8')
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('📍') or 'Latitude' in line or '#' in line:
                continue

            parts = line.split('\t')
            try:
                if len(parts) >= 5: # #, City, Landmark, Lat, Lng
                    name = parts[2].strip()
                    lat = float(parts[3])
                    lng = float(parts[4])
                    coords[name] = (lat, lng)
                else:
                    # Fallback to regex for space-separated
                    match = re.search(r'^\d+\s+\w+\s+(.*?)\s+([\d.]+)\s+([\d.]+)', line)
                    if match:
                        name = match.group(1).strip()
                        lat = float(match.group(2))
                        lng = float(match.group(3))
                        coords[name] = (lat, lng)
            except (ValueError, IndexError):
                continue
        print(f"Mapped {len(coords)} landmarks with coordinates.")
    except Exception as e:
        print(f"Error parsing lat: {e}")
    return coords

async def sync_dodd(file_path, city_landmark_id, city_id, coords):
    print(f"Parsing city intelligence from {file_path}...")
    try:
        content = Path(file_path).read_text(encoding='utf-8')
        
        # 1. Overview
        overview_match = re.search(r'1️⃣ Market Overview\n(.*?)\n_{5,}', content, re.DOTALL)
        overview = clean_text(overview_match.group(1)) if overview_match else ""
        
        # 2. Stats
        commercial = parse_price(re.search(r'Average Commercial Plot Price\n(.*?)\n', content).group(1))
        residential = parse_price(re.search(r'Average Residential Plot Price\n(.*?)\n', content).group(1))
        rental_str = re.search(r'Average Rental \(2BHK House\)\n(.*?)\n', content).group(1)
        rental = parse_price(rental_str.split('–')[0]) # lower bound
        economic = clean_text(re.search(r'Estimated Local Economic Output.*?\n(.*?)\n', content).group(1))
        pop = clean_text(re.search(r'Population\n(.*?)\n', content).group(1))
        appreciation = clean_text(re.search(r'Next 5-Year Appreciation Potential\n(.*?)\n', content).group(1))
        
        # 3. Growth History
        history = []
        history_match = re.search(r'3️⃣ Last 5 Years Growth.*?\n(.*?)\n_{5,}', content, re.DOTALL)
        if history_match:
            for line in history_match.group(1).strip().split('\n'):
                m = re.match(r'(\d{4})\t₹(\d+)\s*L\t(.*)', line)
                if not m: m = re.match(r'(\d{4})\s+₹(\d+)\s*L\s+(.*)', line)
                if m:
                    history.append({"year": int(m.group(1)), "price": int(m.group(2)), "reason": m.group(3).strip()})

        # 4. Growth Prediction
        prediction = []
        pred_match = re.search(r'4️⃣ Next 5 Years Prediction.*?\n(.*?)\n_{5,}', content, re.DOTALL)
        if pred_match:
            for line in pred_match.group(1).strip().split('\n'):
                m = re.match(r'(\d{4})\t₹(\d+)\s*L\t(.*)', line)
                if not m: m = re.match(r'(\d{4})\s+₹(\d+)\s*L\s+(.*)', line)
                if m:
                    prediction.append({"year": int(m.group(1)), "price": int(m.group(2)), "reason": m.group(3).strip()})

        # 5. Political Agenda
        mla_m = re.search(r'•\s*MLA:\s*(.*?)\n', content)
        mp_m = re.search(r'•\s*MP.*?: (.*?)\n', content)
        gov_m = re.search(r'•\s*Governance:\s*(.*?)\n', content)
        
        focus = []
        focus_match = re.search(r'Current Agenda Focus:\n(.*?)\n_{5,}', content, re.DOTALL)
        if focus_match:
            focus = [l.strip('• ').strip() for l in focus_match.group(1).strip().split('\n') if l.strip()]
        
        # 6. Amenities & 7. Upcoming
        amenities = []
        am_match = re.search(r'6️⃣ Key Amenities\n(.*?)\n_{5,}', content, re.DOTALL)
        if am_match: amenities = [l.strip('• ').strip() for l in am_match.group(1).strip().split('\n') if l.strip()]

        upcoming = []
        up_match = re.search(r'7️⃣ Upcoming Development Projects.*?\n(.*?)\n_{5,}', content, re.DOTALL)
        if up_match: upcoming = [l.strip('• ').strip() for l in up_match.group(1).strip().split('\n') if l.strip()]

        # 8. Top 7 Investment Landmarks
        investment_landmarks = []
        inv_match = re.search(r'8️⃣ Top 7 Investment Landmarks.*?\n(.*?)\n_{5,}', content, re.DOTALL)
        if inv_match:
            inv_text = inv_match.group(1).strip()
            # Split by numbered items: 1. , 2. etc.
            inv_items = re.split(r'\n\d+\.\s+', '\n' + inv_text)
            for item in inv_items:
                if not item.strip(): continue
                lines = item.strip().split('\n')
                name = lines[0].strip()
                res = parse_price(re.search(r'Residential:\s*(.*?)$', item, re.M).group(1)) if re.search(r'Residential:', item) else 0
                comm = parse_price(re.search(r'Commercial:\s*(.*?)$', item, re.M).group(1)) if re.search(r'Commercial:', item) else 0
                rent = re.search(r'Rental:\s*(.*?)$', item, re.M).group(1).strip() if re.search(r'Rental:', item) else ""
                growth = re.search(r'Growth:\s*(.*?)$', item, re.M).group(1).strip() if re.search(r'Growth:', item) else ""
                if not growth:
                    growth = re.search(r'5-Year Growth:\s*(.*?)$', item, re.M).group(1).strip() if re.search(r'5-Year Growth:', item) else ""
                
                investment_landmarks.append({
                    "name": name,
                    "residential": res,
                    "commercial": comm,
                    "rental": rent,
                    "growth": growth.strip('%') + "%" if growth else ""
                })

        # 9. Map Landmarks
        map_landmarks = []
        map_section = re.search(r'9️⃣ 48 Major Landmarks.*?\n(.*?)\n_{5,}', content, re.DOTALL)
        if map_section:
            for line in map_section.group(1).strip().split('\n'):
                if '#' in line or 'Landmark' in line: continue
                m = re.match(r'(\d+)\t(.*?)\t₹(\d+)\s*L\t(\d+)%', line)
                if m:
                    name = m.group(2).strip()
                    l_coords = coords.get(name) or coords.get(name.replace('Near ', ''))
                    map_landmarks.append({
                        "name": name, "price": int(m.group(3)), "growth": int(m.group(4)),
                        "latitude": l_coords[0] if l_coords else None, "longitude": l_coords[1] if l_coords else None
                    })

        intel_data = {
            "landmark_id": city_landmark_id, "location_type": "city", "overview": overview,
            "avg_commercial_plot_price": commercial, "avg_residential_plot_price": residential,
            "avg_rental_2bhk": rental, "economic_output": economic, "population": pop,
            "appreciation_potential_5yr": appreciation, "growth_history": history, "growth_prediction": prediction,
            "political_agenda": {
                "mla": mla_m.group(1) if mla_m else "", 
                "mp": mp_m.group(1) if mp_m else "", 
                "governance": gov_m.group(1) if gov_m else "Nagarasabha",
                "focus": focus
            },
            "amenities": amenities, "upcoming_projects": upcoming, 
            "investment_landmarks": investment_landmarks, "map_landmarks": map_landmarks,
            "updated_at": datetime.utcnow()
        }
        
        existing = await MarketIntelligence.find_one(MarketIntelligence.landmark_id == city_landmark_id)
        if existing:
            for k, v in intel_data.items(): setattr(existing, k, v)
            await existing.save()
        else:
            await MarketIntelligence(**intel_data).insert()

        # Also update the City document directly for the 6 boxes displayed in frontend
        city_doc = await City.get(city_id)
        if city_doc:
            city_doc.avg_commercial_plot_price = commercial
            city_doc.avg_residential_plot_price = residential
            city_doc.avg_rental_2bhk = rental_str
            city_doc.economic_output = economic
            city_doc.population = pop
            city_doc.appreciation_potential_5yr = appreciation
            await city_doc.save()
            print(f"City document '{city_doc.name}' updated with market intelligence.")

        print("City market intelligence synced successfully.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error syncing city data: {e}")

async def sync_dod_full(file_path, city_landmark_id, city_id, coords):
    print(f"Parsing area intelligence from {file_path}...")
    try:
        content = Path(file_path).read_text(encoding='utf-8')
        landmark_sections = re.split(r'\n(?=\d+\.\s+)', content)
        
        for section in landmark_sections:
            section = section.strip()
            if not section or 'Doddaballapura City Landmarks Data' in section: continue
            
            name_raw = section.split('\n')[0].strip()
            name = re.sub(r'^\d+\.\s+', '', name_raw).strip()
            if not name or len(name) < 3: continue
            
            print(f"Syncing Area: {name}")
            
            l_coords = coords.get(name) or coords.get(name.replace('Near ', '').strip())
            landmark = await Landmark.find_one(Landmark.name == name)
            
            geo_loc = None
            if l_coords: geo_loc = GeoJSONLocation(type="Point", coordinates=[l_coords[1], l_coords[0]])

            if not landmark:
                landmark = Landmark(name=name, city_id=city_id, location=geo_loc)
                await landmark.insert()
            else:
                landmark.city_id = city_id
                if geo_loc: landmark.location = geo_loc
                await landmark.save()

            # Filter out sub-section splits
            about_m = re.search(r'1️⃣ About.*?\n(.*?)\n_{5,}', section, re.DOTALL)
            overview = clean_text(about_m.group(1)) if about_m else ""
            
            comm_m = re.search(r'Average Commercial Plot Price\s+₹?(\d+)\s*(L|Lakhs)', section)
            res_m = re.search(r'Average Residential Plot Price\s+₹?(\d+)\s*(L|Lakhs)', section)
            appr_m = re.search(r'Next 5 Year Appreciation\s+(.*?)\n', section)

            intel_data = {
                "landmark_id": landmark.id, "parent_landmark_id": city_landmark_id, "location_type": "area",
                "overview": overview, "avg_commercial_plot_price": parse_price(comm_m.group(0)) if comm_m else 0,
                "avg_residential_plot_price": parse_price(res_m.group(0)) if res_m else 0,
                "avg_rental_2bhk": 0, "economic_output": "", "population": "",
                "appreciation_potential_5yr": appr_m.group(1).strip() if appr_m else "",
                "growth_history": [], "growth_prediction": [], "political_agenda": {},
                "amenities": [], "upcoming_projects": [], "investment_landmarks": [], "map_landmarks": [],
                "updated_at": datetime.utcnow()
            }
            
            existing = await MarketIntelligence.find_one(MarketIntelligence.landmark_id == landmark.id)
            if existing:
                for k, v in intel_data.items(): setattr(existing, k, v)
                await existing.save()
            else:
                await MarketIntelligence(**intel_data).insert()
        print("All area intelligence sections synced.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error syncing areas: {e}")

async def main():
    try:
        from app.core.config import settings
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        await init_beanie(
            database=client[settings.DATABASE_NAME],
            document_models=[City, Landmark, MarketIntelligence]
        )
        
        # 1. Ensure City exists (Strictly use Doddaballapura as requested)
        city = await City.find_one(City.name == "Doddaballapura")
        if not city:
            city = City(name="Doddaballapura", slug="doddaballapura", is_active=True)
            await city.insert()
            print(f"Created City: Doddaballapura")

        # 2. Ensure Main Landmark for City Intel exists
        city_landmark = await Landmark.find_one(Landmark.name == "Doddaballapura")
        if not city_landmark:
            city_landmark = Landmark(
                name="Doddaballapura", city_id=city.id,
                location=GeoJSONLocation(type="Point", coordinates=[77.5342, 13.2924])
            )
            await city_landmark.insert()
            print(f"Created main Landmark: Doddaballapura")
        else:
            city_landmark.city_id = city.id
            await city_landmark.save()

        coords = await parse_lat("f:/github/Realstart/lat")
        await sync_dodd("f:/github/Realstart/dodd", city_landmark.id, city.id, coords)
        await sync_dod_full("f:/github/Realstart/dod full", city_landmark.id, city.id, coords)
        
        print("\nSUCCESS: Data from dodd, dod full, and lat pushed to DB.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Sync Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
