import asyncio
from app.db.mongodb import init_db
from app.models.landmark import Landmark
from app.models.market_intelligence import MarketIntelligence

async def seed():
    await init_db()
    
    # 1. Find or Create Bengaluru Landmark
    landmark = await Landmark.find_one(Landmark.name == "Bengaluru")
    if not landmark:
        landmark = Landmark(
            name="Bengaluru",
            city="Karnataka",
            zone="Metro Region",
            description="Silicon Valley of India",
            latitude=12.9716,
            longitude=77.5946
        )
        await landmark.insert()
        print(f"Created Landmark: {landmark.name} ({landmark.id})")
    else:
        print(f"Found Landmark: {landmark.name} ({landmark.id})")

    # 2. Prepare Market Intelligence Data
    intelligence_data = {
        "landmark_id": landmark.id,
        "overview": "Bengaluru is no longer just India’s Silicon Valley — it’s a city where tradition and tech grow side by side, shaping one of the country’s most dynamic real estate markets. From the early morning filter coffee culture in Basavanagudi to the fast-paced startup hubs of Whitefield and Outer Ring Road, every pocket of the city tells a different growth story. With expanding Metro corridors, Peripheral Ring Road momentum, and constant inward migration of professionals, demand is deeply rooted across segments — especially for plotted developments on the outskirts and premium apartments within the core.",
        "avg_commercial_plot_price": 19000000, # Mid of 1.6-2.2 Cr -> 1.9 Cr
        "avg_residential_plot_price": 10250000, # Mid of 85L-1.2Cr -> 1.025 Cr
        "avg_rental_2bhk": 26500, # Mid of 18k-35k -> 26.5k
        "economic_output": "₹8 – ₹10 Lakh Crores annually",
        "population": "~1.4 Crores",
        "appreciation_potential_5yr": "40% – 55%",
        "growth_history": [
            {"year": 2020, "price": 55, "reason": "Pandemic slowdown"},
            {"year": 2021, "price": 65, "reason": "IT recovery"},
            {"year": 2022, "price": 75, "reason": "Startup boom"},
            {"year": 2023, "price": 90, "reason": "Metro expansion + demand surge"},
            {"year": 2024, "price": 105, "reason": "Infrastructure growth"},
            {"year": 2025, "price": 110, "reason": "Strong investor confidence"}
        ],
        "growth_prediction": [
            {"year": 2026, "price": 120, "reason": "Metro Phase 2"},
            {"year": 2027, "price": 130, "reason": "Peripheral growth"},
            {"year": 2028, "price": 140, "reason": "Rental peak demand"},
            {"year": 2029, "price": 150, "reason": "Commercial expansion"},
            {"year": 2030, "price": 160, "reason": "Infrastructure maturity"},
            {"year": 2031, "price": 175, "reason": "Global city positioning"} # 1.7-1.8 -> 1.75
        ],
        "political_agenda": {
            "mla": "R. Ashoka, Ramalinga Reddy, Priya Krishna, K. Gopalaiah, A. C. Srinivasa (Major Constituencies)",
            "mp": "Tejasvi Surya (South), P. C. Mohan (Central), Shobha Karandlaje (North)",
            "governance": "BBMP & BDA",
            "focus": [
                "Metro Phase 2 & 3 expansion",
                "Peripheral Ring Road (PRR)",
                "Suburban Rail Project",
                "Traffic decongestion corridors",
                "Smart City upgrades"
            ]
        },
        "amenities": [
            "Global IT parks (Whitefield, ORR, Electronic City)",
            "International schools & universities",
            "Multi-specialty hospitals",
            "Metro + airport connectivity",
            "High rental demand zones",
            "Premium lifestyle infrastructure"
        ],
        "upcoming_projects": [
            "Metro Phase 2 & 3 expansion",
            "Peripheral Ring Road (PRR)",
            "Bengaluru Suburban Rail",
            "Satellite town development",
            "IT corridor expansion (North & East Bengaluru)"
        ],
        "investment_landmarks": [
            {"name": "Whitefield", "residential": 120, "commercial": 220, "rental": "30K", "growth": 50},
            {"name": "Electronic City", "residential": 90, "commercial": 160, "rental": "22K", "growth": 45},
            {"name": "Sarjapur Road", "residential": 110, "commercial": 190, "rental": "28K", "growth": 48},
            {"name": "Devanahalli (Airport Belt)", "residential": 80, "commercial": 150, "rental": "20K", "growth": 52},
            {"name": "Yelahanka", "residential": 95, "commercial": 170, "rental": "25K", "growth": 46},
            {"name": "Kanakapura Road", "residential": 90, "commercial": 160, "rental": "22K", "growth": 44},
            {"name": "Hennur Road", "residential": 100, "commercial": 180, "rental": "27K", "growth": 47}
        ],
        "map_landmarks": [
            {"name": "MG Road", "price": 350, "growth": 30},
            {"name": "Indiranagar", "price": 320, "growth": 32},
            {"name": "Koramangala", "price": 300, "growth": 33},
            {"name": "Jayanagar", "price": 280, "growth": 30},
            {"name": "Whitefield", "price": 120, "growth": 50},
            {"name": "Electronic City", "price": 90, "growth": 45},
            {"name": "Sarjapur Road", "price": 110, "growth": 48},
            {"name": "Marathahalli", "price": 130, "growth": 44},
            {"name": "Bellandur", "price": 140, "growth": 45},
            {"name": "HSR Layout", "price": 220, "growth": 35},
            {"name": "BTM Layout", "price": 180, "growth": 36},
            {"name": "Banashankari", "price": 200, "growth": 32},
            {"name": "Yelahanka", "price": 95, "growth": 46},
            {"name": "Hebbal", "price": 150, "growth": 42},
            {"name": "Hennur", "price": 100, "growth": 47},
            {"name": "Thanisandra", "price": 110, "growth": 46},
            {"name": "KR Puram", "price": 95, "growth": 45},
            {"name": "Old Madras Road", "price": 100, "growth": 44},
            {"name": "Devanahalli", "price": 80, "growth": 52},
            {"name": "Airport Road", "price": 130, "growth": 48},
            {"name": "Kanakapura Road", "price": 90, "growth": 44},
            {"name": "Mysore Road", "price": 85, "growth": 42},
            {"name": "Tumkur Road", "price": 95, "growth": 46},
            {"name": "Peenya", "price": 120, "growth": 43},
            {"name": "Rajajinagar", "price": 250, "growth": 30},
            {"name": "Malleshwaram", "price": 260, "growth": 30},
            {"name": "Basavanagudi", "price": 240, "growth": 29},
            {"name": "Kengeri", "price": 80, "growth": 45},
            {"name": "Nagarbhavi", "price": 120, "growth": 42},
            {"name": "RR Nagar", "price": 110, "growth": 43},
            {"name": "Uttarahalli", "price": 95, "growth": 44},
            {"name": "Bannerghatta Road", "price": 130, "growth": 45},
            {"name": "Jigani", "price": 75, "growth": 48},
            {"name": "Attibele", "price": 70, "growth": 50},
            {"name": "Anekal", "price": 65, "growth": 52},
            {"name": "Chandapura", "price": 70, "growth": 49},
            {"name": "Bagalur", "price": 80, "growth": 50},
            {"name": "Hoskote", "price": 85, "growth": 48},
            {"name": "Budigere Cross", "price": 90, "growth": 49},
            {"name": "Varthur", "price": 120, "growth": 47},
            {"name": "Panathur", "price": 130, "growth": 46},
            {"name": "Kadugodi", "price": 110, "growth": 48},
            {"name": "Nagawara", "price": 140, "growth": 44},
            {"name": "Kalyan Nagar", "price": 160, "growth": 40},
            {"name": "Cox Town", "price": 220, "growth": 32},
            {"name": "Frazer Town", "price": 230, "growth": 31},
            {"name": "Shivajinagar", "price": 250, "growth": 30},
            {"name": "Yeshwanthpur", "price": 140, "growth": 43}
        ]
    }

    intelligence = await MarketIntelligence.find_one(MarketIntelligence.landmark_id == landmark.id)
    if intelligence:
        await intelligence.update({"$set": intelligence_data})
        print("Updated existing Bengaluru Market Intelligence data.")
    else:
        intelligence = MarketIntelligence(**intelligence_data)
        await intelligence.insert()
        print("Inserted new Bengaluru Market Intelligence data.")

if __name__ == "__main__":
    asyncio.run(seed())
