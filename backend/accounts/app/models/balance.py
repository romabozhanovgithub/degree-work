from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import relationship

from app.db import Base
from app.models.mixins import UUIDMixin


class Balance(UUIDMixin, Base):
    __tablename__ = "balances"

    user_id = Column(String(100), ForeignKey("users.id"), nullable=False)
    currency = Column(String(100), nullable=False)
    amount = Column(Numeric(precision=10, scale=2), nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship(
        "User",
        back_populates="balances",
        lazy="selectin",
    )

    def __str__(self):
        return f"Balance(id={self.id}, user_id={self.user_id}, currency={self.currency}, amount={self.amount})"  # noqa: E501
