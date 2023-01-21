from decimal import Decimal
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.dependencies import access_token, get_db
from app.models import User, UserBalance
from app.schemas import OrderCreate
from app.services import UserService
from app.utils import get_current_active_user, request
from app.exceptions import NOT_ENOUGH_BALANCE

router = APIRouter()


@router.post(
    "/create_order",
    summary="Create new order",
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
    access_token = Depends(access_token),
):
    """
    Create new order. Sends request to orders service with access token.
    """

    user_service = UserService(db)

    # check if user has enough 
    if data.type == "BUY":
        user_balance = user_service.get_user_balance(user, "USD")
        if user_balance.volume < data.volume * data.price:
            raise NOT_ENOUGH_BALANCE
        user_balance.volume -= data.volume * data.price
    elif data.type == "SELL":
        user_balance = user_service.get_user_balance(user, data.name)
        if user_balance.volume < data.volume:
            raise NOT_ENOUGH_BALANCE
        user_balance.volume -= data.volume
    
    db.add(user_balance)
    db.commit()

    users_to_update_balance = await request(
        url="/orders/",
        method="POST",
        data={
            "user": user.id,
            "name": data.name,
            "price": str(data.price),
            "volume": str(data.volume),
            "type": data.type,
        },
        access_token=access_token
    )
    if users_to_update_balance.status_code != 201:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while creating order",
        )

    users_to_update_balance = users_to_update_balance.json()
    # update user balance
    users_balance: list[UserBalance] = db.query(UserBalance).filter(
        UserBalance.user_id.in_(users_to_update_balance),
        UserBalance.name.in_([data.name, "USD"])
    ).all()
    for user_balance in users_balance:
        user_balance_update = users_to_update_balance[user_balance.user_id]
        if user_balance_update.get(user_balance.name):
            user_balance.volume += Decimal(user_balance_update[user_balance.name])
            db.add(user_balance)
    db.commit()
    
    return Response(status_code=status.HTTP_201_CREATED)
