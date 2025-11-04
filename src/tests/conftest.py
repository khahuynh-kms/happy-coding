from beanie import init_beanie
from pymongo import AsyncMongoClient

from ..modules import load_document_models
from ..core.config.config import app_settings
from src.main import app
import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def test_client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport, base_url=app_settings.base_uri
    ) as client:
        yield client


@pytest.fixture
async def test_db():
    client = AsyncMongoClient(app_settings.database.mongodb.test_uri)

    models = load_document_models()
    
    await init_beanie(
        database=client[app_settings.database.mongodb.test_db_name],
        document_models=models
    )

    yield client[app_settings.database.mongodb.test_db_name]

    # await client.drop_database(app_settings.database.mongodb.test_db_name)
    await client.close()
