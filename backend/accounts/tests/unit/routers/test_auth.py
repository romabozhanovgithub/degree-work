from unittest.mock import patch
from fastapi import status
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.services import AuthService


async def _create_test_user(auth_service: AuthService):
    user = await auth_service.sign_up_user(
        first_name="Test",
        last_name="User",
        email="test.user@test.com",
        password="password",
    )
    return user


@patch("app.services.email.EmailService.send_verify_email")
def test_sign_up(mock_send_verify_email, test_db):
    with TestClient(app) as client:
        response = client.post(
            "/auth/sign-up/",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@test.com",
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() is not None
        assert mock_send_verify_email.called is True


@pytest.mark.asyncio
@patch("app.services.email.EmailService.send_verify_email")
async def test_sign_up_existing_user(
    mock_send_verify_email, test_db, auth_service
):
    with TestClient(app) as client:
        user_in_db = await _create_test_user(auth_service)
        response = client.post(
            "/auth/sign-up/",
            json={
                "first_name": user_in_db.first_name,
                "last_name": user_in_db.last_name,
                "email": user_in_db.email,
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock_send_verify_email.assert_not_called()


@pytest.mark.asyncio
async def test_login(test_db, auth_service, user_repository):
    with TestClient(app) as client:
        user_in_db = await _create_test_user(auth_service)
        user_in_db.is_verified = True
        await user_repository.update_user(user_in_db)
        response = client.post(
            "/auth/login/",
            data={"username": user_in_db.email, "password": "password"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is not None


@pytest.mark.asyncio
async def test_login_unverified_user(test_db, auth_service):
    with TestClient(app) as client:
        user_in_db = await _create_test_user(auth_service)
        response = client.post(
            "/auth/login/",
            data={"username": user_in_db.email, "password": "password"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_login_invalid_credentials(
    test_db, auth_service, user_repository
):
    with TestClient(app) as client:
        user_in_db = await _create_test_user(auth_service)
        user_in_db.is_verified = True
        await user_repository.update_user(user_in_db)
        response = client.post(
            "/auth/login/",
            data={"username": user_in_db.email, "password": "wrong_password"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@patch("app.services.payment.PaymentService.create_customer")
async def test_verify_email(
    mock_create_customer, test_db, auth_service, email_service
):
    with TestClient(app) as client:
        user_in_db = await _create_test_user(auth_service)
        token = email_service._create_token(user_in_db.email, 5)
        response = client.get(f"/auth/verify-email?token={token}")
        assert response.status_code == status.HTTP_200_OK
        mock_create_customer.assert_called_once()


@pytest.mark.asyncio
async def test_verify_email_invalid_token(
    test_db, auth_service, email_service
):
    with TestClient(app) as client:
        user_in_db = await _create_test_user(auth_service)
        token = email_service._create_token(user_in_db.email, -5)
        response = client.get(f"/auth/verify-email?token={token}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@patch("app.services.email.EmailService.send_reset_password_email")
async def test_reset_password(
    mock_send_reset_password_email, test_db, auth_service
):
    with TestClient(app) as client:
        user_in_db = await _create_test_user(auth_service)
        response = client.post(
            "/auth/reset-password/",
            json={"email": user_in_db.email},
        )
        print(response.json())
        assert response.status_code == status.HTTP_200_OK
        assert mock_send_reset_password_email.called is True


@pytest.mark.asyncio
async def test_reset_password_invalid_email(
    test_db, auth_service, email_service
):
    with TestClient(app) as client:
        response = client.post(
            "/auth/reset-password/",
            json={"email": "john.doe@test.com"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_reset_password_confirm(test_db, auth_service, email_service):
    with TestClient(app) as client:
        user_in_db = await _create_test_user(auth_service)
        token = email_service._create_token(user_in_db.email, 5)
        response = client.post(
            f"/auth/reset-password/confirm?token={token}",
            json={"new_password": "new_password"},
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_reset_password_confirm_invalid_token(
    test_db, auth_service, email_service
):
    with TestClient(app) as client:
        user_in_db = await _create_test_user(auth_service)
        token = email_service._create_token(user_in_db.email, -5)
        response = client.post(
            f"/auth/reset-password/confirm?token={token}",
            json={"new_password": "new_password"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_verify_token(test_db, auth_service, user_repository):
    with TestClient(app) as client:
        user_in_db = await _create_test_user(auth_service)
        user_in_db.is_verified = True
        await user_repository.update_user(user_in_db)
        token = auth_service.create_access_token(user_in_db.email)
        response = client.get(
            "/auth/verify-token",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == user_in_db.email
