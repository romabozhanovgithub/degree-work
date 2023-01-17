from typing import Any, Tuple
from sqlalchemy.orm import Query, Session

from app.models import User, Order


class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def get_orders_by_ticker_and_type(
        self, ticker: str, type: str
    ) -> Query:
        """
        Get orders by ticker and type.
        """

        return self.db.query(Order).filter(
            Order.ticker == ticker, Order.type == type
        )

    def get_orders_by_user(self, user: User) -> Query:
        """
        Get orders by user.
        """

        return self.db.query(Order).filter(Order.user == user)

    def get_last_order(self, type: str, limit: int = 10) -> Query:
        """
        Get last order.
        """

        return self.db.query(Order).filter(
            Order.type == type
        ).order_by(
            Order.price.desc()
        ).limit(limit)

    def update_orders(
        self, new_order: Order, orders: list[Order]
    ) -> Tuple[Order, list[dict[str, Any]]]:
        """
        Update orders for user.
        Return new order and list of Dicts with Users, Prices and Volumes.

        ```python
        >>> return new_order, [
            {
                "user": user,
                "price": order.price,
                "volume": order.volume,
            },
        ]
        ```
        """

        data = []

        if orders:
            order_data = {}
            for order in orders:
                if new_order.volume > order.volume:
                    new_order.volume -= order.volume
                    order.volume = 0
                    order.is_active = False
                    order_data = {
                        "user": order.user,
                        "price": order.price,
                        "volume": order.volume,
                    }
                elif new_order.volume < order.volume:
                    order.volume -= new_order.volume
                    new_order.volume = 0
                    new_order.is_active = False
                    order_data = {
                        "user": order.user,
                        "price": order.price,
                        "volume": order.volume,
                    }
                else:
                    order.volume = 0
                    order.is_active = False
                    new_order.volume = 0
                    new_order.is_active = False
                    order_data = {
                        "user": order.user,
                        "price": order.price,
                        "volume": order.volume,
                    }
                self.db.add(order)
                data.append(order_data)

        return new_order, data
