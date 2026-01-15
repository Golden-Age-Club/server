"""
WebSocket Connection Manager for Support Chat
Simple in-memory store for active connections: {ticket_id: [websocket]}
"""
from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # ticket_id -> List[WebSocket]
        self.active_rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, ticket_id: str, websocket: WebSocket):
        await websocket.accept()
        if ticket_id not in self.active_rooms:
            self.active_rooms[ticket_id] = []
        self.active_rooms[ticket_id].append(websocket)

    def disconnect(self, ticket_id: str, websocket: WebSocket):
        if ticket_id in self.active_rooms:
            if websocket in self.active_rooms[ticket_id]:
                self.active_rooms[ticket_id].remove(websocket)
            if not self.active_rooms[ticket_id]:
                del self.active_rooms[ticket_id]

    async def broadcast(self, ticket_id: str, message: dict):
        """Broadcast JSON message to all clients in the room"""
        if ticket_id in self.active_rooms:
            # Iterate over a copy to safe-guard against modification during iteration
            for connection in self.active_rooms[ticket_id][:]:
                try:
                    await connection.send_json(message)
                except:
                    # Connection closed? Remove it
                    self.disconnect(ticket_id, connection)


manager = ConnectionManager()
