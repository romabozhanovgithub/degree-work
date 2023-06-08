from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, String, func
from sqlalchemy.orm import relationship

from app.db import Base
from app.models.mixins import UUIDMixin


class User(UUIDMixin, Base):
    __tablename__ = "users"

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    password = Column(String(100), nullable=True)
    is_verified = Column(Boolean, default=False)
    is_google_account = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    balances = relationship(
        "Balance",
        back_populates="user",
        lazy="selectin",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "password IS NOT NULL OR is_google_account = true",
            name="password_required_if_not_google",
        ),
        CheckConstraint(
            "password IS NULL OR is_google_account = false",
            name="password_not_required_if_google",
        ),
    )

    def __str__(self):
        return f"User(id={self.id}, email={self.email})"
