import asyncio
from uuid import uuid4
from app.db.mongodb import init_db
from app.models.landmark import Landmark
from app.models.market_intelligence import MarketIntelligence

async def seed():
    await init_db()
    
    # 1. Find or Create Doddaballapura Landmark
    landmark = await Landmark.find_one(Landmark.name == "Doddaballapura")
    if not landmark:
        landmark = Landmark(
            name="Doddaballapura",
            city="Bangalore Rural",
            zone="North Bangalore",
            description="Industrial growth corridor of North Bengaluru",
            latitude=13.2924,
            longitude=77.5342
        )
        await landmark.insert()
        print(f"Created Landmark: {landmark.name} ({landmark.id})")
    else:
        print(f"Found Landmark: {landmark.name} ({landmark.id})")

    # 2. Prepare Market Intelligence Data
    intelligence_data = {
        "landmark_id": landmark.id,
        "overview": "Doddaballapura is rapidly transforming from a textile town into North Bengaluru’s industrial growth corridor. With Foxconn manufacturing momentum, STRR connectivity, and Devanahalli influence, plotted developments are seeing strong mid-segment demand. Investors are entering before full infrastructure maturity — making 2026 a strategic accumulation phase.",
        "avg_commercial_plot_price": 3600000, # 36 Lakhs
        "avg_residential_plot_price": 2500000, # 25 Lakhs
        "avg_rental_2bhk": 11000, # Average of 9k-13k
        "economic_output": "₹10,000 – ₹12,000 Crores annually",
        "population": "~1.40 Lakhs",
        "appreciation_potential_5yr": "35% – 45%",
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
            "mla": "Dheeraj Muniraju (BJP) – Doddaballapura Constituency",
            "mp": "Dr. K Sudhakar – Chikkaballapura Parliamentary Constituency",
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
            "STRR (Satellite Town Ring Road) – 2026 operational phase",
            "Foxconn Manufacturing Facility – phased expansion",
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
            {"name": "Near Doddaballapura Bus Stand", "price": 38, "growth": 32},
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

    intelligence = await MarketIntelligence.find_one(MarketIntelligence.landmark_id == landmark.id)
    if intelligence:
        await intelligence.update({"$set": intelligence_data})
        print("Updated existing Market Intelligence data.")
    else:
        intelligence = MarketIntelligence(**intelligence_data)
        await intelligence.insert()
        print("Inserted new Market Intelligence data.")

if __name__ == "__main__":
    asyncio.run(seed())
