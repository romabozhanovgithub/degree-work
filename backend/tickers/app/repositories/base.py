from bson import ObjectId
from motor.core import AgnosticCollection
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.results import InsertOneResult

from app.core import settings
from app.db.client import get_client


class BaseRepository:
    collection_name: str
    order_by: str = "created_at"
    order: int = -1

    def __init__(
        self,
        client: AsyncIOMotorClient | None = None,
        collection_name: str | None = None,
    ) -> None:
        self.client = client or get_client()
        self.db = self.client[settings.DB_NAME]
        self.collection_name = collection_name or self.collection_name
        self.collection: AgnosticCollection = self.db[self.collection_name]

    def _get_id(self, id: str) -> ObjectId:
        """
        This method is used to convert a string id to an ObjectId.
        Raises an exception if the id is invalid.
        """

        object_id = ObjectId(id)
        return object_id

    async def _get_documents_by_filter(
        self, filter: dict, limit: int = 100, order_by: str | None = None
    ) -> list[dict]:
        """
        This method is used to get documents by filter.
        Optionally accepts a limit, defaults to 100.
        """

        result = self.collection.find(filter, limit=limit).sort(
            order_by or self.order_by, self.order
        )
        return await result.to_list(length=limit)

    async def create_document(self, document: dict) -> ObjectId:
        """
        Create a new document in the database and return inserted_id.
        """

        result: InsertOneResult = await self.collection.insert_one(document)
        return result.inserted_id

    async def get_document_by_id(self, document_id: str) -> dict | None:
        """
        Find a document by id and return it.
        """

        result = await self.collection.find_one(
            {"_id": self._get_id(document_id)}
        )
        return result

    async def get_documents_by_field(
        self,
        field: str,
        value: str,
        limit: int = 100,
        order: int = -1,
        order_by: str | None = None,
    ) -> list[dict]:
        """
        Find documents by field and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = self.collection.find({field: value}, limit=limit).sort(
            order_by or self.order_by, order or self.order
        )
        return await result.to_list(length=limit)

    async def get_documents_by_fields(
        self, limit: int = 100, order_by: str | None = None, order: int = -1, **fields: dict
    ) -> list[dict]:
        """
        Find documents by fields and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = self.collection.find(fields).sort(
            order_by or self.order_by, order or self.order
        )
        return await result.to_list(length=limit)

    async def get_all_documents(
        self, limit: int = 100, order_by: str | None = None
    ) -> list[dict]:
        """
        Find all documents and return them.
        Optionally accepts a limit, defaults to 100.
        """

        result = self.collection.find({}, limit=limit).sort(
            order_by or self.order_by, self.order
        )
        return await result.to_list(length=limit)

    async def update_document_by_id(
        self, document_id: str, document: dict, return_updated: bool = False
    ) -> dict | None:
        """
        Update a document by id and return it.
        Optionally return the updated document.
        """

        result = await self.collection.find_one_and_update(
            {"_id": self._get_id(document_id)},
            {"$set": document},
            return_document=return_updated,
        )
        return result

    async def delete_document_by_id(self, document_id: str) -> dict | None:
        """
        Delete a document by id and return it.
        """

        result = await self.collection.find_one_and_delete(
            {"_id": self._get_id(document_id)}
        )
        return result
