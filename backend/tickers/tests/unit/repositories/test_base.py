import pytest

from app.repositories import BaseRepository


@pytest.mark.asyncio
async def test_create_document(base_repository: BaseRepository):
    result = await base_repository.create_document({"test": "test"})
    data = await base_repository.get_document_by_id(str(result))
    assert data["test"] == "test"


@pytest.mark.asyncio
async def test_get_document_by_id(base_repository: BaseRepository):
    result = await base_repository.create_document({"test": "test"})
    data = await base_repository.get_document_by_id(result)
    assert data["test"] == "test"


@pytest.mark.asyncio
async def test_get_documents_by_field(base_repository: BaseRepository):
    await base_repository.create_document({"test": "test"})
    await base_repository.create_document({"test": "test"})
    result = await base_repository.get_documents_by_field("test", "test")
    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_documents_by_fields(base_repository: BaseRepository):
    await base_repository.create_document({"test": "test", "test1": "test1"})
    await base_repository.create_document({"test": "test", "test2": "test2"})
    result = await base_repository.get_documents_by_fields(test="test")
    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_all_documents(base_repository: BaseRepository):
    await base_repository.create_document({"test": "test"})
    await base_repository.create_document({"test": "test"})
    result = await base_repository.get_all_documents()
    assert len(result) == 2


@pytest.mark.asyncio
async def test_update_document_by_id(base_repository: BaseRepository):
    result = await base_repository.create_document({"test": "test"})
    data = await base_repository.update_document_by_id(
        result, {"test": "test1"}, return_updated=True
    )
    assert data["test"] == "test1"


@pytest.mark.asyncio
async def test_delete_document_by_id(base_repository: BaseRepository):
    result = await base_repository.create_document({"test": "test"})
    data = await base_repository.delete_document_by_id(result)
    deleted = await base_repository.get_document_by_id(result)
    assert data["test"] == "test"
    assert deleted is None
