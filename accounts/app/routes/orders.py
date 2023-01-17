from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_access_token, get_db
from app.models import User, Order
from app.schemas import OrderCreate, OrdersLast, OrderResponse
from app.services import OrderService, UserService
from app.utils import get_current_active_user

router = APIRouter()


@router.post(
    "/create_order",
    summary="Create new order",
    status_code=status.HTTP_201_CREATED,
    response_model=OrderResponse
)
async def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    """
    Create new order. Sends request to orders service with access token.
    """
    order_service = OrderService(db)
    user_service = UserService(db)

    new_order = Order(
        ticker=data.ticker,
        price=data.price,
        volume=data.volume,
        type=data.type,
        user=user,
    )
    db.add(new_order)
    db.commit()

    # check existing orders
    
    # if order is buy, check if there is sell order with same ticker and lower or equal price
    # if order is sell, check if there is buy order with same ticker and higher or equal price

    if new_order.type == "BUY":
        existing_orders = order_service.get_orders_by_ticker_and_type(
            new_order.ticker, "SELL"
        ).filter(
            Order.price <= new_order.price
        ).all()
    else:
        existing_orders = order_service.get_orders_by_ticker_and_type(
            new_order.ticker, "BUY"
        ).filter(
            Order.price >= new_order.price
        ).all()
    
    if existing_orders:
        # update orders
        new_order, orders = order_service.update_orders(existing_orders, new_order)
        # update balance for users
        if new_order.type == "BUY":
            user_service.update_balance_by_orders(orders)
        else:
            user_service.update_balance_by_orders([{
                "user": new_order.user,
                "price": new_order.price,
                "volume": new_order.volume,
            }])
        db.commit()

    print(f"New order: {new_order}")
    return new_order


@router.get(
    "/user",
    summary="Get orders",
    status_code=status.HTTP_200_OK,
    response_model=list[OrderResponse]
)
async def get_orders(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    """
    Get orders for current user. Sends request to orders service with access token.
    """

    order_service = OrderService(db)
    orders = order_service.get_orders_by_user(user).all()
    print(f"Orders: {orders}")
    return orders


@router.get(
    "/last",
    summary="Get last order",
    status_code=status.HTTP_200_OK,
    response_model=OrdersLast
)
async def get_last_orders(
    db: Session = Depends(get_db),
):
    """
    Get last order for current user. Sends request to orders service with access token.
    """

    order_service = OrderService(db)
    buy_orders = order_service.get_last_order("BUY").all()
    sell_orders = order_service.get_last_order("SELL").all()
    return OrdersLast(buy=buy_orders, sell=sell_orders)
