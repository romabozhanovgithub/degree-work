import uuid
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


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(100), primary_key=True, index=True, default=uuid.uuid4)
    ticker = Column(String(10))
    price = Column(DECIMAL(10, 0))
    volume = Column(Float)
    type = Column(String(10))
    datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Many-to-one relationship
    user_id = Column(String(100), ForeignKey("users.id"))
    user = relationship("User", back_populates="orders")
