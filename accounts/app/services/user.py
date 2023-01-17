from decimal import Decimal
from typing import Any
from sqlalchemy.orm import Session

from app.models import User


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def update_balance_by_orders(
        self, orders: list[dict[str, Any]]
    ) -> None:
        """
        Update balance for user. Only for orders with type "SELL".
        """

        for order in orders:
            user: User = order["user"]
            price: Decimal = order["price"]
            volume: float = order["volume"]

            user.balance += price * volume
            self.db.add(user)
