from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from beanie import Document
from pydantic import Field

class PriceHistory(Document):
    """Historical price data for localities - for trend graphs"""
    id: UUID = Field(default_factory=uuid4)

    # Reference
    landmark_id: UUID
    locality_name: str
    city: str

    # Time period
    year: int
    quarter: int  # 1-4
    month: int  # 1-12
    period_start: datetime
    period_end: datetime

    # Price data
    avg_price_per_sqft: float
    median_price_per_sqft: Optional[float] = None
    min_price_per_sqft: Optional[float] = None
    max_price_per_sqft: Optional[float] = None

    # Volume data
    total_transactions: int = 0

    # Property type breakdown (optional)
    apartment_avg_price: Optional[float] = None
    villa_avg_price: Optional[float] = None
    plot_avg_price: Optional[float] = None

    # Growth metrics
    yoy_growth: Optional[float] = None  # Year-over-year % growth
    qoq_growth: Optional[float] = None  # Quarter-over-quarter % growth

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "price_history"
        indexes = [
            "landmark_id",
            "year",
            "quarter",
            "period_start"
        ]
