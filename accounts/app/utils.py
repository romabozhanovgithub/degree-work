from datetime import datetime, timedelta
import os
from typing import Any, List, Union
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import httpx
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import parse_obj_as
from sqlalchemy.orm import Session

from app.schemas.ticker import TickerCreate
from app.dependencies import get_db
from app.schemas import TokenData
from app.models import User

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']   # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']    # should be kept secret
TICKERS_SERVICE_URL = "http://tickers:8080/api"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/v1/users/login')


def verify_password(plain_password, hashed_password):
    """
    Verify a plain password against a hashed password.
    """

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Get password hash.
    """

    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any], expires_delta: int = None
) -> str:
    """
    Create access token.
    """

    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any], expires_delta: int = None
) -> str:
    """
    Create refresh token.
    """

    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=REFRESH_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticate user by email and password. If user is authenticated, return
    user object, otherwise return False.
    """

    user: User = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    """
    Get current user from token. If user is authenticated, return user object,
    otherwise raise HTTPException.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(
        User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
):
    """
    Get current active user. If user is active, return user object, otherwise
    raise HTTPException.
    """

    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def request(
    url: str,
    method: str,
    access_token: str,
    data: dict = None,
) -> httpx.Response:
    print(f"access_token: {access_token}")
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(
                f"{TICKERS_SERVICE_URL}{url}",
                headers={"x-access-token": f"{access_token}"}
            )
        elif method == "POST":
            response = await client.post(
                f"{TICKERS_SERVICE_URL}{url}",
                json=data,
                headers={"x-access-token": f"{access_token}"}
            )

    return response


async def create_new_tickers_in_bulk(
    tickers: list[dict[str, Any]], access_token: str, user: User
) -> None:
    """
    Create new tickers in bulk.
    """

    response = await request(
        url="/tickers/bulk",
        method="POST",
        access_token=access_token,
        data=tickers
    )
    # if response.status_code != 201:
    #     raise HTTPException(
    #         status_code=response.status_code,
    #         detail=response.json()
    #     )
