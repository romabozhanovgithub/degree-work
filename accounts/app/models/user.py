from sqlalchemy import DECIMAL, Boolean, Column, String
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.utils import uuid4


class User(Base):
    __tablename__ = "users"

    id = Column(String(100), primary_key=True, default=uuid4)
    first_name = Column(String(100), nullable=True, default="")
    last_name = Column(String(100), nullable=True, default="")
    email = Column(String(250), unique=True, index=True)
    hashed_password = Column(String(250))
    balance = Column(DECIMAL(10, 4), default=0)
    is_active = Column(Boolean, default=True)

    # One-to-many relationship
    orders = relationship("Order", back_populates="user")
