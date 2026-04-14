import asyncio
import re
import os
import sys
from pathlib import Path
from datetime import datetime
from uuid import uuid4, UUID
from motor.motor_asyncio import AsyncIOMotorClient

# Ensure we can import from app
sys.path.append(os.getcwd())
from app.core.config import settings

def parse_price(price_str):
    if not price_str: return 0.0
    price_str = price_str.replace(',', '').replace('(', '').replace(')', '')
    match = re.search(r'₹?\s*([\d.]+)\s*(L|Lakhs|Cr|Crores)?', price_str, re.IGNORECASE)
    if not match: 
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

async def main():
    print("Connecting to MongoDB...")
    # FIX: Use UuidRepresentation standard for Pymongo
    client = AsyncIOMotorClient(settings.MONGODB_URL, uuidRepresentation='standard')
    db = client[settings.DATABASE_NAME]
    
    # 1. Get Doddaballapura City
    city = await db.cities.find_one({"name": "Doddaballapura"})
    if not city:
        print("City Doddaballapura not found!")
        return
    city_id = city["_id"] # Native UUID

    # 2. Get/Create Main City Landmark
    landmark = await db.landmarks.find_one({"name": "Doddaballapura"})
    if not landmark:
        landmark_id = uuid4()
        await db.landmarks.insert_one({
            "_id": landmark_id, "name": "Doddaballapura", "city_id": city_id,
            "location": {"type": "Point", "coordinates": [77.5376, 13.2923]}
        })
    else:
        landmark_id = landmark["_id"]

    # 3. Parse dodd content
    content_dodd = Path("f:/github/Realstart/dodd").read_text(encoding='utf-8')
    content_lat = Path("f:/github/Realstart/lat").read_text(encoding='utf-8')
    
    # --- Basic Stats ---
    commercial = parse_price(re.search(r'Average Commercial Plot Price\n(.*?)\n', content_dodd).group(1))
    residential = parse_price(re.search(r'Average Residential Plot Price\n(.*?)\n', content_dodd).group(1))
    rental_str = re.search(r'Average Rental \(2BHK House\)\n(.*?)\n', content_dodd).group(1)
    economic = clean_text(re.search(r'Estimated Local Economic Output.*?\n(.*?)\n', content_dodd).group(1))
    pop = clean_text(re.search(r'Population\n(.*?)\n', content_dodd).group(1))
    appreciation = clean_text(re.search(r'Next 5-Year Appreciation Potential\n(.*?)\n', content_dodd).group(1))
    
    # --- History & Prediction ---
    history = []
    history_match = re.search(r'3️⃣ Last 5 Years Growth.*?\n(.*?)\n_{5,}', content_dodd, re.DOTALL)
    if history_match:
        for line in history_match.group(1).strip().split('\n'):
            m = re.match(r'(\d{4})\s+₹(\d+)\s*L\s+(.*)', line)
            if not m: m = re.match(r'(\d{4})\t₹(\d+)\s*L\t(.*)', line)
            if m: history.append({"year": int(m.group(1)), "value": float(m.group(2)) * 100000})

    prediction = []
    pred_match = re.search(r'4️⃣ Next 5 Years Prediction.*?\n(.*?)\n_{5,}', content_dodd, re.DOTALL)
    if pred_match:
        for line in pred_match.group(1).strip().split('\n'):
            m = re.match(r'(\d{4})\s+₹(\d+)\s*L\s+(.*)', line)
            if not m: m = re.match(r'(\d{4})\t₹(\d+)\s*L\t(.*)', line)
            if m:
                val = float(m.group(2)) * 100000
                prediction.append({"year": int(m.group(1)), "value1": val, "value2": val})

    # --- Political Agenda ---
    mla_m = re.search(r'MLA:\s*(.*?)\n', content_dodd)
    mp_m = re.search(r'MP.*?:\s*(.*?)\n', content_dodd)
    policies = []
    agenda_section = re.search(r'5️⃣ Political & Infrastructure Agenda\n(.*?)\n_{5,}', content_dodd, re.DOTALL)
    if agenda_section:
        focus_match = re.search(r'Current Agenda Focus:\n(.*?)$', agenda_section.group(1), re.DOTALL)
        if focus_match:
            policies = [l.strip('• ').strip() for l in focus_match.group(1).strip().split('\n') if l.strip()]

    # --- Amenities & Projects ---
    amenities = []
    am_section = re.search(r'6️⃣ Key Amenities\n(.*?)\n_{5,}', content_dodd, re.DOTALL)
    if am_section:
        amenities = [l.strip('• ').strip() for l in am_section.group(1).strip().split('\n') if l.strip()]

    upcoming = []
    up_section = re.search(r'7️⃣ Upcoming Development Projects.*?\n(.*?)\n_{5,}', content_dodd, re.DOTALL)
    if up_section:
        upcoming = [l.strip('• ').strip() for l in up_section.group(1).strip().split('\n') if l.strip()]

    # --- Top 7 Investment Landmarks ---
    investment_landmarks = []
    inv_section = re.search(r'8️⃣ Top 7 Investment Landmarks.*?\n(.*?)\n_{5,}', content_dodd, re.DOTALL)
    if inv_section:
        items = re.split(r'\d+\.\s+', inv_section.group(1))
        for item in items:
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
                "name": name, "residential": res, "commercial": comm, "rental": rent, "growth": growth.strip('%')
            })

    # --- 48 Major Landmarks Map Data ---
    map_landmarks = []
    landmark_ids = []
    map_table = re.search(r'📍 Doddaballapura – 48 Landmarks Map Data\n(.*?)\n_{5,}', content_lat, re.DOTALL)
    if map_table:
        for line in map_table.group(1).strip().split('\n'):
            line = line.strip()
            if line.startswith('#') or not line: continue
            parts = re.split(r'\t|\s{2,}', line)
            if len(parts) >= 6:
                name = parts[2].strip()
                lat = float(parts[3])
                lng = float(parts[4])
                price_l = parse_price(parts[5])
                growth = parts[6].strip('%')
                
                lm_exists = await db.landmarks.find_one({"name": name, "city_id": city_id})
                if not lm_exists:
                    lm_id = uuid4()
                    await db.landmarks.insert_one({
                        "_id": lm_id, "name": name, "city_id": city_id,
                        "location": {"type": "Point", "coordinates": [lng, lat]}
                    })
                else:
                    lm_id = lm_exists["_id"]
                    await db.landmarks.update_one({"_id": lm_id}, {"$set": {"location": {"type": "Point", "coordinates": [lng, lat]}}})
                
                landmark_ids.append(lm_id)
                map_landmarks.append({
                    "name": name, "latitude": lat, "longitude": lng, "price": price_l, "growth": growth
                })

    # 4. Update City Document
    await db.cities.update_one(
        {"_id": city_id},
        {"$set": {
            "avg_commercial_plot_price": commercial,
            "avg_residential_plot_price": residential,
            "avg_rental_2bhk": rental_str,
            "economic_output": economic,
            "population": pop,
            "appreciation_potential_5yr": appreciation,
            "price_growth_history": history,
            "price_prediction": prediction,
            "political_infrastructure_agenda": {
                "mla": mla_m.group(1).strip() if mla_m else "",
                "mp": mp_m.group(1).strip() if mp_m else ""
            },
            "key_policies": policies,
            "amenities": amenities,
            "market_upcoming_projects": upcoming,
            "landmarks_id_list": landmark_ids,
            "updated_at": datetime.utcnow()
        }}
    )
    print(f"Updated City with {len(landmark_ids)} landmarks.")

    # 5. Update Market Intelligence
    intel_data = {
        "landmark_id": landmark_id, "location_type": "city",
        "avg_commercial_plot_price": commercial, "avg_residential_plot_price": residential,
        "avg_rental_2bhk": rental_str, "economic_output": economic, "population": pop,
        "appreciation_potential_5yr": appreciation,
        "growth_history": history, "growth_prediction": prediction,
        "amenities": amenities, "upcoming_projects": upcoming,
        "investment_landmarks": investment_landmarks, "map_landmarks": map_landmarks,
        "updated_at": datetime.utcnow()
    }
    await db.market_intelligence.update_one(
        {"landmark_id": landmark_id},
        {"$set": intel_data},
        upsert=True
    )
    print(f"Updated Market Intel with {len(investment_landmarks)} inv landmarks and {len(map_landmarks)} map points.")
    print("SUCCESS: Full synchronization complete.")

if __name__ == "__main__":
    asyncio.run(main())
