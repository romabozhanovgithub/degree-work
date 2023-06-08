from typing import Any, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    ENV: str = "dev"
    DEBUG: bool = True
    SECRET_KEY: str
    APP_TITLE: str = "Accounts"
    # DATABASE
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_URL: Optional[str]
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    # GOOGLE
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    # FRONTEND
    FRONTEND_URL: str
    FRONTEND_RESET_PASSWORD_CONFIRM_URL: str
    # EMAIL
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str
    EMAIL_FROM_NAME: str
    VERIFY_EMAIL_TOKEN_EXPIRE_MINUTES: int = 10
    RESET_PASSWORD_TOKEN_EXPIRE_MINUTES: int = 10
    # STRIPE
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLIC_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    # BALANCE
    BALANCE_TYPES: list[str]
    # RABBITMQ
    RABBITMQ_URL: str
    RABBITMQ_EXCHANGE_NAME: str
    RABBITMQ_ACCOUNTS_QUEUE_NAME: str
    RABBITMQ_WEBSOCKET_QUEUE_NAME: str

    @validator("DB_URL", pre=True)
    def assemble_db_connection(
        cls, v: Optional[str], values: dict[str, str]
    ) -> str:
        if isinstance(v, str):
            return v
        return (
            f"{values['DB_HOST']}{values['DB_USER']}:{values['DB_PASSWORD']}"
            f"@{values['DB_NAME']}:{values['DB_PORT']}"
        )

    class Config:
        case_sensitive = True
        env_file = "./system_configs/.env"

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            if field_name == "BALANCE_TYPES":
                return raw_val.split(",")
            return super().parse_env_var(field_name, raw_val)


settings = Settings()
