from decimal import Decimal
from app.repositories import OrderRepository
from app.schemas import OrderCreate, OrderDB, OrderUpdate
from app.services import BaseService


class OrderService(BaseService):
    repository: OrderRepository

    async def create_order(self, order: OrderCreate) -> OrderDB:
        """
        Create a new order in the database and return the created order.
        """

        new_order = OrderDB(**order.dict())
        result = await self.repository.create_order(new_order)
        return result

    async def get_order(self, order_id: str) -> OrderDB:
        """
        Get an order from the database by id.
        """

        result = await self.repository.get_order_by_id(order_id)
        return result

    async def get_user_orders(
        self, user_id: str, limit: int = 100
    ) -> list[OrderDB]:
        """
        Get all orders from the database by user id.
        """

        result = await self.repository.get_orders_by_user_id(
            user_id, limit=limit
        )
        return result

    async def close_order(self, order_id: str) -> OrderDB:
        """
        Close an order from the database by id.
        """

        result = await self.repository.update_order_by_id(
            order_id,
            OrderUpdate(status="closed").to_dict(
                exclude_unset=True, exclude_none=True
            ),
        )
        return result

    async def cancel_order(self, order_id: str) -> OrderDB:
        """
        Cancel an order from the database by id.
        """

        result = await self.repository.update_order_by_id(
            order_id,
            OrderUpdate(status="canceled").to_dict(
                exclude_unset=True, exclude_none=True
            ),
        )
        return result

    async def get_open_buy_orders_by_symbol(
        self, symbol: str, limit: int = 100, json: bool = False
    ) -> list[OrderDB]:
        """
        Get all open buy orders from the database by symbol.
        """

        result = (
            await self.repository.get_orders_by_status_and_side_and_symbol(
                status="open",
                side="buy",
                symbol=symbol,
                limit=limit,
                json=json,
            )
        )
        return result

    async def get_open_sell_orders_by_symbol(
        self, symbol: str, limit: int = 100, json: bool = False
    ) -> list[OrderDB]:
        """
        Get all open sell orders from the database by symbol.
        """

        result = (
            await self.repository.get_orders_by_status_and_side_and_symbol(
                status="open",
                side="sell",
                symbol=symbol,
                limit=limit,
                json=json,
            )
        )
        return result

    async def get_user_orders_by_symbol(
        self, user_id: str, symbol: str, limit: int = 100
    ) -> list[OrderDB]:
        """
        Get all orders from the database by user id and symbol.
        """

        result = await self.repository.get_orders_by_symbol_and_user_id(
            user_id=user_id, symbol=symbol, limit=limit
        )
        return result

    async def update_order(self, order_id: str, order: OrderUpdate) -> OrderDB:
        """
        Update an order from the database by id.
        """

        result = await self.repository.update_order_by_id(
            order_id, order.to_dict(exclude_unset=True, exclude_none=True)
        )
        return result

    def _get_min_qty(self, order: OrderDB, sell_order: OrderDB) -> Decimal:
        return min(
            order.init_qty - order.executed_qty,
            sell_order.init_qty - sell_order.executed_qty,
        )

    async def get_orders_to_execute(self, order: OrderDB) -> list[OrderDB]:
        order_to_db = order.to_dict()
        side = "sell" if order.side == "buy" else "buy"
        price = (
            {"$gte" if order.side == "buy" else "$lte": order_to_db["price"]}
            if order.type == "limit"
            else None
        )
        orders = await self.repository.get_orders_by_symbol_and_filter(
            symbol=order.symbol,
            filter={"side": side, "status": "open", "price": price},
            limit=None,
        )
        return orders

    async def execute_order(
        self, new_order: OrderDB, order: OrderDB
    ) -> list[OrderDB, OrderDB, Decimal]:
        qty = self._get_min_qty(new_order, order)
        order.executed_qty += qty
        new_order.executed_qty += qty

        if order.executed_qty == order.init_qty:
            order.status = "closed"
        if new_order.executed_qty == new_order.init_qty:
            new_order.status = "closed"

        await self.repository.update_order_by_id(
            order.id, order.to_dict(exclude_unset=True, exclude_none=True)
        )
        return new_order, order, qty
