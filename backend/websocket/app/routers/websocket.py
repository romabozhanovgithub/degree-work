import asyncio
import json
from aio_pika import Queue
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.utils import get_current_user
from app.core.rabbitmq import pika_client

router = APIRouter(prefix="", tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
):
    await websocket.accept()

    # Create a new queue for this client
    queue = await pika_client.declare_user_queue()
    context = {
        "queue": queue,
        "user_id": None,
        "symbol": None,
    }

    async def handle_websocket_messages(context: dict):
        while True:
            data: dict = await websocket.receive_json()
            data_type = data.get("type")
            if data_type is None:
                websocket.send_json({"error": "type is required"})
            elif data_type == "subscribe":
                await pika_client.change_broadcast_queue(
                    context["queue"],
                    symbol=data["target"],
                    unbind_symbol=context["symbol"],
                )
                context["symbol"] = data["target"]
            elif data_type == "auth":
                try:
                    context["user_id"] = await get_current_user(data["token"])
                    context["queue"] = await pika_client.declare_user_queue(
                        queue=context["queue"],
                        symbol=context["symbol"],
                        user_id=context["user_id"],
                    )
                except Exception as e:
                    await websocket.send_json({"error": str(e)})

    async def handle_rabbitmq_messages(context: dict[str, str | Queue | None]):
        async with context["queue"].iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    data = json.loads(message.body)
                    await websocket.send_json(data)

    try:
        tasks = [
            asyncio.create_task(handle_websocket_messages(context)),
            asyncio.create_task(handle_rabbitmq_messages(context)),
        ]
        await asyncio.gather(*tasks)
    except (WebSocketDisconnect, asyncio.CancelledError):
        print("Closing websocket connection...")
        for task in tasks:
            task.cancel()
        await pika_client.close_queue(
            context["queue"], context["symbol"], context["user_id"]
        )
