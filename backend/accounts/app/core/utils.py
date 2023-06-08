from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth

from app.core import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
starlette_config = Config(
    environ={
        "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
        "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
    }
)
oauth = OAuth(starlette_config)
templates = Jinja2Templates(directory="app/templates")
