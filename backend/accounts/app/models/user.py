from sqlalchemy import DECIMAL, Boolean, Column, ForeignKey, String
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
    is_active = Column(Boolean, default=True)

    # One-to-Many relationship
    balance = relationship("UserBalance", back_populates="user")

    def __init__(self, email: str, first_name: str, last_name: str, hashed_password: str):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.hashed_password = hashed_password
        
        for ticker in ["AAPL", "BTC", "USD"]:
            self._init_balance(ticker)

    def _init_balance(self, name: str, volume: float = 0.0):
        self.balance.append(UserBalance(name=name, volume=volume))

    def __str__(self):
        return f"User(id={self.id}, email={self.email})"


class UserBalance(Base):
    __tablename__ = "user_balance"

    id = Column(String(100), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=True, default="")
    volume = Column(DECIMAL(10, 4), default=0)

    # Many-to-One relationship
    user_id = Column(String(100), ForeignKey("users.id"))
    user = relationship("User", back_populates="balance")
