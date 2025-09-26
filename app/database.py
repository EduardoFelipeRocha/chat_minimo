# app/database.py

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timezone
from app.config import settings

_client: Optional[AsyncIOMotorClient] = None

def get_db() -> AsyncIOMotorDatabase:
    """
    Retorna a instância do banco de dados MongoDB.

    Cria uma nova conexão se ela ainda não existir.
    """
    global _client
    if _client is None:
        if not settings.MONGO_URL:
            raise RuntimeError("A variável MONGO_URL deve ser definida no arquivo .env.")
        _client = AsyncIOMotorClient(settings.MONGO_URL)
    return _client[settings.MONGO_DB]

def serialize_doc(doc: dict) -> dict:
    """
    Serializa um documento do MongoDB para um formato JSON.

    Converte o ObjectId para string e o datetime para o formato ISO 8601.
    """
    d = dict(doc)
    if "_id" in d and isinstance(d["_id"], ObjectId):
        d["_id"] = str(d["_id"])
    if "created_at" in d and isinstance(d["created_at"], datetime):
        d["created_at"] = d["created_at"].isoformat()
    return d