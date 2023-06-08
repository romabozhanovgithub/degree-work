import pytest
from app.core import settings

from app.models import Balance
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
async def test_init_user_balance(
    test_db,
    auth_service: AuthService,
    balance_repository: BalanceRepository,
):
    user = await _create_test_user(auth_service)
    user_balance = await balance_repository.init_user_balance(user)
    assert len(user_balance) == len(settings.BALANCE_TYPES)
    assert user_balance[0].user_id == user.id
    assert user_balance[0].amount == 0


@pytest.mark.asyncio
async def test_create_balance(
    test_db, auth_service: AuthService, balance_repository: BalanceRepository
):
    user = await _create_test_user(auth_service)
    balance = await balance_repository.create_balance(
        Balance(currency="USD", user=user)
    )
    assert balance.id is not None
    assert balance.currency == "USD"
    assert balance.user_id == user.id
    assert balance.amount == 0


@pytest.mark.asyncio
async def test_get_balance_by_id(
    test_db, auth_service: AuthService, balance_repository: BalanceRepository
):
    user = await _create_test_user(auth_service)
    balance = await balance_repository.create_balance(
        Balance(currency="USD", user=user)
    )
    balance_from_db = await balance_repository.get_balance_by_id(balance.id)
    assert balance_from_db.id == balance.id


@pytest.mark.asyncio
async def test_get_user_balance_by_currency(
    test_db, auth_service: AuthService, balance_repository: BalanceRepository
):
    user = await _create_test_user(auth_service)
    balance = await balance_repository.create_balance(
        Balance(currency="USD", user=user)
    )
    balance_from_db = await balance_repository.get_user_balance_by_currency(
        user.id, "USD"
    )
    assert balance_from_db.id == balance.id


@pytest.mark.asyncio
async def test_get_user_balance(
    test_db, auth_service: AuthService, balance_repository: BalanceRepository
):
    user = await _create_test_user(auth_service)
    await balance_repository.create_balance(
        Balance(currency="USD", user=user)
    )
    balance_from_db = await balance_repository.get_user_balances(user.id)
    assert balance_from_db[0].user_id == user.id


@pytest.mark.asyncio
async def test_update_balance(
    test_db, auth_service: AuthService, balance_repository: BalanceRepository
):
    user = await _create_test_user(auth_service)
    balance = await balance_repository.create_balance(
        Balance(currency="USD", user=user)
    )
    balance.amount = 100
    balance_from_db = await balance_repository.update_balance(balance)
    assert balance_from_db.amount == 100
