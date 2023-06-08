from typing import Type

from app.repositories import BaseRepository


class BaseService:
    repository: Type[BaseRepository]

    def __init__(self, repository: Type[BaseRepository]) -> None:
        self.repository = repository
