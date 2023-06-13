from pydantic import BaseSettings


class Settings(BaseSettings):
    ENV: str = "dev"
    DEBUG: bool = True
    APP_TITLE: str = "Frontend"

    class Config:
        case_sensitive = True
        env_file = "./system_configs/.env"


settings = Settings()
