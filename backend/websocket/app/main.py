from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import settings
from app.core.rabbitmq import pika_client
from app.routers import websocket_router

app = FastAPI(title=settings.APP_TITLE)

# MIDDLWARES
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTES
app.include_router(websocket_router)


@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    print("Connecting to RabbitMQ...")
    await pika_client.connect()
    print("Connection to RabbitMQ established.")


@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down...")
    print("Closing connection to RabbitMQ...")
    await pika_client.connection.close()
    print("Connection to RabbitMQ closed.")
