# app/models.py

from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, Annotated
from datetime import datetime

# Valida se o ID é um ObjectId válido do MongoDB
PyObjectId = Annotated[str, BeforeValidator(str)]

class MessageIn(BaseModel):
    """
    Modelo Pydantic para validação de mensagens recebidas.
    """
    username: str = Field(..., max_length=50)
    content: str = Field(..., max_length=1000, min_length=1)

class MessageOut(BaseModel):
    """
    Modelo Pydantic para serialização de mensagens enviadas.
    """
    id: PyObjectId = Field(..., alias="_id")
    room: str
    username: str
    content: str
    created_at: datetime

    class Config:
        populate_by_name = True