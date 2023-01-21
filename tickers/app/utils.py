import httpx
from app.routes.manager import manager
from app.schemas import OrdersLast, TickerResponse

ACCOUNTS_SERVICE_URL = "http://accounts:8000/api/v1"


async def request(
    url: str,
    method: str,
    access_token: str,
    data: dict = None,
) -> httpx.Response:
    print(f"access_token: {access_token}")
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(
                f"{ACCOUNTS_SERVICE_URL}{url}",
                headers={"x-access-token": f"{access_token}"}
            )
        elif method == "POST":
            response = await client.post(
                f"{ACCOUNTS_SERVICE_URL}{url}",
                json=data,
                headers={"x-access-token": f"{access_token}"}
            )

    return response


def add_user_balance(users_balance: dict, order: dict) -> None:
    """
    Add user balance to users_balance dict.

    >>> users_balance: dict = {
            user_id: {
                "balance_name": value_to_update,
                "balance_name": value_to_update,
            },
        }
    """

    user = order["user"]
    if order["type"] == "BUY":
        balance_name = order["name"] # AAPL
        if user not in users_balance:
            users_balance[user] = {balance_name: 0}
        users_balance[user][balance_name] += order["volume"]
    else:
        balance_name = "USD"
        if user not in users_balance:
            users_balance[user] = {balance_name: 0}
        users_balance[user][balance_name] += order["volume"] * order["price"]


async def send_ticker_by_websocket(ticker: dict) -> None:
    """
    Send ticker by websocket.
    """

    await manager.broadcast_subscription(
        subscription=ticker["name"],
        data=ticker
    )


async def send_tickers_and_orders_by_websocket(
    subscription: str, tickers: list, order_service
) -> None:
    """
    Send tickers by websocket.
    """

    last_orders = await order_service.get_last_orders(subscription)
    await manager.broadcast_subscription(
        subscription=subscription,
        data={
            "many": True,
            "message": {
                "tickers": [
                    TickerResponse(**ticker).json()
                    for ticker in tickers
                ],
                "orders": OrdersLast(SELL=last_orders["SELL"], BUY=last_orders["BUY"]).dict()
            }
        }
    )
