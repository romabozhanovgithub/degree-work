import pytest

from app.repositories import OrderRepository
from app.schemas import OrderCreate
from app.schemas.order import OrderUpdate


@pytest.mark.asyncio
async def test_create_order(
    order_repository: OrderRepository, order_data: dict
):
    result = await order_repository.create_order(OrderCreate(**order_data))
    data = await order_repository.get_order_by_id(str(result.id))
    assert data.symbol == order_data["symbol"]


@pytest.mark.asyncio
async def test_get_order_by_id(
    order_repository: OrderRepository, order_data: dict
):
    result = await order_repository.create_order(OrderCreate(**order_data))
    data = await order_repository.get_order_by_id(result.id)
    assert data.symbol == order_data["symbol"]


@pytest.mark.asyncio
async def test_get_orders_by_user_id(
    order_repository: OrderRepository, order_data: dict
):
    result = await order_repository.create_order(OrderCreate(**order_data))
    data = await order_repository.get_orders_by_user_id(result.user_id)
    assert data[0].symbol == order_data["symbol"]


@pytest.mark.asyncio
async def test_get_orders_by_symbol(
    order_repository: OrderRepository, order_data: dict
):
    result = await order_repository.create_order(OrderCreate(**order_data))
    data = await order_repository.get_orders_by_symbol(result.symbol)
    assert data[0].symbol == order_data["symbol"]


@pytest.mark.asyncio
async def test_get_orders_by_symbol_and_user_id(
    order_repository: OrderRepository, order_data: dict
):
    result = await order_repository.create_order(OrderCreate(**order_data))
    data = await order_repository.get_orders_by_symbol_and_user_id(
        result.symbol, result.user_id
    )
    assert data[0].symbol == order_data["symbol"]
    assert data[0].user_id == order_data["user_id"]


@pytest.mark.asyncio
async def test_get_all_orders(
    order_repository: OrderRepository, order_data: dict
):
    await order_repository.create_order(OrderCreate(**order_data))
    data = await order_repository.get_all_orders()
    assert data[0].symbol == order_data["symbol"]
    assert data[0].user_id == order_data["user_id"]


@pytest.mark.asyncio
async def test_update_order_by_id(
    order_repository: OrderRepository, order_data: dict
):
    result = await order_repository.create_order(OrderCreate(**order_data))
    data = await order_repository.update_order_by_id(
        result.id, {"symbol": "test"}
    )
    assert data.symbol == "test"


@pytest.mark.asyncio
async def test_update_order_by_id_schema(
    order_repository: OrderRepository, order_data: dict
):
    result = await order_repository.create_order(OrderCreate(**order_data))
    result.executed_qty = 1
    data = await order_repository.update_order_by_id(
        result.id, OrderUpdate(**result.to_dict())
    )
    assert data.executed_qty == 1


@pytest.mark.asyncio
async def test_delete_order_by_id(
    order_repository: OrderRepository, order_data: dict
):
    result = await order_repository.create_order(OrderCreate(**order_data))
    data = await order_repository.delete_order_by_id(result.id)
    deleted_data = await order_repository.get_order_by_id(result.id)
    assert data.symbol == order_data["symbol"]
    assert deleted_data is None
