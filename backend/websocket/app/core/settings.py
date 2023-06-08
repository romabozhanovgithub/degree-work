from pydantic import BaseSettings


class Settings(BaseSettings):
    ENV: str = "dev"
    DEBUG: bool = True
    APP_TITLE: str = "Websocket"
    # USER
    USER_INFO_URL: str
    # RABBITMQ
    RABBITMQ_URL: str
    RABBITMQ_EXCHANGE_NAME: str
    RABBITMQ_WEBSOCKET_QUEUE_NAME: str

    class Config:
        case_sensitive = True
        env_file = "./system_configs/.env"


settings = Settings()
