from fastapi import APIRouter, Request

from app.core.utils import templates

router = APIRouter(prefix="/payment", tags=["payment"])


@router.get("/deposite")
async def deposite(request: Request):
    return templates.TemplateResponse(
        "accounts/payment/deposite.html",
        {
            "request": request,
            "title": "Deposite",
        }
    )


@router.get("/success")
async def success(request: Request):
    return templates.TemplateResponse(
        "accounts/payment/success.html",
        {
            "request": request,
            "title": "Success",
        }
    )
