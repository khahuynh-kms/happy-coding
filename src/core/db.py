from ..modules import load_document_models
from .config.config import app_settings
from pymongo import AsyncMongoClient
from beanie import init_beanie


mongo_config = app_settings.database.mongodb

client = AsyncMongoClient(
    mongo_config.uri
)
db = client[mongo_config.db_name]


async def get_db():
    """
    Dependency for FastAPI
    that initializes Beanie and yields the database connection.
    """

    await init_beanie(
        database=db,
        document_models=load_document_models(),
    )
