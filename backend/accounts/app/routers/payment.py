from typing import Optional
from fastapi import APIRouter, Depends, Header, Request, status
from app.core import settings

from app.core.dependencies import get_payment_service, get_request_user
from app.models import User
from app.schemas import (
    PublishableKeyResponseSchema,
    DepositRequestSchema,
    DepositResponseSchema,
    WebHookSchema,
)
from app.services import PaymentService

router = APIRouter(prefix="/payment", tags=["payment"])


@router.get(
    "/publishable-key",
    summary="Get publishable key",
    description="Get publishable key for Stripe",
    response_model=PublishableKeyResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_publishable_key():
    return PublishableKeyResponseSchema(
        publishable_key=settings.STRIPE_PUBLIC_KEY
    )


@router.post(
    "/deposit",
    summary="Deposit",
    description="Deposit money to your balance",
    response_model=DepositResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def deposit(
    data: DepositRequestSchema,
    payment_service: PaymentService = Depends(get_payment_service),
    user: User = Depends(get_request_user),
):
    payment_intent = payment_service.create_payment_intent(
        customer_id=user.id, amount=data.amount, currency=data.currency
    )
    return DepositResponseSchema(
        client_secret=payment_intent.client_secret,
        publishable_key=settings.STRIPE_PUBLIC_KEY,
    )


@router.post(
    "/webhook",
    summary="Webhook",
    description="Webhook for Stripe",
    status_code=status.HTTP_200_OK,
)
async def webhook(
    request: Request,
    request_data: WebHookSchema,
    stripe_signature: Optional[str] = Header(None),
    payment_service: PaymentService = Depends(get_payment_service),
):
    data = await request.body()
    event = payment_service.get_event(data, stripe_signature)
    if request_data.type == "payment_intent.succeeded":
        await payment_service.payment_intent_confirm(event["data"]["object"])
