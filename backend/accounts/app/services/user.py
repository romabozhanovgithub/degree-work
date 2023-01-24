from decimal import Decimal
from typing import Any
from sqlalchemy.orm import Session

from app.models import User, UserBalance


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def update_balance_by_orders(
        self, orders: list[dict[str, Any]], by_user: User = None
    ) -> None:
        """
        Update balance for user. Only for orders with type "SELL".
        """

        for order in orders:
            user: User = order["user"]
            price: Decimal = order["price"]
            volume: float = order["volume"]

            if by_user is None or by_user != user:
                user.balance += price * volume
            self.db.add(user)

    def get_user_balance(self, user: User, balance_name: str) -> UserBalance:
        """
        Get user balance by name.
        """

        for balance in user.balance:
            if balance.name == balance_name:
                return balance

        return None
