import aio_pika
from aio_pika import Queue, ExchangeType

from app.core import settings


class PikaClient:
    def __init__(self) -> None:
        self.exchange_name = settings.RABBITMQ_EXCHANGE_NAME
        self.websocket_queue_name = settings.RABBITMQ_WEBSOCKET_QUEUE_NAME

    async def connect(self) -> None:
        self.connection = await aio_pika.connect_robust(
            settings.RABBITMQ_URL,
        )
        self.channel = await self.connection.channel()
        # await self.channel.set_qos(prefetch_count=1)

        self.exchange = await self.channel.declare_exchange(
            self.exchange_name,
            ExchangeType.DIRECT,
            durable=True,
        )

    def create_queue_name(self, symbol: str) -> str:
        return f"{self.websocket_queue_name}_{symbol}"

    async def declare_user_queue(
        self,
        symbol: str | None = None,
        user_id: str | None = None,
        queue: Queue | None = None,
    ) -> Queue:
        if queue is None:
            queue = await self.channel.declare_queue(user_id, auto_delete=True)

        if user_id is not None:
            await queue.bind(
                self.exchange,
                routing_key=user_id,
            )
        if symbol is not None:
            broadcast_queue_name = self.create_queue_name(symbol)
            await queue.bind(
                self.exchange,
                routing_key=broadcast_queue_name,
            )
        return queue

    async def close_queue(
        self,
        queue: Queue,
        symbol: str | None = None,
        user_id: str | None = None,
    ) -> None:
        broadcast_queue_name = self.create_queue_name(symbol)
        if user_id is not None:
            await queue.unbind(
                self.exchange,
                routing_key=user_id,
            )
        if symbol is not None:
            await queue.unbind(
                self.exchange,
                routing_key=broadcast_queue_name,
            )
        await queue.delete(if_unused=False)

    async def change_broadcast_queue(
        self, queue: Queue, symbol: str, unbind_symbol: str | None = None
    ) -> Queue:
        broadcast_queue_name = self.create_queue_name(symbol)
        unbind_broadcast_queue_name = self.create_queue_name(unbind_symbol)
        if unbind_symbol is not None:
            await queue.unbind(
                self.exchange,
                routing_key=unbind_broadcast_queue_name,
            )
        await queue.bind(
            self.exchange,
            routing_key=broadcast_queue_name,
        )
        return queue


pika_client = PikaClient()
