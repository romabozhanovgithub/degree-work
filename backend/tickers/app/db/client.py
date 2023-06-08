from motor.motor_asyncio import AsyncIOMotorClient

from app.db.database import db


def get_client() -> AsyncIOMotorClient:
    return db.client
