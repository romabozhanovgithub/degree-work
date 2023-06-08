from datetime import datetime, timedelta
from typing import Any
from fastapi import Request
from jose import JWTError, jwt
from passlib.context import CryptContext
from authlib.integrations.starlette_client import OAuthError

from app.core import settings
from app.core.utils import oauth
from app.core.exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    UserInactiveException,
    UserAlreadyExistsException,
    UnverifiedUserException,
)
from app.models import User
from app.repositories import UserRepository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        """
        Verify a plain password against a hashed password.
        """

        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hash a plain password.
        """

        return pwd_context.hash(password)

    def _create_token(self, subject: str | Any, expires: int) -> str:
        """
        Create JWT token.
        """

        expires_delta = datetime.utcnow() + timedelta(minutes=expires)
        to_encode = {"exp": expires_delta, "sub": subject}
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def create_access_token(self, subject: str | Any) -> str:
        """
        Create access token.
        """

        return self._create_token(
            subject, settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    def create_refresh_token(self, subject: str | Any) -> str:
        """
        Create refresh token.
        """

        return self._create_token(
            subject, settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES
        )

    def decode_token(self, token: str) -> dict[str, str | int]:
        """
        Decode JWT token.
        Throw an error if the token is invalid.
        """

        try:
            decoded_token = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return decoded_token
        except JWTError:
            raise InvalidTokenException()

    async def get_current_user(
        self, token: str, balance: bool = False, currency: str | None = None
    ) -> User:
        """
        Get current user.
        Throw an error if the token is invalid.
        """

        decoded_token = self.decode_token(token)
        user = await self.user_repository.get_user_by_email(
            decoded_token["sub"], balance, currency
        )
        if not user:
            raise InvalidTokenException()
        return user

    async def get_current_active_user(self, token: str) -> User:
        """
        Get current active user.
        Throw an error if the token is invalid or the user is inactive.
        """

        user = await self.get_current_user(token)
        if not user.is_active:
            raise UserInactiveException()
        if not user.is_verified:
            raise UnverifiedUserException()
        return user

    async def authenticate_user(self, email: str, password: str) -> User:
        """
        Authenticate a user.
        Throw an error if the credentials are invalid.
        """

        user = await self.user_repository.get_user_by_email(email)
        if not (user and self.verify_password(password, user.password)):
            raise InvalidCredentialsException()
        if user.is_active is False:
            raise UserInactiveException()
        return user

    async def sign_up_user(
        self, email: str, password: str, first_name: str, last_name: str
    ) -> User:
        """
        Sign up a user.
        Throw an error if the user already exists.
        """

        user = await self.user_repository.get_user_by_email(email)
        if user:
            raise UserAlreadyExistsException()
        user = await self.user_repository.create_user(
            User(
                email=email,
                password=self.get_password_hash(password),
                first_name=first_name,
                last_name=last_name,
            )
        )
        return user

    async def verify_email(self, token: str) -> User:
        """
        Verify a user.
        """

        email = self.decode_token(token)["sub"]
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise InvalidCredentialsException()
        user.is_verified = True
        user = await self.user_repository.update_user(user)
        return user

    async def reset_password(self, token: str, password: str) -> User:
        """
        Reset a user's password.
        """

        email = self.decode_token(token)["sub"]
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise InvalidCredentialsException()
        user.password = self.get_password_hash(password)
        user = await self.user_repository.update_user(user)
        return user

    async def google_authenticate_user(self, request: Request) -> User:
        """
        Authenticate a user with Google.
        """

        try:
            access_token = await oauth.google.authorize_access_token(request)
        except OAuthError:
            raise InvalidCredentialsException()
        user_data = access_token.get("userinfo")
        user = await self.user_repository.get_user_by_email(user_data["email"])
        if not user:
            user = await self.user_repository.create_user(
                User(
                    email=user_data["email"],
                    first_name=user_data["given_name"],
                    last_name=user_data["family_name"],
                    is_verified=True,
                    is_google_account=True,
                )
            )
        return user
