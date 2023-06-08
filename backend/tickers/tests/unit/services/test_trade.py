import pytest

from app.schemas import TradeDB
from app.services import TradeService


@pytest.mark.asyncio
async def test_create_trade(trade_service: TradeService, trade_data: dict):
    trade = TradeDB(**trade_data)
    result = await trade_service.create_trade(trade)
    assert result.symbol == trade.symbol
    assert result.users == trade.users
    assert result.price == trade.price
    assert result.orders == trade.orders


@pytest.mark.asyncio
async def test_get_trade(trade_service: TradeService, trade_data: dict):
    trade = TradeDB(**trade_data)
    result = await trade_service.create_trade(trade)
    data = await trade_service.get_trade(result.id)
    assert data.id == result.id
    assert data.symbol == trade.symbol
    assert data.users == trade.users
    assert data.price == trade.price
    assert data.orders == trade.orders


@pytest.mark.asyncio
async def test_get_user_trades(trade_service: TradeService, trade_data: dict):
    trade = TradeDB(**trade_data)
    result = await trade_service.create_trade(trade)
    data = await trade_service.get_user_trades(result.users[0].user_id)
    assert data[0].id == result.id
    assert data[0].symbol == trade.symbol
    assert data[0].users == trade.users
    assert data[0].price == trade.price
    assert data[0].orders == trade.orders


@pytest.mark.asyncio
async def test_get_symbol_trades(
    trade_service: TradeService, trade_data: dict
):
    trade = TradeDB(**trade_data)
    result = await trade_service.create_trade(trade)
    data = await trade_service.get_symbol_trades(result.symbol)
    assert data[0].id == result.id
    assert data[0].symbol == trade.symbol
    assert data[0].users == trade.users
    assert data[0].price == trade.price
    assert data[0].orders == trade.orders


@pytest.mark.asyncio
async def test_get_order_trades(trade_service: TradeService, trade_data: dict):
    trade = TradeDB(**trade_data)
    result = await trade_service.create_trade(trade)
    data = await trade_service.get_order_trades(result.orders[0])
    assert data[0].id == result.id
    assert data[0].symbol == trade.symbol
    assert data[0].users == trade.users
    assert data[0].price == trade.price
    assert data[0].orders == trade.orders


@pytest.mark.asyncio
async def test_get_symbol_and_user_trades(
    trade_service: TradeService, trade_data: dict
):
    trade = TradeDB(**trade_data)
    result = await trade_service.create_trade(trade)
    data = await trade_service.get_symbol_and_user_trades(
        result.symbol, result.users[0].user_id
    )
    assert data[0].id == result.id
    assert data[0].symbol == trade.symbol
    assert data[0].users == trade.users
    assert data[0].price == trade.price
    assert data[0].orders == trade.orders
