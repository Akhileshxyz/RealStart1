import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

async def send_otp(phone: str) -> str:
    url = f"{settings.FACTOR_BASE_URL}/{settings.FACTOR_API_KEY}/SMS/{phone}/AUTOGEN"
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url)
        data = response.json()
        if data.get("Status") != "Success":
            logger.error(f"2Factor send OTP failed: {data}")
            raise Exception(f"Failed to send OTP: {data.get('Details', 'Unknown error')}")
        return data["Details"]

async def verify_otp(session_id: str, otp: str) -> bool:
    url = f"{settings.FACTOR_BASE_URL}/{settings.FACTOR_API_KEY}/SMS/VERIFY/{session_id}/{otp}"
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url)
        data = response.json()
        return data.get("Status") == "Success" and data.get("Details") == "OTP Matched"
