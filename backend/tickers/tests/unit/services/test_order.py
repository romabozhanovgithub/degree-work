import pytest

from app.schemas import OrderCreate
from app.services import OrderService


@pytest.mark.asyncio
async def test_create_order(order_service: OrderService, order_data: dict):
    order = OrderCreate(**order_data)
    result = await order_service.create_order(order)
    assert result.symbol == order_data["symbol"]


@pytest.mark.asyncio
async def test_get_order(order_service: OrderService, order_data: dict):
    order = OrderCreate(**order_data)
    result = await order_service.create_order(order)
    data = await order_service.get_order(result.id)
    assert data.id == result.id
    assert data.symbol == order_data["symbol"]


@pytest.mark.asyncio
async def test_get_user_orders(order_service: OrderService, order_data: dict):
    order = OrderCreate(**order_data)
    result = await order_service.create_order(order)
    data = await order_service.get_user_orders(order_data["user_id"])
    assert data[0].id == result.id
    assert data[0].symbol == order_data["symbol"]
    assert data[0].user_id == order_data["user_id"]


@pytest.mark.asyncio
async def test_close_order(order_service: OrderService, order_data: dict):
    order = OrderCreate(**order_data)
    result = await order_service.create_order(order)
    data = await order_service.close_order(result.id)
    assert data.id == result.id
    assert data.symbol == order_data["symbol"]
    assert data.status == "closed"


@pytest.mark.asyncio
async def test_cancel_order(order_service: OrderService, order_data: dict):
    order = OrderCreate(**order_data)
    result = await order_service.create_order(order)
    data = await order_service.cancel_order(result.id)
    assert data.id == result.id
    assert data.symbol == order_data["symbol"]
    assert data.status == "canceled"


@pytest.mark.asyncio
async def test_get_open_buy_orders_by_symbol(
    order_service: OrderService, order_data: dict
):
    order = OrderCreate(**order_data)
    result = await order_service.create_order(order)
    data = await order_service.get_open_buy_orders_by_symbol(
        order_data["symbol"]
    )
    assert data[0].id == result.id
    assert data[0].symbol == order_data["symbol"]
    assert data[0].status == "open"
    assert data[0].side == "buy"


@pytest.mark.asyncio
async def test_get_open_sell_orders_by_symbol(
    order_service: OrderService, order_data: dict
):
    order_data["side"] = "sell"
    order = OrderCreate(**order_data)
    result = await order_service.create_order(order)
    print(result)
    data = await order_service.get_open_sell_orders_by_symbol(
        order_data["symbol"]
    )
    assert data[0].id == result.id
    assert data[0].symbol == order_data["symbol"]
    assert data[0].status == "open"
    assert data[0].side == "sell"


@pytest.mark.asyncio
async def test_get_user_orders_by_symbol(
    order_service: OrderService, order_data: dict
):
    order = OrderCreate(**order_data)
    result = await order_service.create_order(order)
    data = await order_service.get_user_orders_by_symbol(
        order_data["user_id"], order_data["symbol"]
    )
    assert data[0].id == result.id
    assert data[0].symbol == order_data["symbol"]
    assert data[0].user_id == order_data["user_id"]
