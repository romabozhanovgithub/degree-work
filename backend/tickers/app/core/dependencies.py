from fastapi import Depends, Header
import httpx

from app.core import settings
from app.core.exceptions import InvalidAuthorizationTokenException
from app.repositories import OrderRepository, TradeRepository
from app.schemas import UserSchema
from app.services import OrderService, TradeService


async def get_order_repository() -> OrderRepository:
    return OrderRepository()


async def get_trade_repository() -> TradeRepository:
    return TradeRepository()


async def get_order_service(
    order_repository: OrderRepository = Depends(get_order_repository),
):
    return OrderService(repository=order_repository)


async def get_trade_service(
    trade_repository: TradeService = Depends(get_trade_repository),
):
    return TradeService(repository=trade_repository)


async def get_request_user(
    authorization: str | None = Header(None, alias="Authorization"),
    http_bearer: str | None = Header(None, alias="HTTPBearer"),
) -> UserSchema:
    if authorization is not None:
        access_token = authorization
    elif http_bearer is not None:
        access_token = http_bearer
    else:
        raise InvalidAuthorizationTokenException()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=settings.VERIFY_TOKEN_URL,
            headers={"Authorization": access_token},
        )
        if response.status_code != 200:
            raise InvalidAuthorizationTokenException()
        return UserSchema(**response.json())
