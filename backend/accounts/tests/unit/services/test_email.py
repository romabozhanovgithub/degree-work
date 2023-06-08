from unittest.mock import patch
from fastapi import BackgroundTasks
from fastapi_mail import MessageSchema, MessageType
import pytest

from app.services import EmailService, AuthService


def test_get_message(email_service: EmailService):
    message = email_service._get_message(
        subject="Test Subject",
        body={"test": "body"},
        email_to="john.doe@test.com",
    )
    assert message.subject == "Test Subject"
    assert message.template_body == {"test": "body"}
    assert message.recipients == ["john.doe@test.com"]
    assert message.subtype == MessageType.html
    assert isinstance(message, MessageSchema)


def test_create_token(email_service: EmailService):
    token = email_service._create_token(
        user_email="john.doe@test.com", expires=5
    )
    assert isinstance(token, str)


@patch("app.services.email.EmailService._create_token")
def test_create_verify_link(
    mock_create_token,
    email_service: EmailService,
):
    mock_create_token.return_value = "test_token"
    link = email_service._create_verify_link(user_email="john.doe@test.com")
    assert isinstance(link, str)
    assert link.startswith("http")
    assert "test_token" in link


@patch("app.services.email.EmailService._create_token")
def test_create_reset_password_link(
    mock_create_token,
    email_service: EmailService,
):
    mock_create_token.return_value = "test_token"
    link = email_service._create_reset_password_link(
        user_email="john.doe@test.com"
    )
    assert isinstance(link, str)
    assert link.startswith("http")
    assert "test_token" in link


@pytest.mark.asyncio
@patch("fastapi_mail.FastMail.send_message")
async def test_send_email_async(
    mock_send_message, email_service: EmailService
):
    message_data = {
        "subject": "Test Subject",
        "body": {"test": "body"},
        "email_to": "john.doe@test.com",
    }
    message = email_service._get_message(**message_data)
    await email_service._send_email_async(
        **message_data,
        template_name="test_template",
    )
    assert mock_send_message.called_once_with(
        message=message,
        template_name="test_template",
    )


@patch("fastapi.BackgroundTasks.add_task")
def test_send_email_background(mock_add_task, email_service: EmailService):
    message_data = {
        "subject": "Test Subject",
        "body": {"test": "body"},
        "email_to": "john.doe@test.com",
    }
    message = email_service._get_message(**message_data)
    email_service._send_email_background(
        background_tasks=BackgroundTasks(),
        **message_data,
        template_name="test_template",
    )
    assert mock_add_task.called_once_with(
        email_service.fm.send_message,
        message=message,
        template_name="test_template",
    )


@pytest.mark.asyncio
@patch("app.services.email.EmailService._send_email_async")
async def test_send_email(mock_send_email_async, email_service: EmailService):
    await email_service._send_email(
        subject="Test Subject",
        body={"test": "body"},
        email_to="john.doe@test.com",
        template_name="test_template",
        background_tasks=BackgroundTasks(),
    )
    assert mock_send_email_async.called


@pytest.mark.asyncio
@patch("app.services.email.EmailService._send_email")
async def test_send_verify_email(mock_send_email, email_service: EmailService):
    await email_service.send_verify_email(
        email_to="john.doe@test.com",
        background_tasks=BackgroundTasks(),
    )
    assert mock_send_email.called


@pytest.mark.asyncio
@patch("app.services.email.EmailService._send_email")
async def test_send_reset_password_email(
    mock_send_email,
    test_db,
    email_service: EmailService,
    auth_service: AuthService,
):
    await auth_service.sign_up_user(
        first_name="John",
        last_name="Doe",
        email="john.doe@test.com",
        password="test_password",
    )
    await email_service.send_reset_password_email(
        email_to="john.doe@test.com",
        background_tasks=BackgroundTasks(),
    )
    assert mock_send_email.called
