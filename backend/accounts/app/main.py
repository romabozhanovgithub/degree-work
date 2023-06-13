import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core import settings
from app.core.dependencies import get_session
from app.core.utils import oauth
from app.db import init_models  # noqa: F401
from app.repositories import BalanceRepository
from app.routers import auth_router, user_router, payment_router
from app.core.rabbitmq import pika_client
from app.core.rabbitmq.utils import consume_income_message

app = FastAPI(title=settings.APP_TITLE)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# GOOGLE
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",  # noqa E501
    client_kwargs={"scope": "openid email profile"},
)

# MIDDLEWARES
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(payment_router)


@app.on_event("startup")
async def startup_event():
    await init_models()
    async for session in get_session():
        balance_repository = BalanceRepository(session)
        break
    print("Starting up...")
    print("Connecting to RabbitMQ...")
    await pika_client.connect()
    print("Connected to RabbitMQ")
    asyncio.create_task(
        pika_client.consume_accounts_queue(
            consume_income_message, balance_repository=balance_repository
        )
    )


@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down...")
    print("Closing RabbitMQ connection...")
    await pika_client.connection.close()
    print("Closed RabbitMQ connection")
