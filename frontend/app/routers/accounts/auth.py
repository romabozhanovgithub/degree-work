from fastapi import APIRouter, Request

from app.core.utils import templates

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(
        "accounts/auth/login.html",
        {
            "request": request,
            "title": "Login",
        }
    )


@router.get("/signup")
async def signup(request: Request):
    return templates.TemplateResponse(
        "accounts/auth/signup.html",
        {
            "request": request,
            "title": "Signup",
        }
    )


@router.get("/signup/success")
async def signup_success(request: Request):
    return templates.TemplateResponse(
        "accounts/auth/signup_success.html",
        {
            "request": request,
            "title": "Signup Success",
        }
    )


@router.get("/verify")
async def verify(request: Request):
    return templates.TemplateResponse(
        "accounts/auth/verify.html",
        {
            "request": request,
            "title": "Verify",
        }
    )
