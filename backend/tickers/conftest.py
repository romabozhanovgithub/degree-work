import asyncio
from motor.core import AgnosticClient
import pytest
import pytest_asyncio

from app.core import settings
from app.repositories import BaseRepository, OrderRepository, TradeRepository
from app.db.client import get_client
from app.db.utils import connect_to_mongo, close_mongo_connection
from app.services import OrderService, TradeService


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def db_connect():
    await connect_to_mongo()
    yield
    await close_mongo_connection()


@pytest.fixture(autouse=True)
def db(db_connect):
    # Clear database before each test
    client: AgnosticClient = get_client()
    client.drop_database(settings.DB_NAME)
    yield
    client.drop_database(settings.DB_NAME)


# REPOSITORY FIXTURES
@pytest.fixture
def base_repository(db):
    return BaseRepository(collection_name="test_collection")


@pytest.fixture
def order_repository(db):
    return OrderRepository()


@pytest.fixture
def trade_repository(db):
    return TradeRepository()


# SERVICE FIXTURES
@pytest.fixture
def order_service(order_repository):
    return OrderService(repository=order_repository)


@pytest.fixture
def trade_service(trade_repository):
    return TradeService(repository=trade_repository)


# SCHEMA FIXTURES
@pytest.fixture
def order_data():
    order = {
        "symbol": "test",
        "price": "1.0",
        "init_qty": "1.0",
        "type": "market",
        "side": "buy",
        "user_id": "646be16ba7f9c69f0bdf2bc5",
    }
    return order


@pytest.fixture
def trade_data():
    trade = {
        "symbol": "test",
        "orders": ["646be16ba7f1c69f0bdf2bc5", "646be16ba7f1c69f0bdf2bc6"],
        "price": "1.0",
        "qty": "1.0",
        "comission": "0.1",
        "users": [
            {
                "user_id": "646be16ba7f9c69f0bdf2bc5",
                "side": "buy",
            },
            {
                "user_id": "646be16ba7f9c69f0bdf2bc6",
                "side": "sell",
            },
        ],
    }
    return trade
