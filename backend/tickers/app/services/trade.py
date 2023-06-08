from decimal import Decimal
from app.repositories import TradeRepository
from app.schemas import TradeDB, OrderDB, UserTrade
from app.services import BaseService


class TradeService(BaseService):
    repository: TradeRepository

    async def create_trade(self, trade: TradeDB) -> TradeDB:
        """
        Create a new trade in the database and return the created trade.
        """

        new_trade = TradeDB(**trade.to_dict())
        result = await self.repository.create_trade(new_trade)
        return result

    async def create_trade_from_orders(
        self, order1: OrderDB, order2: OrderDB, qty: Decimal | None = None
    ) -> TradeDB:
        """
        Create a new trade in the database from two orders and return
        the created trade.
        """

        if qty is None:
            qty = min(order1.init_qty, order2.init_qty)

        new_trade = TradeDB(
            symbol=order1.symbol,
            orders=[order1.id, order2.id],
            price=order2.price,
            qty=qty,
            comission=0,
            users=[
                UserTrade(
                    user_id=order1.user_id,
                    side=order1.side,
                ),
                UserTrade(
                    user_id=order2.user_id,
                    side=order2.side,
                ),
            ],
        )
        result = await self.repository.create_trade(new_trade)
        return result

    async def get_trade(self, trade_id: str) -> TradeDB:
        """
        Get a trade from the database by id.
        """

        result = await self.repository.get_trade_by_id(trade_id)
        return result

    async def get_user_trades(
        self, user_id: str, limit: int = 100
    ) -> list[TradeDB]:
        """
        Get all trades from the database by user id.
        """

        result = await self.repository.get_trades_by_user_id(user_id, limit)
        return result

    async def get_symbol_trades(
        self, symbol: str, limit: int = 100
    ) -> list[TradeDB]:
        """
        Get all trades from the database by symbol.
        """

        result = await self.repository.get_trades_by_symbol(symbol, limit)
        return result

    async def get_order_trades(
        self, order_id: str, limit: int = 100
    ) -> list[TradeDB]:
        """
        Get all trades from the database by order id.
        """

        result = await self.repository.get_trades_by_order_id(order_id, limit)
        return result

    async def get_symbol_and_user_trades(
        self, symbol: str, user_id: str, limit: int = 100
    ) -> list[TradeDB]:
        """
        Get all trades from the database by symbol and user id.
        """

        result = await self.repository.get_trades_by_symbol_and_user_id(
            symbol, user_id, limit
        )
        return result
