from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.routes.manager import manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    while True:
        try:
            # accept message with json from websocket and if subscription type
            # add subscription to manager
            data = await websocket.receive_json()
            await manager.accept_data(websocket, data)
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            break
