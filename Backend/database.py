import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

class Database:
    client: AsyncIOMotorClient = None
    
db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(MONGODB_URL)

async def close_mongo_connection():
    if db.client is not None:
        db.client.close()

def get_database():
    return db.client["glof_sentinel"]
