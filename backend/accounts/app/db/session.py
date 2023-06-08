from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.db.base import engine


async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
