from datetime import datetime
from sqlalchemy import (
    DECIMAL,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    String
)
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.utils import uuid4


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(100), primary_key=True, index=True, default=uuid4)
    ticker = Column(String(10))
    price = Column(DECIMAL(10, 4))
    volume = Column(DECIMAL(10, 4))
    type = Column(String(10))
    datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Many-to-one relationship
    user_id = Column(String(100), ForeignKey("users.id"))
    user = relationship("User", back_populates="orders")
