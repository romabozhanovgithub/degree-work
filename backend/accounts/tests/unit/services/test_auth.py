from unittest.mock import patch
import pytest

from app.core.exceptions import (
    UserInactiveException,
    InvalidCredentialsException,
    UnverifiedUserException,
    UserAlreadyExistsException,
)
from app.repositories import UserRepository
from app.services import AuthService
from app.models import User


def test_verify_password(auth_service: AuthService):
    password = "password"
    hashed_password = auth_service.get_password_hash(password)
    assert auth_service.verify_password(password, hashed_password) is True
    assert (
        auth_service.verify_password("wrong_password", hashed_password)
        is False
    )


def test_get_password_hash(auth_service: AuthService):
    password = "password"
    hashed_password = auth_service.get_password_hash(password)
    assert hashed_password != password
    assert auth_service.verify_password(password, hashed_password) is True


@patch("app.services.auth.AuthService._create_token")
def test_create_access_token(auth_service: AuthService):
    token = auth_service.create_access_token("test")
    assert token is not None
    assert auth_service._create_token.called_once_with("test", 1)


@patch("app.services.auth.AuthService._create_token")
def test_create_refresh_token(auth_service: AuthService):
    token = auth_service.create_refresh_token("test")
    assert token is not None
    assert auth_service._create_token.called_once_with("test", 1)


def test_create_token(auth_service: AuthService):
    token = auth_service._create_token("test", 1)
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_token(auth_service: AuthService):
    token = auth_service._create_token("test", 1)
    decoded_token = auth_service.decode_token(token)
    assert decoded_token is not None
    assert isinstance(decoded_token, dict)
    assert decoded_token["sub"] == "test"
    assert decoded_token["exp"] is not None
    assert isinstance(decoded_token["exp"], int)


@pytest.mark.asyncio
async def test_get_current_user(
    test_db, auth_service: AuthService, user_repository: UserRepository
):
    user = await user_repository.create_user(
        User(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password="password",
        )
    )
    token = auth_service.create_access_token(user.email)
    current_user = await auth_service.get_current_user(token)
    assert current_user is not None
    assert current_user.id == user.id


@pytest.mark.asyncio
async def test_get_current_active_user(
    test_db, auth_service: AuthService, user_repository: UserRepository
):
    user = await user_repository.create_user(
        User(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password="password",
            is_verified=True,
        )
    )
    token = auth_service.create_access_token(user.email)
    current_user = await auth_service.get_current_active_user(token)
    assert current_user is not None
    assert current_user.id == user.id
    assert current_user.is_active is True


@pytest.mark.asyncio
async def test_get_current_active_user_inactive(
    test_db, auth_service: AuthService, user_repository: UserRepository
):
    user = await user_repository.create_user(
        User(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password="password",
            is_active=False,
        )
    )
    token = auth_service.create_access_token(user.email)
    with pytest.raises(UserInactiveException):
        await auth_service.get_current_active_user(token)


@pytest.mark.asyncio
async def test_get_current_active_user_unverified(
    test_db, auth_service: AuthService, user_repository: UserRepository
):
    user = await user_repository.create_user(
        User(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password="password",
            is_verified=False,
        )
    )
    token = auth_service.create_access_token(user.email)
    with pytest.raises(UnverifiedUserException):
        await auth_service.get_current_active_user(token)


@pytest.mark.asyncio
async def test_authenticate_user(
    test_db, auth_service: AuthService, user_repository: UserRepository
):
    hashed_password = auth_service.get_password_hash("password")
    user = await user_repository.create_user(
        User(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password=hashed_password,
        )
    )
    authenticated_user = await auth_service.authenticate_user(
        user.email, "password"
    )
    assert authenticated_user is not None
    assert authenticated_user.id == user.id


@pytest.mark.asyncio
async def test_authenticate_user_invalid_credentials(
    test_db, auth_service: AuthService, user_repository: UserRepository
):
    hashed_password = auth_service.get_password_hash("password")
    user = await user_repository.create_user(
        User(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password=hashed_password,
        )
    )
    with pytest.raises(InvalidCredentialsException):
        await auth_service.authenticate_user(user.email, "wrong_password")


@pytest.mark.asyncio
async def test_authenticate_user_inactive(
    test_db, auth_service: AuthService, user_repository: UserRepository
):
    hashed_password = auth_service.get_password_hash("password")
    user = await user_repository.create_user(
        User(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password=hashed_password,
            is_active=False,
        )
    )
    with pytest.raises(UserInactiveException):
        await auth_service.authenticate_user(user.email, "password")


@pytest.mark.asyncio
async def test_sign_up(test_db, auth_service: AuthService):
    user = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@test.com",
        "password": "password",
    }
    created_user = await auth_service.sign_up_user(**user)
    assert created_user is not None
    assert created_user.id is not None
    assert created_user.first_name == user["first_name"]
    assert created_user.last_name == user["last_name"]
    assert created_user.email == user["email"]
    assert created_user.is_active is True
    assert created_user.is_verified is False


@pytest.mark.asyncio
async def test_sign_up_existing_user(
    test_db, auth_service: AuthService, user_repository: UserRepository
):
    user = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@test.com",
        "password": "password",
    }
    await user_repository.create_user(
        User(
            first_name=user["first_name"],
            last_name=user["last_name"],
            email=user["email"],
            password=auth_service.get_password_hash(user["password"]),
        )
    )
    with pytest.raises(UserAlreadyExistsException):
        await auth_service.sign_up_user(**user)


@pytest.mark.asyncio
async def test_verify_email(
    test_db, auth_service: AuthService, user_repository: UserRepository
):
    hashed_password = auth_service.get_password_hash("password")
    user = await user_repository.create_user(
        User(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password=hashed_password,
        )
    )
    token = auth_service.create_access_token(user.email)
    await auth_service.verify_email(token)
    updated_user = await user_repository.get_user_by_email(user.email)
    assert updated_user is not None
    assert updated_user.is_verified is True


@pytest.mark.asyncio
async def test_verify_email_invalid_credentials(
    test_db, auth_service: AuthService, user_repository: UserRepository
):
    hashed_password = auth_service.get_password_hash("password")
    await user_repository.create_user(
        User(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password=hashed_password,
        )
    )
    token = auth_service.create_access_token("invalid")
    with pytest.raises(InvalidCredentialsException):
        await auth_service.verify_email(token)


@pytest.mark.asyncio
async def test_reset_password(
    test_db, auth_service: AuthService, user_repository: UserRepository
):
    hashed_password = auth_service.get_password_hash("password")
    user = await user_repository.create_user(
        User(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password=hashed_password,
        )
    )
    token = auth_service.create_access_token(user.email)
    await auth_service.reset_password(token, "new_password")
    updated_user = await user_repository.get_user_by_email(user.email)
    assert updated_user is not None
    assert updated_user.password != hashed_password


@pytest.mark.asyncio
async def test_reset_password_invalid_credentials(
    test_db, auth_service: AuthService, user_repository: UserRepository
):
    hashed_password = auth_service.get_password_hash("password")
    await user_repository.create_user(
        User(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            password=hashed_password,
        )
    )
    token = auth_service.create_access_token("invalid")
    with pytest.raises(InvalidCredentialsException):
        await auth_service.reset_password(token, "new_password")
