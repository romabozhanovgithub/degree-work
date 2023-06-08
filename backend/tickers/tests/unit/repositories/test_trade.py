import pytest

from app.repositories import TradeRepository
from app.schemas import TradeDB


@pytest.mark.asyncio
async def test_create_trade(
    trade_repository: TradeRepository, trade_data: dict
):
    result = await trade_repository.create_trade(TradeDB(**trade_data))
    data = await trade_repository.get_trade_by_id(str(result.id))
    assert data.symbol == trade_data["symbol"]


@pytest.mark.asyncio
async def test_get_trade_by_id(
    trade_repository: TradeRepository, trade_data: dict
):
    result = await trade_repository.create_trade(TradeDB(**trade_data))
    data = await trade_repository.get_trade_by_id(result.id)
    assert data.id == result.id
    assert data.symbol == trade_data["symbol"]


@pytest.mark.asyncio
async def test_get_trades_by_symbol(
    trade_repository: TradeRepository, trade_data: dict
):
    result = await trade_repository.create_trade(TradeDB(**trade_data))
    data = await trade_repository.get_trades_by_symbol(result.symbol)
    assert data[0].symbol == trade_data["symbol"]


@pytest.mark.asyncio
async def test_get_trades_by_order_id(
    trade_repository: TradeRepository, trade_data: dict
):
    await trade_repository.create_trade(TradeDB(**trade_data))
    trade_data["orders"][0] = "646be16ba7f9c69f0bdf2bc8"
    await trade_repository.create_trade(TradeDB(**trade_data))
    data = await trade_repository.get_trades_by_order_id(
        trade_data["orders"][0]
    )
    assert str(data[0].orders[0]) == trade_data["orders"][0]
    assert str(data[0].orders[1]) == trade_data["orders"][1]


@pytest.mark.asyncio
async def test_get_trades_by_user_id(
    trade_repository: TradeRepository, trade_data: dict
):
    await trade_repository.create_trade(TradeDB(**trade_data))
    trade_data["users"][0]["user_id"] = "646be16ba7f9c69f0bdf2bc7"
    await trade_repository.create_trade(TradeDB(**trade_data))
    data = await trade_repository.get_trades_by_user_id(
        trade_data["users"][0]["user_id"]
    )
    assert len(data) == 1
    assert data[0].users[0].user_id == trade_data["users"][0]["user_id"]
    assert data[0].users[1].user_id == trade_data["users"][1]["user_id"]


@pytest.mark.asyncio
async def test_get_trades_by_symbol_and_user_id(
    trade_repository: TradeRepository, trade_data: dict
):
    await trade_repository.create_trade(TradeDB(**trade_data))
    trade_data["users"][0]["user_id"] = "646be16ba7f9c69f0bdf2bc7"
    await trade_repository.create_trade(TradeDB(**trade_data))
    data = await trade_repository.get_trades_by_symbol_and_user_id(
        trade_data["symbol"], trade_data["users"][0]["user_id"]
    )
    assert len(data) == 1
    assert data[0].users[0].user_id == trade_data["users"][0]["user_id"]
    assert data[0].users[1].user_id == trade_data["users"][1]["user_id"]
    assert data[0].symbol == trade_data["symbol"]


@pytest.mark.asyncio
async def test_get_trades_by_order_id_and_user_id(
    trade_repository: TradeRepository, trade_data: dict
):
    await trade_repository.create_trade(TradeDB(**trade_data))
    trade_data["users"][0]["user_id"] = "646be16ba7f9c69f0bdf2bc7"
    await trade_repository.create_trade(TradeDB(**trade_data))
    data = await trade_repository.get_trades_by_order_id_and_user_id(
        trade_data["orders"][0], trade_data["users"][0]["user_id"]
    )
    assert len(data) == 1
    assert data[0].users[0].user_id == trade_data["users"][0]["user_id"]
    assert data[0].users[1].user_id == trade_data["users"][1]["user_id"]
    assert str(data[0].orders[0]) == trade_data["orders"][0]
    assert str(data[0].orders[1]) == trade_data["orders"][1]


@pytest.mark.asyncio
async def test_get_trades_by_symbol_and_order_id_and_user_id(
    trade_repository: TradeRepository, trade_data: dict
):
    await trade_repository.create_trade(TradeDB(**trade_data))
    trade_data["orders"][0] = "646be16ba7f9c69f0bdf2bc8"
    trade_data["users"][0]["user_id"] = "646be16ba7f9c69f0bdf2bc7"
    await trade_repository.create_trade(TradeDB(**trade_data))
    data = (
        await trade_repository.get_trades_by_symbol_and_user_id_and_order_id(
            trade_data["symbol"],
            trade_data["users"][0]["user_id"],
            trade_data["orders"][0],
        )
    )
    assert len(data) == 1
    assert data[0].symbol == trade_data["symbol"]
    assert str(data[0].orders[0]) == trade_data["orders"][0]
    assert str(data[0].orders[1]) == trade_data["orders"][1]
    assert data[0].users[0].user_id == trade_data["users"][0]["user_id"]
    assert data[0].users[1].user_id == trade_data["users"][1]["user_id"]


@pytest.mark.asyncio
async def test_get_all_trades(
    trade_repository: TradeRepository, trade_data: dict
):
    await trade_repository.create_trade(TradeDB(**trade_data))
    trade_data["orders"][0] = "646be16ba7f9c69f0bdf2bc8"
    trade_data["users"][0]["user_id"] = "646be16ba7f9c69f0bdf2bc7"
    await trade_repository.create_trade(TradeDB(**trade_data))
    data = await trade_repository.get_all_trades()
    assert len(data) == 2
