from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from motor.core import AgnosticCollection

from app.dependencies import get_db, get_access_token
from app.schemas import TickerResponse, TickerPermanentRequest
from app.routes.manager import manager

router = APIRouter()


@router.get("/tickers", response_model=list[str])
async def get_tickers(db: AgnosticCollection = Depends(get_db)):
    """
    Get all tickers names
    """

    tickers = await db["tickers"].distinct("name")
    return tickers


@router.get("/tickers/{ticker_name}", response_model=list[TickerResponse])
async def get_ticker(ticker_name: str, db: AgnosticCollection = Depends(get_db)):
    """
    Get ticker by name
    """

    ticker = await db["tickers"].find_one({"name": ticker_name}, sort=[("datetime", -1)])
    if not ticker:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return ticker


@router.get("/tickers/{ticker_name}/{ticker_id}", response_model=TickerResponse)
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


@router.get("/tickers/{ticker_name}/last", response_model=TickerResponse)
async def get_last_ticker(
    ticker_name: str, db: AgnosticCollection = Depends(get_db)
):
    """
    Get last ticker by name
    """

    ticker = await db["tickers"].find_one({"name": ticker_name}, sort=[("datetime", -1)])
    if not ticker:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return ticker


@router.post("/tickers/permanent", response_model=TickerResponse)
async def create_ticker(
    ticker: TickerPermanentRequest,
    db: AgnosticCollection = Depends(get_db),
    access_token: str = Depends(get_access_token)
):
    """
    Create ticker by name
    """

    price = await db["tickers"].find_one(
        {"name": ticker.name}, sort=[("datetime", -1)]
    )
    ticker = await db["tickers"].insert_one({
        **ticker.dict(),
        "price": price["price"],
    })
    ticker = await db["tickers"].find_one({"_id": ticker.inserted_id})
    await manager.broadcast(ticker)
    return ticker
