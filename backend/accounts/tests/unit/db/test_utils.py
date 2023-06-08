import pytest
from unittest.mock import patch

from app.db import init_models


@pytest.mark.asyncio
@patch("app.db.base.Base.metadata.drop_all")
@patch("app.db.base.Base.metadata.create_all")
async def test_init_models(mock_drop_all, mock_create_all):
    await init_models()
    mock_drop_all.assert_called_once()
    mock_create_all.assert_called_once()
