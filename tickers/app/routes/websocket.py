from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.routes.manager import manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    while True:
        try:
            data = await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            break
