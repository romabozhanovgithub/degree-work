from typing import List

from fastapi import WebSocket
from pydantic import parse_obj_as

from app.schemas import TickerResponse


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def accept_data(self, websocket: WebSocket, data: dict):
        if data["type"] == "subscribe":
            if data["message"] not in self.subscriptions:
                self.subscriptions[data["message"]] = [websocket]
            else:
                self.subscriptions[data["message"]].append(websocket)
            await websocket.send_text(f"Subscribed to {data['message']}")
        elif data["type"] == "unsubscribe":
            self.subscriptions[data["message"]].remove(websocket)
            await websocket.send_text(f"Unsubscribed from {data['message']}")


    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_subscription(self, subscription: str, data: dict):
        for connection in self.subscriptions[subscription]:
            await connection.send_json({
                "type": "subscription",
                "message": {
                    "subscription": subscription,
                    "data": data
                }
            })

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_json(TickerResponse(**message).json())


manager = ConnectionManager()
