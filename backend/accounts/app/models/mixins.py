import uuid
from sqlalchemy import Column, String


class UUIDMixin:
    id = Column(
        String(100), primary_key=True, default=lambda: str(uuid.uuid4())
    )
