from fastapi import APIRouter
from app.routes import users, tickers, orders

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(tickers.router, prefix="/tickers", tags=["tickers"])
router.include_router(orders.router, prefix="/orders", tags=["orders"])
