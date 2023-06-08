from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import (
    get_auth_service,
    get_balance_repository,
    get_email_service,
    get_payment_service,
    get_request_user,
    get_user_repository,
)
from app.core.exceptions import (
    UnverifiedUserException,
    EmailDoesNotExistException,
)
from app.models import User
from app.repositories import UserRepository, BalanceRepository
from app.schemas import (
    AccessTokenSchema,
    UserResponseSchema,
    SignUpSchema,
    ResetPasswordSchema,
    ResetPasswordConfirmSchema,
)
from app.services import AuthService, EmailService, PaymentService
from app.core.utils import oauth

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    summary="Login",
    description="Login with username and password",
    response_model=AccessTokenSchema,
    status_code=status.HTTP_200_OK,
)
async def login(
    background_tasks: BackgroundTasks,
    data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    email_service: EmailService = Depends(get_email_service),
):
    user = await auth_service.authenticate_user(data.username, data.password)
    if not user.is_verified:
        await email_service.send_verify_email(
            user.email, background_tasks, background=True
        )
        raise UnverifiedUserException
    access_token = auth_service.create_access_token(user.email)
    return AccessTokenSchema(access_token=access_token)


@router.post(
    "/sign-up",
    summary="Sign up",
    description="Sign up with username and password",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def sign_up(
    data: SignUpSchema,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service),
    email_service: EmailService = Depends(get_email_service),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
):
    user = await auth_service.sign_up_user(
        data.email, data.password, data.first_name, data.last_name
    )
    await balance_repository.init_user_balance(user)
    await email_service.send_verify_email(
        user.email, background_tasks, background=True
    )
    return UserResponseSchema.from_orm(user)


@router.get(
    "/verify-email",
    summary="Verify email",
    description="Verify email with token",
    status_code=status.HTTP_200_OK,
)
async def verify_email(
    token: str,
    auth_service: AuthService = Depends(get_auth_service),
    payment_service: PaymentService = Depends(get_payment_service),
):
    user = await auth_service.verify_email(token)
    payment_service.create_customer(user)


@router.post(
    "/reset-password",
    summary="Reset password",
    description="Reset password with email",
    status_code=status.HTTP_200_OK,
)
async def reset_password(
    reset_password: ResetPasswordSchema,
    background_tasks: BackgroundTasks,
    email_service: EmailService = Depends(get_email_service),
    user_repository: UserRepository = Depends(get_user_repository),
):
    user = await user_repository.get_user_by_email(reset_password.email)
    if user is None:
        raise EmailDoesNotExistException()
    await email_service.send_reset_password_email(
        reset_password.email, background_tasks, background=True
    )


@router.post(
    "/reset-password/confirm",
    summary="Reset password confirm",
    description="Reset password confirm with token",
    status_code=status.HTTP_200_OK,
)
async def reset_password_confirm(
    token: str,
    reset_password: ResetPasswordConfirmSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.reset_password(token, reset_password.new_password)


@router.get(
    "/verify-token",
    summary="Verify token",
    description="Verify token",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def verify_token(
    user: User = Depends(get_request_user),
):
    return UserResponseSchema.from_orm(user)


@router.get(
    "/google",
    summary="Google Auth",
    response_model=AccessTokenSchema,
    status_code=status.HTTP_200_OK,
)
async def google_auth(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> AccessTokenSchema:
    user = await auth_service.google_authenticate_user(request)
    token = auth_service.create_access_token(user.email)
    return AccessTokenSchema(
        access_token=token,
    )


@router.get(
    "/google/login",
    summary="Google Login",
)
async def google_login(
    request: Request,
) -> None:
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, str(redirect_uri))
