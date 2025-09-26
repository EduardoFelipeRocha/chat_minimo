# app/routes/messages.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException, status
from bson import ObjectId
from datetime import datetime, timezone

from app.database import get_db, serialize_doc
from app.models import MessageIn, MessageOut
from app.ws_manager import manager

router = APIRouter()
db = get_db()

@router.get("/rooms/{room}/messages", response_model=dict)
async def get_messages(
    room: str, 
    limit: int = Query(20, ge=1, le=100), 
    before_id: str | None = Query(None)
):
    """
    Retorna o histórico de mensagens de uma sala.
    """
    query = {"room": room}
    if before_id:
        try:
            query["_id"] = {"$lt": ObjectId(before_id)}
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="before_id inválido. O ID deve ser um ObjectId válido."
            )

    cursor = db["messages"].find(query).sort("_id", -1).limit(limit)
    docs = [serialize_doc(d) async for d in cursor]
    docs.reverse()
    next_cursor = docs[0]["_id"] if docs else None
    return {"items": [MessageOut.model_validate(d) for d in docs], "next_cursor": next_cursor}

@router. post("/rooms/{room}/messages", status_code=status.HTTP_201_CREATED, response_model=MessageOut)
async def post_message(room: str, message: MessageIn):
    """
    Salva uma nova mensagem no banco de dados.
    """
    doc = {
        "room": room,
        "username": message.username,
        "content": message.content,
        "created_at": datetime.now(timezone.utc),
    }
    res = await db["messages"].insert_one(doc)
    doc["_id"] = res.inserted_id
    return MessageOut.model_validate(serialize_doc(doc))

@router.websocket("/ws/{room}")
async def ws_room(ws: WebSocket, room: str):
    """
    Gerencia as conexões WebSocket de uma sala.
    """
    await manager.connect(room, ws)
    try:
        # Envia o histórico inicial para o novo cliente
        cursor = db["messages"].find({"room": room}).sort("_id", -1).limit(20)
        items = [serialize_doc(d) async for d in cursor]
        items.reverse()
        await ws.send_json({"type": "history", "items": [MessageOut.model_validate(d).model_dump(by_alias=True) for d in items]})

        while True:
            payload = await ws.receive_json()
            message = MessageIn.model_validate(payload)
            
            doc = {
                "room": room,
                "username": message.username,
                "content": message.content,
                "created_at": datetime.now(timezone.utc),
            }
            res = await db["messages"].insert_one(doc)
            doc["_id"] = res.inserted_id
            
            # Broadcast da nova mensagem para todos os clientes
            await manager.broadcast(
                room, 
                {"type": "message", "item": MessageOut.model_validate(serialize_doc(doc)).model_dump(by_alias=True)}
            )
    except WebSocketDisconnect:
        manager.disconnect(room, ws)