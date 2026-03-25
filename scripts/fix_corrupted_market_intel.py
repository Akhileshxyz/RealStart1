import asyncio
from uuid import UUID
from app.db.mongodb import init_db
from app.models.market_intelligence import MarketIntelligence
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def inspect_and_fix_corrupted_records():
    """Find and fix corrupted MarketIntelligence records"""
    await init_db()
    
    logger.info("Fetching all market intelligence records...")
    all_records = await MarketIntelligence.find_all().to_list()
    logger.info(f"Found {len(all_records)} records")
    
    corrupted_count = 0
    
    for record in all_records:
        try:
            # Try to serialize the record
            record.model_dump(mode='json')
            logger.info(f"✓ Record {record.landmark_id} is valid")
        except (UnicodeDecodeError, ValueError, TypeError) as e:
            corrupted_count += 1
            logger.error(f"✗ Record {record.landmark_id} is corrupted: {e}")
            
            # Inspect each field
            fields_to_check = [
                'overview', 'economic_output', 'population', 
                'appreciation_potential_5yr', 'amenities', 'upcoming_projects'
            ]
            
            for field_name in fields_to_check:
                field_value = getattr(record, field_name, None)
                if field_value and isinstance(field_value, (str, bytes)):
                    try:
                        if isinstance(field_value, bytes):
                            logger.error(f"  - Field '{field_name}' contains binary data")
                            # Try to decode or replace
                            try:
                                decoded = field_value.decode('utf-8', errors='replace')
                                setattr(record, field_name, decoded)
                                logger.info(f"  - Decoded '{field_name}' with replacement chars")
                            except Exception as decode_err:
                                logger.error(f"  - Failed to decode '{field_name}': {decode_err}")
                                setattr(record, field_name, "")
                        elif isinstance(field_value, str):
                            # Check if string contains non-UTF8 bytes
                            field_value.encode('utf-8')
                    except (UnicodeDecodeError, UnicodeEncodeError) as field_err:
                        logger.error(f"  - Field '{field_name}' has encoding issue: {field_err}")
                        setattr(record, field_name, "")
            
            # Try to save the fixed record
            try:
                await record.save()
                logger.info(f"  → Fixed and saved record {record.landmark_id}")
            except Exception as save_err:
                logger.error(f"  → Failed to save fixed record: {save_err}")
                logger.error(f"  → Consider deleting record {record.id} manually")
    
    if corrupted_count == 0:
        logger.info("✓ No corrupted records found!")
    else:
        logger.warning(f"Found and attempted to fix {corrupted_count} corrupted record(s)")

if __name__ == "__main__":
    asyncio.run(inspect_and_fix_corrupted_records())
