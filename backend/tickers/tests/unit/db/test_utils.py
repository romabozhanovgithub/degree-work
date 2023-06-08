from motor.motor_asyncio import AsyncIOMotorClient
import pytest

from app.db.client import get_client
from app.db.utils import connect_to_mongo


@pytest.mark.asyncio
async def test_connect_to_mongo():
    await connect_to_mongo()
    client = get_client()
    assert isinstance(client, AsyncIOMotorClient)
