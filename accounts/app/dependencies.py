import os
from app.db import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_access_token():
    return os.environ.get('ACCESS_TOKEN')
