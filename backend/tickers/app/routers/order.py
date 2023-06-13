from fastapi import APIRouter, Depends, Header, status, BackgroundTasks

from app.core.dependencies import get_order_service, get_trade_service
from app.core.utils import get_current_user
from app.schemas import (
    OrderCreateRequest,
    OrderResponseSchema,
    OrderLastResponseSchema,
)
from app.services import OrderService, TradeService
from app.routers.utils import execute_order, update_user_balance

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/create",
    summary="Create a new order",
    description="Create a new order and return the created order.",
    response_model=OrderResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    background_tasks: BackgroundTasks,
    order: OrderCreateRequest,
    order_service: OrderService = Depends(get_order_service),
    trade_service: TradeService = Depends(get_trade_service),
    authorization: str | None = Header(None, alias="Authorization"),
    http_bearer: str | None = Header(None, alias="HTTPBearer"),
) -> OrderResponseSchema:
    """
    Create a new order and return the created order.
    """

    user = await update_user_balance(order, authorization, http_bearer)
    order.user_id = user.id
    result = await order_service.create_order(order)
    background_tasks.add_task(
        execute_order, result, order_service, trade_service
    )
    return result


@router.get(
    "/last/{symbol}",
    summary="Get last orders by symbol",
    description="Get last orders by symbol and return the orders.",
    response_model=OrderLastResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_last_orders_by_symbol(
    symbol: str,
    limit: int = 10,
    order_service: OrderService = Depends(get_order_service),
) -> OrderLastResponseSchema:
    """
    Get last orders by symbol and return the orders.
    """

    buy_orders = await order_service.get_open_buy_orders_by_symbol(
        symbol=symbol, limit=limit
    )
    sell_orders = await order_service.get_open_sell_orders_by_symbol(
        symbol=symbol, limit=limit
    )
    return OrderLastResponseSchema(buy=buy_orders, sell=sell_orders)


@router.get(
    "/user/{user_id}",
    summary="Get orders by user id",
    description="Get orders by user id and return the orders.",
    response_model=list[OrderResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_orders_by_user_id(
    limit: int = 100,
    order_service: OrderService = Depends(get_order_service),
    authorization: str | None = Header(None, alias="Authorization"),
    http_bearer: str | None = Header(None, alias="HTTPBearer"),
) -> list[OrderResponseSchema]:
    """
    Get orders by user id and return the orders.
    """

    user_id = await get_current_user(
        authorization=authorization, http_bearer=http_bearer
    )
    return await order_service.get_user_orders(user_id, limit=limit)


@router.get(
    "/{order_id}",
    summary="Get an order by id",
    description="Get an order by id and return the order.",
    response_model=OrderResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_order_by_id(
    order_id: str,
    order_service: OrderService = Depends(get_order_service),
) -> OrderResponseSchema:
    """
    Get an order by id and return the order.
    """

    return await order_service.get_order(order_id)
