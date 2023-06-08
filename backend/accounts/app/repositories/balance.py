from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import settings

from app.models import User, Balance


class BalanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def init_user_balance(self, user: User) -> list[Balance]:
        user_balance = []
        for currency in settings.BALANCE_TYPES:
            balance = Balance(currency=currency, user=user)
            self.session.add(balance)
        await self.session.commit()
        user_balance = await self.get_user_balances(user.id)
        return user_balance

    async def create_balance(self, balance: Balance) -> Balance:
        self.session.add(balance)
        await self.session.commit()
        await self.session.refresh(balance)
        return balance

    async def get_balance_by_id(self, balance_id: str) -> Balance:
        statement = select(Balance).where(Balance.id == balance_id)
        result = await self.session.execute(statement)
        return result.scalar()

    async def get_user_balance_by_currency(
        self, user_id: str, currency: str
    ) -> Balance:
        statement = (
            select(Balance)
            .where(Balance.user_id == user_id)
            .where(Balance.currency == currency)
        )
        result = await self.session.execute(statement)
        return result.scalar()

    async def get_user_balances(self, user_id: str) -> list[Balance]:
        statement = select(Balance).where(Balance.user_id == user_id)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def update_balance(self, balance: Balance) -> Balance:
        await self.session.commit()
        await self.session.refresh(balance)
        return balance
