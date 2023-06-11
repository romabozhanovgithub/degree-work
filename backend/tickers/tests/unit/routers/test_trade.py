from unittest.mock import patch
from fastapi import status
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.schemas.trade import TradeDB
from app.services import TradeService


async def _create_trade(
    trade_service: TradeService, trade_data: dict | None = None
) -> None:
    if trade_data is None:
        trade_data = {
            "symbol": "AAPL",
            "orders": [
                "646be16ba7f9c69f0bdf4bc5",
                "646be16ba7f9c69f0bdf5bc5",
            ],
            "price": 100.0,
            "qty": 1.0,
            "users": [
                {
                    "user_id": "646be16ba7f9c69f0bdf2bc5",
                    "side": "buy",
                },
                {
                    "user_id": "646be16ba7f9c69f0bdf3bc5",
                    "side": "sell",
                },
            ],
        }
    trade = await trade_service.create_trade(TradeDB(**trade_data))
    return trade


@pytest.mark.asyncio
@patch("app.core.rabbitmq.pika_client.connect")
@patch("app.core.rabbitmq.pika_client.close_connection")
async def test_get_trade_by_id(
    mock_close_connection,
    mock_connect,
    trade_service: TradeService,
) -> None:
    with TestClient(app) as client:
        trade = await _create_trade(trade_service)
        response = client.get(f"/trades/{trade.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["symbol"] == trade.symbol


@pytest.mark.asyncio
@patch("app.core.rabbitmq.pika_client.connect")
@patch("app.core.rabbitmq.pika_client.close_connection")
async def test_get_last_trades_by_symbol(
    mock_close_connection,
    mock_connect,
    trade_service: TradeService,
) -> None:
    with TestClient(app) as client:
        trade = await _create_trade(trade_service)
        response = client.get(f"/trades/last/{trade.symbol}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()[0]["symbol"] == trade.symbol

        
@pytest.mark.asyncio
@patch("app.core.rabbitmq.pika_client.connect")
@patch("app.core.rabbitmq.pika_client.close_connection")
@patch("app.routers.trade.get_current_user")
async def test_get_trades_by_user_id(
    mock_get_current_user,
    mock_close_connection,
    mock_connect,
    trade_service: TradeService,
) -> None:
    with TestClient(app) as client:
        trade = await _create_trade(trade_service)
        mock_get_current_user.return_value = trade.users[0].user_id
        response = client.get(
            f"/trades/user",
            headers={
                "Authorization": trade.users[0].user_id
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()[0]["_id"] == str(trade.id)
        assert response.json()[0]["symbol"] == trade.symbol
