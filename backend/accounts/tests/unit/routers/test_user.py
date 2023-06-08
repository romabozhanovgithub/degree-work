from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.repositories import BalanceRepository
from app.services import AuthService


async def _create_test_user(auth_service: AuthService):
    user = await auth_service.sign_up_user(
        first_name="Test",
        last_name="User",
        email="test.user@test.com",
        password="password",
    )
    return user


@pytest.mark.asyncio
async def test_get_current_user(
    test_db, auth_service: AuthService, balance_repository: BalanceRepository
):
    with TestClient(app) as client:
        user_in_db = await _create_test_user(auth_service)
        user_in_db.is_verified = True
        await auth_service.user_repository.update_user(user_in_db)
        await balance_repository.init_user_balance(user_in_db)
        token = auth_service.create_access_token(user_in_db.email)
        response = client.get(
            "/user/me/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json() is not None
        assert response.json()["email"] == user_in_db.email
        assert len(response.json()["balances"]) == len(user_in_db.balances)
