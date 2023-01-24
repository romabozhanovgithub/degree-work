import os

from fastapi import HTTPException, Header
from app.db import SessionLocal

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_access_token(x_access_token: str = Header(...)):
    if x_access_token == ACCESS_TOKEN:
        return x_access_token
    else:
        raise HTTPException(status_code=400, detail="Access token is missing or invalid")


def access_token():
    return os.environ.get('ACCESS_TOKEN')
