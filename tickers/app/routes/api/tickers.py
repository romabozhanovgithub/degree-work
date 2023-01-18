from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from motor.core import AgnosticCollection

from app.dependencies import get_db, get_access_token
from app.schemas import TickerResponse, TickerRequest
from app.routes.manager import manager

router = APIRouter()


@router.get("/", response_model=list[str])
async def get_tickers(db: AgnosticCollection = Depends(get_db)):
    """
    Get all tickers names
    """

    tickers = await db["tickers"].distinct("name")
    return tickers


@router.get("/{ticker_name}", response_model=list[TickerResponse])
async def get_ticker(ticker_name: str, db: AgnosticCollection = Depends(get_db)):
    """
    Get ticker by name
    """

    ticker = await db["tickers"].find_one({"name": ticker_name}, sort=[("datetime", -1)])
    if not ticker:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return ticker


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


@router.get("/{ticker_name}/last", response_model=TickerResponse)
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


@router.post("/", response_model=TickerResponse)
async def create_ticker(
    ticker: TickerRequest,
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


@router.post("/bulk", response_model=list[TickerResponse])
async def create_tickers_in_bulk(
    tickers: list[TickerRequest],
    db: AgnosticCollection = Depends(get_db),
    access_token: str = Depends(get_access_token)
):
    """
    Create tickers in bulk
    """

    print(f"Tickers: {tickers}")

    tickers = await db["tickers"].insert_many([ticker.dict() for ticker in tickers])
    tickers = await db["tickers"].find(
        {"_id": {"$in": tickers.inserted_ids}}
    ).to_list(None)
    for ticker in tickers:
        await manager.broadcast(ticker)
    return tickers
