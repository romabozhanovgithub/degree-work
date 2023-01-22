from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from motor.core import AgnosticCollection

from app.dependencies import get_db
from app.schemas import TickerResponse

router = APIRouter()


@router.get("/", response_model=list[str])
async def get_tickers(db: AgnosticCollection = Depends(get_db)):
    """
    Get all tickers names
    """

    tickers = await db["tickers"].distinct("name")
    return tickers


@router.get("/{ticker_name}/{ticker_id}", response_model=TickerResponse)
async def get_ticker_by_id(
    ticker_name: str, ticker_id: str, db: AgnosticCollection = Depends(get_db)
):
    """
    Get ticker by name and id
    """

    ticker = await db["tickers"].find_one({"name": ticker_name, "_id": ObjectId(ticker_id)})
    if not ticker:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return ticker


@router.get("/{ticker_name}", response_model=list[TickerResponse])
async def get_tickers_by_name(
    ticker_name: str,
    skip: int = 0,
    limit: int = 100,
    db: AgnosticCollection = Depends(get_db)
):
    """
    Get ticker by name
    """

    tickers = await db["tickers"].find(
        {"name": ticker_name}, sort=[("datetime", -1)], skip=skip, limit=limit
    ).to_list(None)
    return tickers
