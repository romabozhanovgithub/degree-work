from typing import Literal
from app.repositories import BaseRepository
from app.schemas import OrderDB, OrderUpdate


class OrderRepository(BaseRepository):
    collection_name = "orders"

    async def create_order(self, order: OrderDB) -> OrderDB:
        """
        Create a new order in the database and return the created order.
        """

        result = await self.create_document(order.to_dict())
        order = await self.get_order_by_id(result)
        return order

    async def get_order_by_id(self, order_id: str) -> OrderDB | None:
        """
        Find an order by id and return it.
        """

        result = await self.get_document_by_id(order_id)
        return OrderDB(**result) if result else None

    async def get_orders_by_user_id(
        self, user_id: str, limit: int = 100
    ) -> list[OrderDB]:
        """
        Find orders by user_id and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = await self.get_documents_by_field("userId", user_id, limit)
        return [OrderDB(**order) for order in result]

    async def get_orders_by_symbol(
        self, symbol: str, limit: int = 100
    ) -> list[OrderDB]:
        """
        Find orders by symbol and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = await self.get_documents_by_field("symbol", symbol, limit)
        return [OrderDB(**order) for order in result]

    async def get_orders_by_status(
        self, status: Literal["open", "closed", "canceled"], limit: int = 100
    ) -> list[OrderDB]:
        """
        Find orders by status and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = await self.get_documents_by_field("status", status, limit)
        return [OrderDB(**order) for order in result]

    async def get_orders_by_type(
        self, type: Literal["market", "limit"], limit: int = 100
    ) -> list[OrderDB]:
        """
        Find orders by type and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = await self.get_documents_by_field("type", type, limit)
        return [OrderDB(**order) for order in result]

    async def get_orders_by_side(
        self, side: Literal["buy", "sell"], limit: int = 100
    ) -> list[OrderDB]:
        """
        Find orders by side and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = await self.get_documents_by_field("side", side, limit)
        return [OrderDB(**order) for order in result]

    async def get_orders_by_status_and_side_and_symbol(
        self,
        status: Literal["open", "closed", "canceled"],
        side: Literal["buy", "sell"],
        symbol: str,
        limit: int = 100,
        order_by: str = "price",
        order: int = -1,
        json: bool = False,
    ) -> list[OrderDB]:
        """
        Find orders by status and side and symbol and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = await self.get_documents_by_fields(
            limit, status=status, side=side, symbol=symbol, order_by=order_by, order=order
        )
        if json:
            return [OrderDB(**order).to_json() for order in result]
        return [OrderDB(**order) for order in result]

    async def get_orders_by_symbol_and_user_id(
        self, symbol: str, user_id: str, limit: int = 100
    ) -> list[OrderDB]:
        """
        Find orders by symbol and user_id and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = await self.get_documents_by_fields(
            limit, **{"symbol": symbol, "userId": user_id}
        )
        return [OrderDB(**order) for order in result]

    async def get_orders_by_symbol_and_filter(
        self, symbol: str, filter: dict, limit: int = 100
    ) -> list[OrderDB]:
        """
        Find orders by symbol and filter and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = await self.get_documents_by_fields(
            limit, **{"symbol": symbol, **filter}
        )
        return [OrderDB(**order) for order in result]

    async def get_all_orders(self, limit: int = 100) -> list[OrderDB]:
        """
        Find all orders and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = await self.get_all_documents(limit)
        return [OrderDB(**order) for order in result]

    async def update_order_by_id(
        self, order_id: str, order: OrderUpdate | dict
    ) -> OrderDB | None:
        """
        Update an order by id and return the updated order.
        """

        if isinstance(order, OrderUpdate):
            order = order.to_dict()

        result = await self.update_document_by_id(
            order_id, order, return_updated=True
        )
        return OrderDB(**result) if result else None

    async def delete_order_by_id(self, order_id: str) -> OrderDB | None:
        """
        Delete an order by id and return the deleted order.
        """

        result = await self.delete_document_by_id(order_id)
        return OrderDB(**result) if result else None
