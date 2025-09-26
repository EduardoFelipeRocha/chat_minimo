# app/ws_manager.py

from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect

class WSManager:
    """
    Gerencia as conexões WebSocket por sala (room).
    """
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room: str, ws: WebSocket):
        """Aceita uma nova conexão WebSocket e a adiciona a uma sala."""
        await ws.accept()
        self.rooms.setdefault(room, set()).add(ws)

    def disconnect(self, room: str, ws: WebSocket):
        """Remove uma conexão da sala ao ser desconectada."""
        conns = self.rooms.get(room)
        if conns and ws in conns:
            conns.remove(ws)
            if not conns:
                self.rooms.pop(room, None)

    async def broadcast(self, room: str, payload: dict):
        """
        Envia uma mensagem JSON para todos os clientes conectados em uma sala.

        Lida com clientes que foram desconectados inesperadamente.
        """
        for ws in list(self.rooms.get(room, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(room, ws)

manager = WSManager()