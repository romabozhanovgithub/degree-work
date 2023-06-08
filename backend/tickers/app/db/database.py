from motor.motor_asyncio import AsyncIOMotorClient


class Database:
    client: AsyncIOMotorClient = None


db = Database()
