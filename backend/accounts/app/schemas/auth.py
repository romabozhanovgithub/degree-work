from typing import Optional
from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class SignUpSchema(LoginSchema):
    first_name: str
    last_name: str


class AccessTokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ResetPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordConfirmSchema(BaseModel):
    new_password: str


class CustomOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
    def __init__(
        self,
        grant_type: str = Form(default=None, regex="password"),
        username: Optional[str] = Form(default=None),
        email: EmailStr = Form(default=""),
        password: str = Form(default=""),
        scope: str = Form(default=""),
    ):
        super().__init__(
            grant_type=grant_type,
            username=username,
            password=password,
            scope=scope,
        )
