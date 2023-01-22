import os
from fastapi import APIRouter, Body, Header, Request, status
import stripe
from app.routes import users, orders

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(orders.router, prefix="/orders", tags=["orders"])


@router.post(
    "checkout",
    summary="Checkout order",
    status_code=status.HTTP_201_CREATED,
)
async def checkout():
    """
    """
    
    domain_url = "http://localhost:8000"
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": "price_1MSxamKWjgNN4QwtnIc0sqPz"
                },
            ],
            mode="payment",
            success_url=domain_url + "/api/v1/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "/api/v1/cancel",
        )
        return {"id": checkout_session.id}
    except Exception as e:
        return e


@router.get(
    "success",
    summary="Success page",
    status_code=status.HTTP_200_OK,
)
async def success():
    """
    """
    
    return "Success"


@router.get(
    "cancel",
    summary="Cancel page",
    status_code=status.HTTP_200_OK,
)
async def cancel():
    """
    """
    
    return "Cancel"


@router.post(
    "webhook",
    summary="Webhook",
    status_code=status.HTTP_200_OK,
)
async def webhook(
    request: Request,
    payload: bytes = Body(...),
    stripe_signature: str = Header(...),
):
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError as e:
        # Invalid payload
        return e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return e

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # Fulfill the purchase...
        print("Payment was successful.")
    else:
        print("Unhandled event type {}".format(event["type"]))

    return "Success"
