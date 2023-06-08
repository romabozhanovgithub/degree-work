from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base

from app.core import settings


engine = create_async_engine(settings.DB_URL, echo=False)
Base = declarative_base()
