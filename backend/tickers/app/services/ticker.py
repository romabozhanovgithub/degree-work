from motor.core import AgnosticCollection


class TickerService:
    def __init__(self, db: AgnosticCollection):
        self.db = db

    async def create_ticker(self, ticker: dict) -> dict:
        """
        Create ticker
        """

        await self.db["tickers"].insert_one(ticker)
        return ticker
