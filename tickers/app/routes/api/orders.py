from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pymongo import UpdateOne
from motor.core import AgnosticCollection

from app.dependencies import get_db, get_access_token
from app.schemas import Order, OrderRequest, OrderResponse, OrdersLast

router = APIRouter()


@router.get("/", response_model=list[OrderResponse])
async def get_orders(db: AgnosticCollection = Depends(get_db)):
    """
    Get all orders
    """

    orders = await db["orders"].find().to_list(None)
    return orders


@router.post("/", response_model=OrderResponse)
async def create_order(
    order: OrderRequest,
    db: AgnosticCollection = Depends(get_db),
    access_token: str = Depends(get_access_token)
):
    """
    Create new order
    """

    order = {
        **order.dict(),
        "price": float(order.price),
        "volume": float(order.volume),
    }
    order = await db["orders"].insert_one(order)
    order = await db["orders"].find_one({"_id": order.inserted_id})

    # check existing orders
    # if order is buy, check if there is sell order with same ticker and lower or equal price
    # if order is sell, check if there is buy order with same ticker and higher or equal price
    if order["type"] == "BUY":
        pipeline = [
            {
                "$match": {
                    "name": order["name"],
                    "type": "SELL",
                    "price": {
                        "$lte": order["price"]
                    },
                    "is_active": True
                }
            },
            {
                "$sort": {
                    "price": -1
                }
            },
        ]
    else:
        pipeline = [
            {
                "$match": {
                    "name": order["name"],
                    "type": "BUY",
                    "price": {
                        "$gte": order["price"]
                    },
                    "is_active": True
                }
            },
            {
                "$sort": {
                    "price": -1
                }
            },
        ]

    existing_orders = await db["orders"].aggregate(pipeline).to_list(None)
    if existing_orders:
        for existing_order in existing_orders:
            # if order volume is bigger than existing order volume,
            # update existing order volume to 0
            # and decrease order volume by existing order volume,
            # also set is_active to False for existing order
            if order["volume"] > existing_order["volume"]:
                await db["orders"].update_one(
                    {"_id": existing_order["_id"]},
                    {
                        "$set": {
                            "volume": 0,
                            "is_active": False
                        }
                    }
                )
                order["volume"] -= existing_order["volume"]
            # if order volume is smaller than existing order volume,
            # update existing order volume by decreasing it by order volume
            # and set is_active to False and order volume to 0 for order,
            # also break the loop
            elif order["volume"] < existing_order["volume"]:
                # update in one query
                await db["orders"].bulk_write([
                    UpdateOne(
                        {"_id": existing_order["_id"]},
                        {
                            "$set": {
                                "volume": existing_order["volume"] - order["volume"]
                            }
                        }
                    ),
                    UpdateOne(
                        {"_id": order["_id"]},
                        {
                            "$set": {
                                "volume": 0,
                                "is_active": False
                            }
                        }
                    )
                ])
                break
            # if order volume is equal to existing order volume,
            # set is_active to False for both orders and volume to 0 for both orders
            # and break the loop
            else:
                # update in one query
                await db["orders"].bulk_write([
                    UpdateOne(
                        {"_id": existing_order["_id"]},
                        {
                            "$set": {
                                "volume": 0,
                                "is_active": False
                            }
                        }
                    ),
                    UpdateOne(
                        {"_id": order["_id"]},
                        {
                            "$set": {
                                "volume": 0,
                                "is_active": False
                            }
                        }
                    )
                ])
                break
    return order


@router.get("/{order_name}/last", response_model=OrdersLast)
async def get_last_orders(order_name: str, db: AgnosticCollection = Depends(get_db)):
    """
    Get last orders grouped by price and volume sum
    """
    pipeline = [
        {
            "$match": {
                "name": order_name,
                "is_active": True
            }
        },
        {
            "$group": {
                "_id": {
                    "type": "$type",
                    "price": "$price"
                },
                "volume": {
                    "$sum": "$volume"
                }
            }
        },
        {
            "$sort": {
                "_id.price": -1
            }
        },
        {
            "$group": {
                "_id": "$_id.type",
                "data": {
                    "$push": {
                        "price": "$_id.price",
                        "volume": "$volume"
                    }
                }
            }
        },
        {
            "$project": {
                "data": {
                    "$slice": ["$data", 10]
                },
                "type": "$_id"
            }
        },
        {
            "$group": {
                "_id": None,
                "data": {
                    "$push": {
                        "type": "$type",
                        "data": "$data"
                    }
                }
            },
        }
    ]

    orders: list = await db["orders"].aggregate(pipeline).to_list(None)
    
    res = {
        "BUY": [],
        "SELL": []
    }
    if orders:
        for order in orders[0]["data"]:
            if order["type"] == "BUY":
                res["BUY"] = order["data"]
            else:
                res["SELL"] = order["data"]
    return res
