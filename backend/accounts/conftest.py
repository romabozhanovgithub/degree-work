import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session
from app.db.base import Base, engine
from app.repositories import UserRepository, BalanceRepository
from app.services import AuthService, EmailService, PaymentService


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def user_repository(session) -> UserRepository:
    return UserRepository(session)


@pytest_asyncio.fixture
async def balance_repository(session) -> BalanceRepository:
    return BalanceRepository(session)


@pytest_asyncio.fixture
async def auth_service(user_repository) -> AuthService:
    return AuthService(user_repository)


@pytest_asyncio.fixture
async def email_service(user_repository) -> EmailService:
    return EmailService(user_repository)


@pytest_asyncio.fixture
async def payment_service(balance_repository) -> PaymentService:
    return PaymentService(balance_repository)
