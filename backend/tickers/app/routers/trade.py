from fastapi import APIRouter, Depends, Header, status

from app.core.dependencies import get_trade_service
from app.core.utils import get_current_user
from app.schemas import TradeResponse
from app.services import TradeService

router = APIRouter(prefix="/trades", tags=["trades"])



@router.get(
    "/last/{symbol}",
    summary="Get last trades by symbol",
    description="Get last trades by symbol and return the trades.",
    response_model=list[TradeResponse],
    status_code=status.HTTP_200_OK,
)
async def get_last_trades_by_symbol(
    symbol: str,
    limit: int = 100,
    trade_service: TradeService = Depends(get_trade_service),
) -> list[TradeResponse]:
    """
    Get last trades by symbol and return the trades.
    """

    return await trade_service.get_symbol_trades(symbol, limit)


@router.get(
    "/user",
    summary="Get trades by user id",
    description="Get trades by user id and return the trades.",
    response_model=list[TradeResponse],
    status_code=status.HTTP_200_OK,
)
async def get_trades_by_user_id(
    symbol: str = None,
    limit: int = 100,
    trade_service: TradeService = Depends(get_trade_service),
    authorization: str | None = Header(None, alias="Authorization"),
    http_bearer: str | None = Header(None, alias="HTTPBearer"),
) -> list[TradeResponse]:
    """
    Get trades by user id and return the trades.
    """

    user_id = await get_current_user(
        authorization=authorization, http_bearer=http_bearer
    )
    if symbol is not None:
        return await trade_service.get_symbol_and_user_trades(
            user_id, symbol, limit
        )
    return await trade_service.get_user_trades(user_id, limit)


@router.get(
    "/{trade_id}",
    summary="Get a trade by id",
    description="Get a trade by id and return the trade.",
    response_model=TradeResponse,
    status_code=status.HTTP_200_OK,
)
async def get_trade_by_id(
    trade_id: str,
    trade_service: TradeService = Depends(get_trade_service),
) -> TradeResponse:
    """
    Get a trade by id and return the trade.
    """

    return await trade_service.get_trade(trade_id)
