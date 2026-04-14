import asyncio
import os
import sys
from datetime import datetime
from uuid import uuid4

# Add project root to path
sys.path.append(os.getcwd())

from app.db.mongodb import init_db
from app.models.blog import Blog

async def seed_blogs():
    print("Initializing Database...")
    await init_db()

    print("--- Seeding Blogs ---")
    
    blogs_data = [
        {
            "slug": "tips-to-invest-in-real-estate-india",
            "title": "Tips To Invest in Real Estate India",
            "subtitle": "A Comprehensive Guide to the 2026 Property Market",
            "description": "Expert advice on navigating the Indian real estate market after the 2026 budget.",
            "content": "<article><h2>The Future of Investment</h2><p>Real estate investment in India is evolving. With the 2026 budget focus on infrastructure, several corridors are emerging as gold mines for investors...</p></article>",
            "category": "Investment",
            "tag": "Featured",
            "tags": ["Investment", "Finance", "2026"],
            "image_url": "https://api.realstart.in/storage/blogs/img_21.png",
            "author_name": "Pavan Dhananjaya",
            "author_avatar_url": "https://api.realstart.in/storage/avatars/pavan.png",
            "author_role": "UI/UX Designer",
            "seo": {
                "title": "Real Estate Investment Tips India 2026 | RealStart",
                "description": "Expert advice on navigating the Indian real estate market after the 2026 budget.",
                "keywords": ["investment", "india", "real estate", "budget 2026"]
            },
            "is_published": True,
            "published_at": datetime.utcnow()
        },
        {
            "slug": "emerging-trends-commercial-spaces",
            "title": "Emerging Trends in Commercial Spaces",
            "subtitle": "How Hybrid Work is Shaping the Future of Offices",
            "description": "Why hybrid work models are shaping the future of offices across metro cities.",
            "content": "<article><h2>The Office of Tomorrow</h2><p>Commercial real estate is no longer just about floor space. It's about flexibility, well-being, and technology integration...</p></article>",
            "category": "Commercial",
            "tag": "Trending",
            "tags": ["Commercial", "Trends", "Finance"],
            "image_url": "https://api.realstart.in/storage/blogs/img_22.png",
            "author_name": "Antigravity AI",
            "author_role": "Market Analyst",
            "seo": {
                "title": "Commercial Real Estate Trends 2026",
                "description": "Discover how the future of office space is being redefined.",
                "keywords": ["commercial", "trends", "office space"]
            },
            "is_published": True,
            "published_at": datetime.utcnow()
        },
        {
            "slug": "sustainable-homes-in-the-suburbs",
            "title": "Sustainable Homes in the Suburbs",
            "subtitle": "Eco-Friendly Living is Gaining Massive Traction",
            "description": "Why eco-friendly developments are gaining massive traction in suburban areas.",
            "content": "<article><h2>Greener Living</h2><p>Homebuyers are increasingly looking for energy-efficient homes, rainwater harvesting, and solar power integration as standard features...</p></article>",
            "category": "Residential",
            "tag": "New",
            "tags": ["Sustainability", "Residential", "Trends"],
            "image_url": "https://api.realstart.in/storage/blogs/img_23.png",
            "author_name": "Pavan Dhananjaya",
            "author_role": "Lead Designer",
            "seo": {
                "title": "Sustainable Suburban Living | RealStart",
                "description": "Exploring the rise of eco-friendly residential projects in the suburbs.",
                "keywords": ["sustainability", "residential", "suburbs"]
            },
            "is_published": True,
            "published_at": datetime.utcnow()
        },
        {
            "slug": "budget-highlights-for-home-buyers-2026",
            "title": "Budget Highlights for Home Buyers 2026",
            "subtitle": "Key Takeaways from the Latest Finance Bill",
            "description": "Understanding tax benefits and interest rate subsidies for new homeowners.",
            "content": "<article><h2>Financial Roadmap for Homebuyers</h2><p>The 2026 budget has introduced several incentives for first-time homebuyers. From interest subventions to increased tax deductions under Section 24...</p></article>",
            "category": "Finance",
            "tags": ["Finance", "Residential", "Tax"],
            "image_url": "https://api.realstart.in/storage/blogs/img_24.png",
            "author_name": "Finance Desk",
            "author_role": "Content Strategist",
            "seo": {
                "title": "Budget 2026: Homebuyer Benefits",
                "description": "Detailed analysis of tax breaks and subsidies for homebuyers in current budget.",
                "keywords": ["finance", "budget", "tax", "real estate"]
            },
            "is_published": True,
            "published_at": datetime.utcnow()
        },
        {
            "slug": "smart-home-technology-evolution",
            "title": "Smart Home Technology Evolution",
            "subtitle": "From Voice Control to Integrated Ecosystems",
            "description": "How the next generation of smart homes will manage energy and security autonomously.",
            "content": "<article><h2>Intelligence Embedded</h2><p>Smart homes are moving beyond simple gadgets to fully integrated AI-driven ecosystems that learn inhabitant behavior to optimize comfort and safety...</p></article>",
            "category": "Technology",
            "tags": ["Technology", "Residential", "Sustainability"],
            "image_url": "https://api.realstart.in/storage/blogs/img_25.png",
            "author_name": "Antigravity AI",
            "author_role": "Tech Enthusiast",
            "seo": {
                "title": "Future of Smart Homes 2026",
                "description": "Explore the latest in smart home technology and automation.",
                "keywords": ["technology", "smart home", "ia", "sustainability"]
            },
            "is_published": True,
            "published_at": datetime.utcnow()
        }
    ]

    for data in blogs_data:
        # Check if already exists
        existing = await Blog.find_one(Blog.slug == data["slug"])
        if not existing:
            blog = Blog(**data)
            await blog.insert()
            print(f"Created Blog: {blog.title}")
        else:
            print(f"Blog '{data['title']}' already exists, skipping.")

    print("\nSeeding Complete!")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_blogs())
