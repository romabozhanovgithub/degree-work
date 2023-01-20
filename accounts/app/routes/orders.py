from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.ticker import TickerCreate
from app.dependencies import get_access_token, get_db
from app.models import User, Order
from app.schemas import OrderCreate, OrdersLast, OrderResponse
from app.services import OrderService, UserService
from app.utils import create_new_tickers_in_bulk, get_current_active_user

router = APIRouter()


@router.post(
    "/create_order",
    summary="Create new order",
    status_code=status.HTTP_201_CREATED,
    response_model=OrderResponse
)
async def create_order(
    background_tasks: BackgroundTasks,
    data: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
    access_token = Depends(get_access_token),
):
    """
    Create new order. Sends request to orders service with access token.
    """

    order_service = OrderService(db)
    user_service = UserService(db)

    # check if user has enough balance
    if data.type == "BUY":
        if user.balance < data.price * data.volume:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough balance",
            )

    # check if user already has order with same ticker and type
    new_order: Order = order_service.get_order_by_ticker_and_type(
        data.ticker, data.type
    ).filter(
        Order.user == user,
        Order.price == data.price,
    ).first()

    if new_order:
        # update order
        new_order.volume += data.volume
        db.add(new_order)
    else:
        # create order
        new_order = Order(
            ticker=data.ticker,
            price=data.price,
            volume=data.volume,
            type=data.type,
            user=user,
        )
        db.add(new_order)
    db.commit()
    print(f"Existing order: {new_order.volume}")

    if data.type == "BUY":
        user.balance -= data.price * data.volume
        db.add(user)
        db.commit()

    # check existing orders
    # if order is buy, check if there is sell order with same ticker and lower or equal price
    # if order is sell, check if there is buy order with same ticker and higher or equal price

    if new_order.type == "BUY":
        existing_orders = order_service.get_orders_by_ticker_and_type(
            new_order.ticker, "SELL"
        ).filter(
            Order.price <= new_order.price,
        ).all()
    else:
        existing_orders = order_service.get_orders_by_ticker_and_type(
            new_order.ticker, "BUY"
        ).filter(
            Order.price >= new_order.price,
        ).all()
    
    if existing_orders:
        # update orders
        old_volume = new_order.volume
        new_order, orders = order_service.update_orders(new_order, existing_orders)
        # update balance for users
        if new_order.type == "BUY": # if order is buy, update balance for seller
            user_service.update_balance_by_orders(orders, new_order.user)
        else:
            user_service.update_balance_by_orders([{
                "user": new_order.user,
                "price": new_order.price,
                "volume": old_volume - new_order.volume,
            }])
        db.commit()

        if orders:
            data = [
                {
                    **TickerCreate(
                        name=ticker["name"],
                        price=ticker["price"],
                        volume=ticker["volume"],
                        datetime=ticker["datetime"],
                        type=ticker["type"],
                    ).dict(),
                    "datetime": ticker["datetime"],
                }
                for ticker in orders
                if ticker["user"].email != user.email
            ]

            for ticker in data:
                print(f"Ticker: {ticker}")

            background_tasks.add_task(
                create_new_tickers_in_bulk,
                access_token=access_token,
                tickers=data,
                user=user,
            )

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
    "/{ticker}/last",
    summary="Get last order",
    status_code=status.HTTP_200_OK,
    response_model=OrdersLast
)
async def get_last_orders(
    ticker: str,
    db: Session = Depends(get_db),
):
    """
    Get last order for current user. Sends request to orders service with access token.
    """

    order_service = OrderService(db)
    buy_orders = order_service.get_last_order(
        ticker, "BUY", "DESC"
    ).all()
    sell_orders = order_service.get_last_order(
        ticker, "SELL", "DESC"
    ).all()
    return OrdersLast(buy=buy_orders, sell=sell_orders)
