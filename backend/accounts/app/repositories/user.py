from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, selectinload

from app.models import User, Balance


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_id(self, user_id: str) -> User | None:
        statement = select(User).where(User.id == user_id)
        result = await self.session.execute(statement)
        user = result.scalar()
        if user:
            return user
        return None

    async def get_user_by_email(
        self, email: str, balance: bool = False, currency: str | None = None
    ) -> User | None:
        statement = select(User).where(User.email == email)
        if balance and currency:
            statement = (
                statement.join(User.balances)
                .options(contains_eager(User.balances))
                .filter(
                    and_(
                        Balance.currency == currency,
                        Balance.user_id == User.id,
                    )
                )
            )
        elif balance:
            statement = statement.options(selectinload(User.balances))
        result = await self.session.execute(statement)
        user = result.scalars().first()
        if user:
            return user
        return None

    async def get_all_users(self) -> list[User]:
        statement = select(User)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def update_user(self, user: User) -> User:
        await self.session.commit()
        await self.session.refresh(user)
        return user
