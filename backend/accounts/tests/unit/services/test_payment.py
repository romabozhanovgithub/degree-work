from unittest.mock import patch
import pytest
from app.core import settings

from app.repositories import BalanceRepository
from app.services import AuthService, PaymentService


class MockPaymentIntent:
    def __init__(self, customer: str, amount: int):
        self.customer = customer
        self.amount = amount
        self.currency = "usd"


async def _create_test_user(auth_service: AuthService):
    user = await auth_service.sign_up_user(
        first_name="Test",
        last_name="User",
        email="test.user@test.com",
        password="password",
    )
    return user


def test_get_stripe_client(payment_service: PaymentService):
    stripe_client = payment_service._get_stripe_client()
    assert stripe_client is not None
    assert stripe_client.api_key == settings.STRIPE_SECRET_KEY


@pytest.mark.asyncio
@patch("stripe.Customer.create")
async def test_create_customer(
    mock_create,
    test_db,
    auth_service: AuthService,
    payment_service: PaymentService,
):
    user = await _create_test_user(auth_service)
    payment_service.create_customer(user)
    mock_create.assert_called_once_with(id=user.id, email=user.email)


@pytest.mark.asyncio
@patch("stripe.PaymentIntent.create")
async def test_create_payment_intent(
    mock_create,
    test_db,
    auth_service: AuthService,
    payment_service: PaymentService,
):
    user = await _create_test_user(auth_service)
    payment_service.create_payment_intent(100, user.id, "usd")
    mock_create.assert_called_once_with(
        amount=100,
        currency="usd",
        customer=user.id,
        payment_method_types=payment_service.payment_method_types,
        description="Payment for user",
    )


@pytest.mark.asyncio
async def test_payment_intent_confirm(
    test_db,
    auth_service: AuthService,
    payment_service: PaymentService,
    balance_repository: BalanceRepository,
):
    user = await _create_test_user(auth_service)
    await balance_repository.init_user_balance(user)
    await payment_service.payment_intent_confirm(
        MockPaymentIntent(user.id, 100)
    )
    balance = await balance_repository.get_user_balance_by_currency(
        user.id, "usd"
    )
    assert balance.amount == 100


@pytest.mark.asyncio
@patch("stripe.Webhook.construct_event")
async def test_get_event(
    mock_construct_event, payment_service: PaymentService
):
    payment_service.get_event({}, "test")
    mock_construct_event.assert_called_once_with(
        {}, "test", settings.STRIPE_WEBHOOK_SECRET
    )
