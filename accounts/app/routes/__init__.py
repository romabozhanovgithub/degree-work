from fastapi import APIRouter
from app.routes import users, orders

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(orders.router, prefix="/orders", tags=["orders"])
