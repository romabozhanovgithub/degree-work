from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session
from app.models import User
from app.repositories import UserRepository, BalanceRepository
from app.services import AuthService, EmailService, PaymentService
from app.core.utils import oauth2_scheme


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    return UserRepository(session)


async def get_balance_repository(
    session: AsyncSession = Depends(get_session),
) -> BalanceRepository:
    return BalanceRepository(session)


async def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repository)


async def get_email_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> EmailService:
    return EmailService(user_repository)


async def get_payment_service(
    balance_repository: BalanceRepository = Depends(get_balance_repository),
) -> PaymentService:
    return PaymentService(balance_repository)


async def get_request_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    user = await auth_service.get_current_active_user(token)
    return user
