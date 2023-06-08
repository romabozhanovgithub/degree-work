from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import settings
from app.db.utils import connect_to_mongo, close_mongo_connection
from app.routers import order_router
from app.core.rabbitmq import pika_client

app = FastAPI(title=settings.APP_TITLE)

# MIDDLEWARES
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS
app.include_router(order_router)


# EVENTS
@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    await connect_to_mongo()
    print("Connected to MongoDB")
    print("Connecting to RabbitMQ...")
    await pika_client.connect()
    print("Connected to RabbitMQ")


@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down...")
    await close_mongo_connection()
    print("Disconnected from MongoDB")
    print("Closing RabbitMQ connection...")
    await pika_client.connection.close()
    print("RabbitMQ connection closed")
