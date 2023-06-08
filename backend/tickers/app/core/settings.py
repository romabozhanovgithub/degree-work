from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    ENV: str = "dev"
    DEBUG: bool = True
    SECRET_KEY: str
    APP_TITLE: str = "Tickers"
    # DATABASE
    DB_NAME: str
    DB_URL: Optional[str]
    # ACCESS TOKEN
    VERIFY_TOKEN_URL: str
    CREATE_NEW_ORDER_URL: str
    # RABBITMQ
    RABBITMQ_URL: str
    RABBITMQ_EXCHANGE_NAME: str
    RABBITMQ_ACCOUNTS_QUEUE_NAME: str
    RABBITMQ_WEBSOCKET_QUEUE_NAME: str

    class Config:
        case_sensitive = True
        env_file = "./system_configs/.env"


settings = Settings()
