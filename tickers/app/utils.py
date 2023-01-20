import httpx
from app.routes.manager import manager

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
    """

    user_id = order["user"]
    if users_balance.get(user_id):
        users_balance[user_id] += order["price"] * order["volume"]
    else:
        users_balance[user_id] = order["price"] * order["volume"]


async def send_ticker_by_websocket(ticker: dict) -> None:
    """
    Send ticker by websocket.
    """

    await manager.broadcast_subscription(
        subscription=ticker["name"],
        data=ticker
    )


async def send_tickers_by_websocket(subscription: str, tickers: list) -> None:
    """
    Send tickers by websocket.
    """

    await manager.broadcast_subscription(
        subscription=subscription,
        data={
            "many": True,
            "message": [
                {
                    "name": ticker["name"],
                    "price": ticker["price"],
                    "volume": ticker["volume"],
                    "datetime": ticker["datetime"],
                }
                for ticker in tickers
            ]
        }
    )
