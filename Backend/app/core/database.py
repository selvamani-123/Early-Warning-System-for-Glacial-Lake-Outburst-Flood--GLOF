from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import certifi
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongo():
    logger.info("Connecting to MongoDB...")
    db.client = AsyncIOMotorClient(settings.mongodb_uri, tlsCAFile=certifi.where())
    db.db = db.client[settings.db_name]
    logger.info("Connected to MongoDB!")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        logger.info("Closed MongoDB connection.")

def get_db():
    return db.db
