from datetime import datetime, timedelta
from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jose import jwt
from pydantic import EmailStr

from app.core import settings
from app.core.exceptions import InvalidUserResetPasswordException
from app.repositories import UserRepository

email_config = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_USERNAME,
    MAIL_PASSWORD=settings.EMAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_FROM,
    MAIL_FROM_NAME=settings.EMAIL_FROM_NAME,
    MAIL_SERVER=settings.EMAIL_HOST,
    MAIL_PORT=settings.EMAIL_PORT,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER="./app/templates/email",
)


class EmailService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository
        self.fm = FastMail(email_config)
        self.verify_template = "verify.html"
        self.reset_password_template = "reset_password.html"

    def _get_message(
        self, subject: str, email_to: str, body: dict
    ) -> MessageSchema:
        """
        This method is used to get the message object.
        """

        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            template_body=body,
            subtype=MessageType.html,
        )
        return message

    async def _send_email_async(
        self, subject: str, email_to: str, body: dict, template_name: str
    ) -> None:
        """
        This method is used to send the email asynchronously.
        """

        message = self._get_message(subject, email_to, body)
        await self.fm.send_message(message, template_name=template_name)

    def _send_email_background(
        self,
        background_tasks: BackgroundTasks,
        subject: str,
        email_to: str,
        body: dict,
        template_name: str,
    ) -> None:
        """
        This method is used to send the email in the background.
        """

        message = self._get_message(subject, email_to, body)
        background_tasks.add_task(
            self.fm.send_message, message, template_name=template_name
        )

    async def _send_email(
        self,
        subject: str,
        email_to: str,
        body: dict,
        template_name: str,
        background_tasks: BackgroundTasks,
        background: bool = False,
    ) -> None:
        """
        This method is used to send the email.
        Optionaly, you can send the email in the background
        by setting the background parameter to True.
        """

        if background:
            self._send_email_background(
                background_tasks, subject, email_to, body, template_name
            )
        else:
            await self._send_email_async(
                subject, email_to, body, template_name
            )

    def _create_token(self, user_email: EmailStr, expires: int) -> str:
        """
        Create JWT token.
        """

        expires_delta = datetime.utcnow() + timedelta(minutes=expires)
        to_encode = {"exp": expires_delta, "sub": user_email}
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def _create_verify_link(self, user_email: str) -> str:
        """
        This method is used to create the verification link.
        """

        token = self._create_token(
            user_email, settings.VERIFY_EMAIL_TOKEN_EXPIRE_MINUTES
        )
        return f"{settings.FRONTEND_URL}/auth/verify?token={token}"

    async def send_verify_email(
        self,
        email_to: str,
        background_tasks: BackgroundTasks,
        background: bool = False,
    ) -> None:
        """
        This method is used to send the verification email.
        Optionaly, you can send the email in the background
        by setting the background parameter to True.
        """

        subject = "Verify your email"
        verify_link = self._create_verify_link(email_to)
        body = {"verify_link": verify_link}
        await self._send_email(
            subject,
            email_to,
            body,
            self.verify_template,
            background_tasks,
            background,
        )

    def _create_reset_password_link(self, user_email: str) -> str:
        """
        This method is used to create the reset password link.
        """

        token = self._create_token(
            user_email, settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES
        )
        reset_password_link = settings.FRONTEND_RESET_PASSWORD_CONFIRM_URL
        return f"{settings.FRONTEND_URL}/{reset_password_link}?token={token}"

    async def send_reset_password_email(
        self,
        email_to: str,
        background_tasks: BackgroundTasks,
        background: bool = False,
    ) -> None:
        """
        This method is used to send the reset password email.
        Raises InvalidUserResetPasswordException if the user
        is a google account.

        Optionaly, you can send the email in the background
        by setting the background parameter to True.
        """

        user = await self.user_repository.get_user_by_email(email_to)
        if user.is_google_account:
            raise InvalidUserResetPasswordException()

        subject = "Reset password"
        reset_password_link = self._create_reset_password_link(email_to)
        body = {"reset_password_link": reset_password_link}
        await self._send_email(
            subject,
            email_to,
            body,
            self.reset_password_template,
            background_tasks,
            background,
        )
