import json
import aio_pika

from app.core import settings
from app.schemas import OrderSchema


class PikaClient:
    def __init__(self) -> None:
        self.exchange_name = settings.RABBITMQ_EXCHANGE_NAME
        self.accounts_queue_name = settings.RABBITMQ_ACCOUNTS_QUEUE_NAME
        self.websocket_queue_name = settings.RABBITMQ_WEBSOCKET_QUEUE_NAME

    async def connect(self) -> None:
        self.connection = await aio_pika.connect_robust(
            settings.RABBITMQ_URL,
        )
        self.channel = await self.connection.channel()
        # await self.channel.set_qos(prefetch_count=1)

        self.exchange = await self.channel.declare_exchange(
            self.exchange_name,
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )

        self.accounts_queue = await self.channel.declare_queue(
            self.accounts_queue_name, durable=True
        )

    def create_message(self, message: str | dict | list) -> aio_pika.Message:
        body = (
            json.dumps(message).encode()
            if isinstance(message, (dict, list))
            else message
        )
        return aio_pika.Message(
            body=body,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

    async def send_message(self, message: str, routing_key: str) -> None:
        message = self.create_message(message)
        await self.exchange.publish(
            message,
            routing_key=routing_key,
        )

    async def _print(self, message: aio_pika.IncomingMessage) -> None:
        order = OrderSchema.parse_raw(message.body)
        print(order)

    async def send_message_to_websocket_queue(
        self, message: str, user_id: str
    ) -> None:
        await self.send_message(message, routing_key=user_id)

    async def consume_accounts_queue(
        self, callback: callable, **kwargs
    ) -> None:
        await self.accounts_queue.bind(
            self.exchange, routing_key=self.accounts_queue_name
        )

        async with self.accounts_queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await callable(message, **kwargs)


pika_client = PikaClient()
