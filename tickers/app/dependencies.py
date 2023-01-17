import os
from fastapi import HTTPException, Header
from motor.core import AgnosticClient
from app.db import client

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


def get_db() -> AgnosticClient:
    return client["tickers_db"]["tickers"]


# Function to get access token from request header, that will be send by another service
def get_access_token(x_access_token: str = Header(...)):
    if x_access_token == ACCESS_TOKEN:
        return x_access_token
    else:
        raise HTTPException(status_code=400, detail="Access token is missing or invalid")
