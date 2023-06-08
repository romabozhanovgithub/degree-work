from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_auth_service, get_balance_repository
from app.core.utils import oauth2_scheme
from app.repositories import BalanceRepository
from app.schemas import (
    UserResponseSchema,
    UserWithBalaceResponseSchema,
    BalanceUpdateSchema,
)
from app.services import AuthService

router = APIRouter(prefix="/user", tags=["user"])


@router.get(
    "/me",
    summary="Get current user",
    description="Get current user",
    response_model=UserWithBalaceResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_current_user(token, True)
    return UserWithBalaceResponseSchema.from_orm(user)


@router.post(
    "/new-order",
    summary="Update balance",
    description="Update balance",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def new_order(
    balance: BalanceUpdateSchema,
    token: str = Depends(oauth2_scheme),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_current_user(token, True, balance.currency)
    if user.balances[0].amount < balance.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough balance",
        )
    user.balances[0].amount -= balance.amount
    await balance_repository.update_balance(user.balances[0])
    return UserResponseSchema.from_orm(user)
