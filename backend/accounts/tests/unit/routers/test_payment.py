from unittest.mock import patch
from fastapi import status
from fastapi.testclient import TestClient
import pytest

from app.core import settings
from app.main import app
from app.repositories import UserRepository
from app.services import AuthService


class MockPaymentIntent:
    def __init__(self, client_secret: str):
        self.client_secret = client_secret


async def _create_test_user(auth_service: AuthService):
    user = await auth_service.sign_up_user(
        first_name="Test",
        last_name="User",
        email="test.user@test.com",
        password="password",
    )
    return user


@pytest.mark.asyncio
async def test_get_publishable_key():
    with TestClient(app) as client:
        response = client.get("/payment/publishable-key/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None
        assert response.json()["publishableKey"] == settings.STRIPE_PUBLIC_KEY


@pytest.mark.asyncio
@patch("app.services.payment.PaymentService.create_payment_intent")
async def test_deposit(
    mock_create_payment_intent,
    test_db,
    auth_service: AuthService,
    user_repository: UserRepository,
):
    with TestClient(app) as client:
        user_in_db = await _create_test_user(auth_service)
        user_in_db.is_verified = True
        await user_repository.update_user(user_in_db)
        token = auth_service.create_access_token(user_in_db.email)
        mock_create_payment_intent.return_value = MockPaymentIntent(
            "test_client_secret"
        )
        response = client.post(
            "/payment/deposit/",
            headers={
                "Authorization": f"Bearer {token}",
            },
            json={
                "amount": 1000,
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["clientSecret"] == "test_client_secret"
        assert response.json()["publishableKey"] == settings.STRIPE_PUBLIC_KEY
        assert mock_create_payment_intent.called_once_with(
            customer_id=user_in_db.id, amount=1000
        )


@pytest.mark.asyncio
@patch("app.services.payment.PaymentService.get_event")
@patch("app.services.payment.PaymentService.payment_intent_confirm")
async def test_webhook(
    mock_payment_intent_confirm,
    mock_get_event,
    test_db,
    auth_service: AuthService,
    user_repository: UserRepository,
):
    with TestClient(app) as client:
        user_in_db = await _create_test_user(auth_service)
        user_in_db.is_verified = True
        await user_repository.update_user(user_in_db)
        token = auth_service.create_access_token(user_in_db.email)
        response = client.post(
            "/payment/webhook/",
            headers={
                "Authorization": f"Bearer {token}",
                "stripe-signature": "test_signature",
            },
            json={
                "type": "payment_intent.succeeded",
                "data": {
                    "test": "test",
                },
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert mock_get_event.called_once_with(
            data=b'{"type": "payment_intent.succeeded", "data": {"test": "test"}}',  # noqa: E501
            signature="test_signature",
        )
        assert mock_payment_intent_confirm.called_once_with(
            event=mock_get_event.return_value
        )
