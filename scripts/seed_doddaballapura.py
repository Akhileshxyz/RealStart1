import asyncio
import shutil
from pathlib import Path
from datetime import datetime
from uuid import uuid4
from app.db.mongodb import init_db
from app.models.landmark import Landmark
from app.models.market_intelligence import MarketIntelligence

async def seed():
    await init_db()
    
    # --- 1. CITY LEVEL: Doddaballapura ---
    city_landmark = await Landmark.find_one(Landmark.name == "Doddaballapura")
    if not city_landmark:
        city_landmark = Landmark(
            name="Doddaballapura",
            city="Bangalore Rural",
            zone="North Bangalore",
            description="Industrial growth corridor of North Bengaluru",
            latitude=13.2924,
            longitude=77.5342,
            location={"type": "Point", "coordinates": [77.5342, 13.2924]}
        )
        await city_landmark.insert()
        print(f"Created City Landmark: {city_landmark.name} ({city_landmark.id})")
    else:
        print(f"Found City Landmark: {city_landmark.name} ({city_landmark.id})")

    # --- 2. AREA LEVEL: Near Doddaballapura Bus Stand ---
    area_name = "Near Doddaballapura Bus Stand"
    area_landmark = await Landmark.find_one(Landmark.name == area_name)
    if not area_landmark:
        area_landmark = Landmark(
            name=area_name,
            city="Bangalore Rural",
            zone="North Bangalore",
            description="The heart of Doddaballapura and main transit hub",
            latitude=13.293133,
            longitude=77.542108,
            location={"type": "Point", "coordinates": [77.542108, 13.293133]}
        )
        await area_landmark.insert()
        print(f"Created Area Landmark: {area_landmark.name} ({area_landmark.id})")
    else:
        print(f"Found Area Landmark: {area_landmark.name} ({area_landmark.id})")

    # --- 3. SEED AREA MARKET INTELLIGENCE ---
    area_intel_data = {
        "landmark_id": area_landmark.id,
        "parent_landmark_id": city_landmark.id,
        "location_type": "area",
        "overview": "The Near Doddaballapura Bus Stand area is the heartbeat of the town. It's the main transport hub where intercity and intracity buses start and end, bringing constant footfall - students, workers, visitors, and traders. Because of this central role, residential and commercial plots here command premium demand. Road connectivity to highways and city centers makes this zone especially attractive for both investors and home buyers.",
        "avg_commercial_plot_price": 6000000,
        "avg_residential_plot_price": 5500000,
        "avg_rental_2bhk": 13500,
        "economic_output": "High commercial activity and transit hub",
        "population": "High footfall (transit hub)",
        "appreciation_potential_5yr": "~30%",
        "growth_history": [
            {"year": 2020, "price": 20, "reason": "Market was slow post-pandemic reset, lesser investor interest."},
            {"year": 2021, "price": 25, "reason": "Basic commuter demand returned; office/government jobs restarted."},
            {"year": 2022, "price": 30, "reason": "Road connectivity talks (STRR & highways) boosted confidence."},
            {"year": 2023, "price": 36, "reason": "Industrial interest & Devanahalli influence grew."},
            {"year": 2024, "price": 45, "reason": "Foxconn & other manufacturers’ news raised investor interest."},
            {"year": 2025, "price": 50, "reason": "Higher visibility from infrastructure maps & better access."},
            {"year": 2026, "price": 55, "reason": "Bus Stand area solidified as premium transit + living spot."}
        ],
        "growth_prediction": [
            {"year": 2026, "price": 55, "reason": "Current price plateau with strong footfall."},
            {"year": 2027, "price": 58, "reason": "STRR nearing completion improves connectivity."},
            {"year": 2028, "price": 62, "reason": "Local commercial activity increases."},
            {"year": 2029, "price": 65, "reason": "Residential demand rises with new services."},
            {"year": 2030, "price": 69, "reason": "New facilities (schools/hospitals) open nearby."},
            {"year": 2031, "price": 72, "reason": "Mature urban footprint + investor confidence."}
        ],
        "political_agenda": {
            "mla": "Dheeraj Muniraju (BJP) - Doddaballapura Constituency",
            "mp": "Dr. K Sudhakar - Chikkaballapura Parliamentary Constituency",
            "governance": "Nagarasabha",
            "focus": [
                "Peripheral Ring Road (STRR) connectivity",
                "Bus Stand internal road widening & civic upgrades",
                "Drainage and pavement improvement"
            ]
        },
        "amenities": [
            "KSRTC / Bus Stand - Main transport hub",
            "Doddaballapura Railway Station - ~1.5-2 km (train access)",
            "National Highway Access (NH + SH junction) - quick access",
            "Local Market & Shops - daily needs & services",
            "Schools & Clinics - everyday living essentials"
        ],
        "upcoming_projects": [
            "Peripheral Ring Road (STRR) - final phases will uplift connectivity around Bus Stand.",
            "Bus Stand area internal road widening & civic upgrades - improving drainage and pavements.",
            "New Commercial Complex proposals - local traders and developers planning business hubs.",
            "Upgraded local amenities (play zones / healthcare / community spaces) - scheduled by urban council."
        ],
        "investment_landmarks": [
            {"name": "Gandhinagara residential belt", "residential": 52, "commercial": 58, "rental": "12K", "growth": 28},
            {"name": "Terinabeedi road extension", "residential": 50, "commercial": 55, "rental": "11K", "growth": 30},
            {"name": "Hemavathipete commercial spine", "residential": 55, "commercial": 65, "rental": "15K", "growth": 32},
            {"name": "Railway Station flank areas", "residential": 48, "commercial": 52, "rental": "10K", "growth": 35},
            {"name": "Main Market & Court Road stretch", "residential": 56, "commercial": 68, "rental": "16K", "growth": 29}
        ],
        "map_landmarks": []
    }

    area_intel = await MarketIntelligence.find_one(MarketIntelligence.landmark_id == area_landmark.id)
    if area_intel:
        # Update fields properly
        for key, value in area_intel_data.items():
            setattr(area_intel, key, value)
        await area_intel.save()
        print("Updated existing Area Market Intelligence data.")
    else:
        area_intel = MarketIntelligence(**area_intel_data)
        await area_intel.insert()
        print("Inserted new Area Market Intelligence data.")

    # --- 4. SEED CITY MARKET INTELLIGENCE ---
    city_intel_data = {
        "landmark_id": city_landmark.id,
        "parent_landmark_id": None,
        "location_type": "city",
        "overview": "Doddaballapura is rapidly transforming from a textile town into North Bengaluru's industrial growth corridor. With Foxconn manufacturing momentum, STRR connectivity, and Devanahalli influence, plotted developments are seeing strong mid-segment demand. Investors are entering before full infrastructure maturity - making 2026 a strategic accumulation phase.",
        "avg_commercial_plot_price": 3600000, 
        "avg_residential_plot_price": 2500000, 
        "avg_rental_2bhk": 11000, 
        "economic_output": "Rs. 10,000 - Rs. 12,000 Crores annually",
        "population": "~1.40 Lakhs",
        "appreciation_potential_5yr": "35% - 45%",
        "growth_history": [
            {"year": 2020, "price": 14, "reason": "Low demand phase, post-pandemic stagnation"},
            {"year": 2021, "price": 16, "reason": "Industrial activity recovery"},
            {"year": 2022, "price": 18, "reason": "Devanahalli influence spillover"},
            {"year": 2023, "price": 21, "reason": "STRR progress visibility"},
            {"year": 2024, "price": 23, "reason": "Foxconn land acquisition impact"},
            {"year": 2025, "price": 25, "reason": "Investor accumulation phase"}
        ],
        "growth_prediction": [
            {"year": 2026, "price": 27, "reason": "STRR near completion"},
            {"year": 2027, "price": 29, "reason": "Foxconn operations scaling"},
            {"year": 2028, "price": 32, "reason": "Rental demand from workforce"},
            {"year": 2029, "price": 34, "reason": "Commercial spillover growth"},
            {"year": 2030, "price": 36, "reason": "Infrastructure maturity"},
            {"year": 2031, "price": 40, "reason": "Full industrial ecosystem impact"}
        ],
        "political_agenda": {
            "mla": "Dheeraj Muniraju (BJP) - Doddaballapura Constituency",
            "mp": "Dr. K Sudhakar - Chikkaballapura Parliamentary Constituency",
            "governance": "Nagarasabha",
            "focus": [
                "STRR connectivity integration",
                "Industrial employment corridor",
                "Road widening & drainage upgrade",
                "Water supply strengthening for expansion zones"
            ]
        },
        "amenities": [
            "International School presence",
            "Multi-specialty Hospitals",
            "Direct highway access (NH-44 & STRR link)",
            "Railway connectivity",
            "Industrial zones & logistics hubs",
            "Proximity to International Airport"
        ],
        "upcoming_projects": [
            "STRR (Satellite Town Ring Road) - 2026 operational phase",
            "Foxconn Manufacturing Facility - phased expansion",
            "Industrial cluster expansion (logistics & warehousing)",
            "Road widening towards Devanahalli corridor",
            "Commercial complex proposals near main bus stand region"
        ],
        "investment_landmarks": [
            {"name": "Near TB Circle", "residential": 28, "commercial": 38, "rental": "12K", "growth": 40},
            {"name": "Jalappa College Road", "residential": 26, "commercial": 35, "rental": "11K", "growth": 37},
            {"name": "Railway Station Road", "residential": 27, "commercial": 39, "rental": "12K", "growth": 42},
            {"name": "Devanahalli Road Stretch", "residential": 29, "commercial": 41, "rental": "12-13K", "growth": 45},
            {"name": "Raghunathpura", "residential": 24, "commercial": 32, "rental": "10K", "growth": 35},
            {"name": "Kantanakunte", "residential": 23, "commercial": 30, "rental": "9-10K", "growth": 32},
            {"name": "Gauribidanur Road Belt", "residential": 25, "commercial": 34, "rental": "11K", "growth": 36}
        ],
        "map_landmarks": [
            {"name": "Near Doddaballapura Bus Stand", "price": 38, "growth": 32, "latitude": 13.293133, "longitude": 77.542108, "landmark_id": area_landmark.id},
            {"name": "Near Doddaballapura Railway Station", "price": 40, "growth": 34},
            {"name": "TB Circle", "price": 42, "growth": 35},
            {"name": "D-Cross", "price": 34, "growth": 30},
            {"name": "Marasandra", "price": 30, "growth": 28},
            {"name": "Bhashettyhalli", "price": 37, "growth": 32},
            {"name": "Apparel Park (Industrial)", "price": 48, "growth": 38},
            {"name": "Raghunathpura", "price": 32, "growth": 30},
            {"name": "Palanajogahalli", "price": 29, "growth": 28},
            {"name": "Kantanakunte", "price": 28, "growth": 27},
            {"name": "Thirumagondanahalli", "price": 27, "growth": 26},
            {"name": "Hadonahalli", "price": 26, "growth": 26},
            {"name": "Tubugere", "price": 27, "growth": 27},
            {"name": "Gaati", "price": 30, "growth": 28},
            {"name": "Basava Bhavana Circle", "price": 48, "growth": 38},
            {"name": "Kurubarahalli", "price": 29, "growth": 28},
            {"name": "Kodigehalli", "price": 35, "growth": 31},
            {"name": "Rameshwara", "price": 31, "growth": 29},
            {"name": "Belavangala", "price": 28, "growth": 27},
            {"name": "Neralagatta", "price": 27, "growth": 26},
            {"name": "Maralenahalli", "price": 29, "growth": 28},
            {"name": "Sasalu", "price": 28, "growth": 27},
            {"name": "Aarudi", "price": 30, "growth": 28},
            {"name": "Jalappa College", "price": 37, "growth": 32},
            {"name": "Muthyalamma Temple", "price": 31, "growth": 29},
            {"name": "Dargajogahalli", "price": 30, "growth": 28},
            {"name": "Taluk Office", "price": 40, "growth": 34},
            {"name": "Kongadiyappa College", "price": 38, "growth": 33},
            {"name": "Bhuvaneshwarinagara", "price": 36, "growth": 31},
            {"name": "Terinabeedi", "price": 35, "growth": 30},
            {"name": "Aralumallige", "price": 33, "growth": 29},
            {"name": "Madure", "price": 32, "growth": 28},
            {"name": "Thammashettyhalli", "price": 31, "growth": 28},
            {"name": "Melekote", "price": 32, "growth": 28},
            {"name": "Alahalli", "price": 33, "growth": 29},
            {"name": "Majarehosalli", "price": 33, "growth": 29},
            {"name": "Honnagatta", "price": 31, "growth": 28},
            {"name": "Gouribidanur Road", "price": 36, "growth": 31},
            {"name": "Chikkatumakur", "price": 34, "growth": 29},
            {"name": "Makalidurga", "price": 30, "growth": 27},
            {"name": "Muthsandra", "price": 31, "growth": 28},
            {"name": "Hamam", "price": 29, "growth": 27},
            {"name": "Thippapura", "price": 30, "growth": 28},
            {"name": "Chikkaballapura Road", "price": 38, "growth": 32},
            {"name": "Devanahalli Road", "price": 42, "growth": 35},
            {"name": "Chapparadakallu", "price": 32, "growth": 29},
            {"name": "Nandi Hills Road", "price": 40, "growth": 34},
            {"name": "Rajagatta", "price": 37, "growth": 32}
        ]
    }

    city_intel = await MarketIntelligence.find_one(MarketIntelligence.landmark_id == city_landmark.id)
    if city_intel:
        # Update fields properly
        for key, value in city_intel_data.items():
            setattr(city_intel, key, value)
        await city_intel.save()
        print("Updated existing City Market Intelligence data.")
    else:
        city_intel = MarketIntelligence(**city_intel_data)
        await city_intel.insert()
        print("Inserted new City Market Intelligence data.")

    # Copy default locality hero image (uploads/Frame 2147225768.png) → /uploads/localities/{city_id}.png
    root = Path(__file__).resolve().parent.parent
    src = root / "uploads" / "Frame 2147225768.png"
    if src.is_file():
        dest_dir = root / "uploads" / "localities"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{city_landmark.id}.png"
        shutil.copy2(src, dest)
        city_landmark.image_url = f"/uploads/localities/{city_landmark.id}.png"
        city_landmark.updated_at = datetime.utcnow()
        await city_landmark.save()
        print(f"Set city image_url -> {city_landmark.image_url}")

if __name__ == "__main__":
    asyncio.run(seed())
