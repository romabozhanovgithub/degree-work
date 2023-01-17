from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.schemas import UserCreate, UserResponse, Token
from app.models import User
from app.dependencies import get_db
from app.utils import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_active_user, get_password_hash, verify_password


router = APIRouter()


@router.post(
    '/signup',
    summary="Create new user",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
)
async def create_user(data: UserCreate, db: Session = Depends(get_db)):
    """
    Create new user. If user with this email already exist, raise HTTPException.
    """

    user = db.query(User).filter(User.email == data.email).first()
    if user is not None:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )
    user = {
        'first_name': data.first_name,
        'last_name': data.last_name,
        'email': data.email,
        'hashed_password': get_password_hash(data.password),
    }
    db_user = User(**user)
    db.add(db_user)
    db.commit()
    return db_user


@router.post(
    '/login',
    summary="Login user",
    status_code=status.HTTP_200_OK,
    response_model=Token
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Login user. If user is authenticated, return access token, otherwise raise
    HTTPException.
    """

    user: User = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    '/me',
    summary="Get current user",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse
)
async def get_current_user(
    db: Session = Depends(get_db), user: str = Depends(get_current_active_user)
):
    """
    Get current user from token. If user is authenticated, return user object,
    otherwise raise HTTPException.
    """

    return user
