from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.dependencies import get_access_token, get_db
from app.models import User, UserBalance
from app.schemas import OrderCreate
from app.services import UserService
from app.utils import get_current_active_user, request

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
    access_token = Depends(get_access_token),
):
    """
    Create new order. Sends request to orders service with access token.
    """

    user_service = UserService(db)

    # check if user has enough balance
    user_balance: UserBalance = getattr(user.balance, data.ticker)
    if user_balance.volume < data.volume:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough balance",
        )

    user_balance.volume -= data.volume
    db.add(user_balance)

    users_to_update_balance = await request(
        "POST",
        "/orders/create_order",
        data.json(),
        access_token
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
        UserBalance.name.in_([data.ticker, "USD"])
    ).all()
    for user_balance in users_balance:
        user_balance.volume += users_to_update_balance[
            user_balance.user_id
        ][user_balance.name]
        db.add(user_balance)
    db.commit()
    
    return Response(status_code=status.HTTP_201_CREATED)
