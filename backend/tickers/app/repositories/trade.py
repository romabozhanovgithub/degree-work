from app.repositories import BaseRepository
from app.schemas import TradeDB


class TradeRepository(BaseRepository):
    collection_name = "trades"

    async def create_trade(self, trade: TradeDB) -> TradeDB:
        """
        Create a new trade in the database and return the created trade.
        """

        result = await self.create_document(trade.to_dict())
        trade = await self.get_trade_by_id(result)
        return trade

    async def get_trade_by_id(self, trade_id: str) -> TradeDB | None:
        """
        Find an trade by id and return it.
        """

        result = await self.get_document_by_id(trade_id)
        return TradeDB(**result) if result else None

    async def get_trades_by_symbol(
        self, symbol: str, limit: int = 100
    ) -> list[TradeDB]:
        """
        Find trades by symbol and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = await self.get_documents_by_field("symbol", symbol, limit)
        return [TradeDB(**trade) for trade in result]

    async def get_trades_by_order_id(
        self, order_id: str, limit: int = 100
    ) -> list[TradeDB]:
        """
        Find trades by order_id and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = await self.get_documents_by_field(
            "orders", self._get_id(order_id), limit
        )
        return [TradeDB(**trade) for trade in result]

    async def get_trades_by_user_id(
        self, user_id: str, limit: int = 100
    ) -> list[TradeDB]:
        """
        Find trades by user_id and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = await self.get_documents_by_field(
            "users.userId", user_id, limit
        )
        return [TradeDB(**trade) for trade in result]

    async def get_trades_by_symbol_and_user_id(
        self, symbol: str, user_id: str, limit: int = 100
    ) -> list[TradeDB]:
        """
        Find trades by symbol and user_id and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = await self._get_documents_by_filter(
            {"symbol": symbol, "users.userId": user_id}, limit
        )
        return [TradeDB(**trade) for trade in result]

    async def get_trades_by_order_id_and_user_id(
        self, order_id: str, user_id: str, limit: int = 100
    ) -> list[TradeDB]:
        """
        Find trades by order_id and user_id and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = await self._get_documents_by_filter(
            {"orders": self._get_id(order_id), "users.userId": user_id}, limit
        )
        return [TradeDB(**trade) for trade in result]

    async def get_trades_by_symbol_and_user_id_and_order_id(
        self, symbol: str, user_id: str, order_id: str, limit: int = 100
    ) -> list[TradeDB]:
        """
        Find trades by symbol and user_id and order_id and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = await self._get_documents_by_filter(
            {
                "symbol": symbol,
                "orders": self._get_id(order_id),
                "users.userId": user_id,
            },
            limit,
        )
        return [TradeDB(**trade) for trade in result]

    async def get_all_trades(self, limit: int = 100) -> list[TradeDB]:
        """
        Find all trades and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = await self.get_all_documents(limit)
        return [TradeDB(**trade) for trade in result]
