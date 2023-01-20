from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pymongo import InsertOne, UpdateOne
from motor.core import AgnosticCollection

from app.dependencies import get_db, get_access_token
from app.schemas import OrderRequest, OrderResponse, OrdersLast
from app.services import OrderService
from app.utils import send_tickers_by_websocket

router = APIRouter()


@router.get("/", response_model=list[OrderResponse])
async def get_orders(db: AgnosticCollection = Depends(get_db)):
    """
    Get all orders
    """

    orders = await db["orders"].find().to_list(None)
    return orders


@router.post("/", response_model=dict)
async def create_order(
    background_tasks: BackgroundTasks,
    order: OrderRequest,
    db: AgnosticCollection = Depends(get_db),
    access_token: str = Depends(get_access_token)
):
    """
    Create new order
    """

    order_service = OrderService(db)
    order = {
        **order.dict(),
        "price": float(order.price),
        "volume": float(order.volume),
        "datetime": datetime.utcnow().isoformat(),
    }
    new_order = await order_service.get_order_by_user_type_name_price(
        **order
    )
    if new_order:
        new_order["volume"] += order["volume"]
        created = False
    else:
        new_order = order
        created = True

    bulk_operations, users_to_update_balance, new_tickers = await order_service.update_orders_by_new_order(
        new_order
    )

    if created:
        bulk_operations.append(InsertOne(new_order))
    else:
        bulk_operations.append(
            UpdateOne(
                {"_id": ObjectId(new_order["_id"])},
                {"$set": {"volume": new_order["volume"]}},
            )
        )
    await db["orders"].bulk_write(bulk_operations)

    # send ticker to websocket
    if new_tickers:
        await db["tickers"].insert_many(new_tickers)
        background_tasks.add_task(
            send_tickers_by_websocket, new_order["name"], new_tickers
        )
        
    return JSONResponse(
        status_code=201, content=users_to_update_balance
    )


@router.get("/last/{order_name}", response_model=OrdersLast)
async def get_last_orders(order_name: str, db: AgnosticCollection = Depends(get_db)):
    """
    Get last orders grouped by price and volume sum
    """
    
    order_service = OrderService(db)
    orders = await order_service.get_last_orders(order_name)
    res = {"BUY": [], "SELL": []}
    if orders:
        for order in orders:
            if order["type"] == "BUY":
                res["BUY"] = order["data"]
            else:
                res["SELL"] = order["data"]
    return res
