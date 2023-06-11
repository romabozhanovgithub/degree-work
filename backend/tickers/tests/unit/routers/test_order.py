from unittest.mock import patch
from fastapi import status
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.schemas import OrderCreate, OrderDB
from app.services import OrderService


async def _create_order(
    order_service: OrderService, order_data: dict | None = None
) -> OrderDB:
    if order_data is None:
        order_data = {
            "symbol": "AAPL",
            "price": 100.0,
            "init_qty": 1.0,
            "type": "limit",
            "side": "buy",
            "user_id": "646be16ba7f9c69f0bdf2bc5",
        }
    order = await order_service.create_order(OrderCreate(**order_data))
    return order


def test_create_order() -> None:
    pass


@pytest.mark.asyncio
@patch("app.core.rabbitmq.pika_client.connect")
@patch("app.core.rabbitmq.pika_client.close_connection")
async def test_get_order_by_id(
    mock_close_connection, mock_connect, order_service: OrderService
) -> None:
    with TestClient(app) as client:
        order = await _create_order(order_service)
        response = client.get(f"/orders/{order.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["symbol"] == order.symbol


@pytest.mark.asyncio
@patch("app.core.rabbitmq.pika_client.connect")
@patch("app.core.rabbitmq.pika_client.close_connection")
async def test_get_last_orders_by_symbol(
    mock_close_connection, mock_connect, order_service: OrderService
) -> None:
    with TestClient(app) as client:
        buy_order = await _create_order(order_service)
        sell_order = await _create_order(
            order_service,
            order_data={
                "symbol": "AAPL",
                "price": 120.0,
                "init_qty": 1.0,
                "type": "limit",
                "side": "sell",
                "user_id": "646be16ba7f9c69f0bdf2bc5",
            },
        )
        response = client.get("/orders/last/AAPL")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["buy"][0]["side"] == buy_order.side
        assert response.json()["sell"][0]["side"] == sell_order.side


@pytest.mark.asyncio
@patch("app.core.rabbitmq.pika_client.connect")
@patch("app.core.rabbitmq.pika_client.close_connection")
@patch("app.routers.order.get_current_user")
async def test_get_orders_by_user_id(
    mock_get_current_user,
    mock_close_connection,
    mock_connect,
    order_service: OrderService,
) -> None:
    with TestClient(app) as client:
        order = await _create_order(order_service)
        mock_get_current_user.return_value = order.user_id
        response = client.get(
            f"/orders/user/{order.user_id}",
            headers={"Authorization": order.user_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["symbol"] == order.symbol
        assert response.json()[0]["userId"] == order.user_id
