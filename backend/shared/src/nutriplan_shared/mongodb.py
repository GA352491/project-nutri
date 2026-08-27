from pymongo import AsyncMongoClient  # Native async API — PyMongo >= 4.9 (motor deprecated)
from beanie import init_beanie
from typing import List, Type
from .config import get_settings

settings = get_settings()

async def init_mongodb(document_models: List[Type]):
    """Initialize MongoDB and Beanie ODM using PyMongo's native async client.

    PyMongo >= 4.9 ships a built-in AsyncMongoClient that replaces the now-deprecated
    motor library.  Beanie's init_beanie() accepts either client interchangeably.
    """
    client: AsyncMongoClient = AsyncMongoClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=1000,
        connectTimeoutMS=1000
    )
    # The database name is the last path segment of the URL (e.g., /nutriplan)
    db_name = settings.MONGODB_URL.split("/")[-1].split("?")[0]
    await init_beanie(database=client[db_name], document_models=document_models)
