from datetime import datetime
from typing import Optional
from bson import ObjectId
from pymongo import UpdateOne
from pymongo.results import UpdateResult
from motor.core import AgnosticCollection

from app.utils import request, add_user_balance, send_ticker_by_websocket


class OrderService:
    def __init__(self, db: AgnosticCollection):
        self.db = db

    async def get_orders(
        self, sort = ("datetime", -1), limit: Optional[int] = None
    ) -> list:
        """
        Get all orders, sort and limit are optional
        """

        orders = await self.db["orders"].find(
            {}, sort=[sort], limit=limit
        ).to_list(None)
        return orders

    async def get_order_by_id(self, order_id: str) -> dict:
        """
        Get order by id
        """

        order = await self.db["orders"].find_one({"_id": ObjectId(order_id)})
        return order

    async def get_orders_by_user(self, user: str) -> list:
        """
        Get orders by user
        """

        orders = await self.db["orders"].find(
            {"user": user}, sort=[("datetime", -1)]
        ).to_list(None)
        return orders

    async def get_order_by_user_type_name_price(
        self, user: str,
        type: str,
        name: str,
        price: float,
        is_active: bool = True,
        **kwargs
    ) -> dict:
        """
        Get order by user, type, name and price
        """

        order = await self.db["orders"].find_one(
            {
                "user": user,
                "type": type,
                "name": name,
                "price": price,
                "volume": {
                    "$gt": 0
                },
            }
        )
        return order

    async def get_orders_for_create(self, order: dict) -> list:
        """
        Get orders for create
        """

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
                        "volume": {
                            "$gt": 0
                        }
                    }
                },
                {
                    "$sort": {
                        "price": 1
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
                        "volume": {
                            "$gt": 0
                        }
                    }
                },
                {
                    "$sort": {
                        "price": -1
                    }
                },
            ]

        orders = await self.db["orders"].aggregate(pipeline).to_list(None)
        return orders

    async def get_last_orders(
        self, order_name: str, limit: int = 10
    ) -> list:
        """
        Get last orders grouped by price and volume sum
        """

        pipeline = [
            {
                "$match": {
                    "name": order_name,
                    "volume": {
                        "$gt": 0
                    }
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
                        "$slice": ["$data", limit]
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

        orders: list = await self.db["orders"].aggregate(
            pipeline
        ).to_list(None)
        res = {"BUY": [], "SELL": []}
        if orders:
            for order in orders[0]["data"]:
                if order["type"] == "BUY":
                    res["BUY"] = order["data"]
                else:
                    res["SELL"] = order["data"]
        return res

    async def update_order_by_id(
        self, order_id: ObjectId, update: dict
    ) -> UpdateResult:
        """
        Update order by id
        """

        updated_order: UpdateResult = await self.db["orders"].update_one(
            {"_id": order_id},
            {"$set": update}
        )
        return updated_order

    async def update_orders_by_new_order(self, new_order: dict):
        """
        Update orders by new order
        """

        # get orders for create
        print(f"New order: {new_order}")
        existing_orders = await self.get_orders_for_create(new_order)
        print(f"Existing orders: {existing_orders}")

        # update orders
        bulk_operations = []
        users_to_update_balance = {}
        new_tickers = []
        for existing_order in existing_orders:
            volume = min(new_order["volume"], existing_order["volume"])
            new_order["volume"] -= volume

            # update existing order
            bulk_operations.append(
                UpdateOne(
                    {"_id": existing_order["_id"]},
                    {
                        "$inc": {
                            "volume": -volume
                        }
                    }
                )
            )

            # update user balance
            if existing_order["type"] == "SELL":
                price = new_order["price"]
            else:
                price = existing_order["price"]
            add_user_balance(
                    users_to_update_balance,
                    {
                        **existing_order,
                        "volume": volume,
                        "price": price
                    }
                )
            add_user_balance(
                users_to_update_balance,
                {
                    **new_order,
                    "volume": volume,
                    "price": price
                }
            )
            
            if new_order["user"] != existing_order["user"]:
                # add ticker
                new_tickers.append(
                    {
                        "name": new_order["name"],
                        "price": price,
                        "volume": volume,
                        "datetime": datetime.utcnow().isoformat()
                    }
                )

            # if new order volume is 0, break
            if new_order["volume"] == 0:
                break

        return bulk_operations, users_to_update_balance, new_tickers
