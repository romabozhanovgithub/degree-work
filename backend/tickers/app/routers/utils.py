from decimal import Decimal
from fastapi import HTTPException
import httpx

from app.core import settings
from app.core.exceptions.user import InvalidAuthorizationTokenException
from app.core.rabbitmq import pika_client
from app.schemas import OrderDB, UserSchema, TradeDB, NewTradesList
from app.services import OrderService, TradeService


async def send_last_orders_by_symbol(
    symbol: str,
    order_service: OrderService,
) -> None:
    """
    Send last orders to websocket queue.
    """

    last_buy_orders = await order_service.get_open_buy_orders_by_symbol(
        symbol, limit=10, json=True
    )
    last_sell_orders = await order_service.get_open_sell_orders_by_symbol(
        symbol, limit=10, json=True
    )
    message = {
        "type": "broadcast",
        "target": "last_orders",
        "data": {
            "last_buy_orders": last_buy_orders,
            "last_sell_orders": last_sell_orders,
        },
    }
    print(message)
    await pika_client.send_message_to_websocket_queue(
        symbol=symbol,
        message=message,
    )


async def send_new_trades(
    new_trades: list[TradeDB],
) -> None:
    """
    Send new trades to websocket queue.
    """

    await pika_client.send_message_to_websocket_queue(
        symbol=new_trades[0].symbol,
        message={
            "type": "broadcast",
            "target": "new_trades",
            "data": {
                "new_trades": NewTradesList(new_trades=new_trades).to_json(
                    by_alias=True
                ),
            },
        },
    )


async def send_executed_order(executed_order: OrderDB, qty: Decimal) -> None:
    """
    Send executed order to accounts queue.
    """

    to_buy, to_sell = executed_order.symbol.split("/")
    currency = to_buy if executed_order.side == "buy" else to_sell

    await pika_client.send_message_to_accounts_queue(
        {
            "user_id": executed_order.user_id,
            "currency": currency,
            "amount": qty,
        }
    )


async def execute_order(
    new_order: OrderDB,
    order_service: OrderService,
    trade_service: TradeService,
) -> None:
    """
    Execute a new order.
    """

    orders = await order_service.get_orders_to_execute(new_order)
    new_trades = []
    for order in orders:
        new_order, executed_order, qty = await order_service.execute_order(
            new_order=new_order, order=order
        )
        await send_executed_order(executed_order, qty)
        if new_order.user_id != executed_order.user_id:
            new_trade = await trade_service.create_trade_from_orders(
                new_order=new_order,
                executed_order=executed_order,
                qty=qty,
            )
            new_trades.append(new_trade)
        if new_order.status == "closed":
            await order_service.update_order(
                new_order.id,
                new_order.to_dict(exclude_unset=True, exclude_none=True),
            )
            await pika_client.send_message_to_accounts_queue(
                new_order.json(by_alias=True)
            )
            break

    await send_last_orders_by_symbol(new_order.symbol, order_service)
    if new_trades:
        await send_new_trades(new_trades)


async def update_user_balance(
    order: OrderDB,
    authorization: str | None = None,
    http_bearer: str | None = None,
) -> UserSchema:
    """
    Update user balance. Send a request to accounts service.
    Raise HTTPException if response status code is not 200.
    """

    if authorization is not None:
        access_token = authorization
    elif http_bearer is not None:
        access_token = http_bearer
    else:
        raise InvalidAuthorizationTokenException()

    to_buy, to_sell = order.symbol.split("/")
    cost = order.init_qty * order.price
    if order.side == "buy":
        currency = to_sell
        balance = cost
    else:
        currency = to_buy
        balance = order.init_qty

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=settings.CREATE_NEW_ORDER_URL,
            headers={"Authorization": access_token},
            json={
                "currency": currency,
                "amount": str(balance),
            },
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
        return UserSchema(**response.json())
