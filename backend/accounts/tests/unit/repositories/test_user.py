import pytest

from app.repositories import UserRepository
from app.models import User


@pytest.mark.asyncio
async def test_create_user(test_db, user_repository: UserRepository):
    user = User(
        first_name="John",
        last_name="Doe",
        email="john.doe@test.com",
        password="password",
    )
    created_user = await user_repository.create_user(user)
    assert created_user.id is not None
    assert created_user.first_name == user.first_name
    assert created_user.last_name == user.last_name
    assert created_user.email == user.email
    assert created_user.is_verified is False
    assert created_user.is_google_account is False
    assert created_user.is_active is True
    assert created_user.is_superuser is False
    assert created_user.created_at is not None


@pytest.mark.asyncio
async def test_get_user_by_id(test_db, user_repository: UserRepository):
    created_user = await user_repository.create_user(
        User(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password="password",
        )
    )
    user = await user_repository.get_user_by_id(created_user.id)
    assert user is not None
    assert user.id == created_user.id


@pytest.mark.asyncio
async def test_get_user_by_id_returns_none(
    test_db, user_repository: UserRepository
):
    user = await user_repository.get_user_by_id("invalid-id")
    assert user is None


@pytest.mark.asyncio
async def test_get_user_by_email(test_db, user_repository: UserRepository):
    created_user = await user_repository.create_user(
        User(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password="password",
        )
    )
    user = await user_repository.get_user_by_email(created_user.email)
    assert user is not None
    assert user.id == created_user.id


@pytest.mark.asyncio
async def test_get_user_by_email_returns_none(
    test_db, user_repository: UserRepository
):
    user = await user_repository.get_user_by_email("invalid-email")
    assert user is None


@pytest.mark.asyncio
async def test_get_all_users(test_db, user_repository: UserRepository):
    await user_repository.create_user(
        User(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password="password",
        )
    )
    users = await user_repository.get_all_users()
    assert len(users) == 1


@pytest.mark.asyncio
async def test_update_user(test_db, user_repository: UserRepository):
    created_user = await user_repository.create_user(
        User(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password="password",
        )
    )
    created_user.first_name = "Jane"
    updated_user = await user_repository.update_user(created_user)
    assert updated_user.first_name == "Jane"
