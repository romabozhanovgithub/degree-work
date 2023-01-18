from fastapi import APIRouter
from app.routes.api import orders, tickers

router = APIRouter()

router.include_router(orders.router, prefix="/orders", tags=["orders"])
router.include_router(tickers.router, prefix="/tickers", tags=["tickers"])
