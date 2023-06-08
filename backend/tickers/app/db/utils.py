from motor.motor_asyncio import AsyncIOMotorClient

from app.core import settings
from app.db.database import db


async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.DB_URL)


async def close_mongo_connection():
    db.client.close()
