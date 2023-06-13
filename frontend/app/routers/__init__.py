from fastapi import APIRouter, Request

from app.core.utils import templates
from app.routers.accounts import auth_router  # noqa: F401
from app.routers.accounts import payment_router  # noqa: F401


router = APIRouter(prefix="", tags=["main"])


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Home",
        }
    )
