import json
import aio_pika

from app.core import settings


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
        self.websocket_queue = await self.channel.declare_queue(
            self.websocket_queue_name, durable=True
        )

    async def close_connection(self) -> None:
        await self.connection.close()

    def create_queue_name(self, symbol: str) -> str:
        return f"{self.websocket_queue_name}_{symbol}"

    def create_message(self, message: str | dict | list) -> aio_pika.Message:
        body = (
            json.dumps(message).encode()
            if isinstance(message, (dict, list))
            else message.encode()
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

    async def send_message_to_accounts_queue(self, message: str) -> None:
        await self.send_message(message, routing_key=self.accounts_queue_name)

    async def send_message_to_websocket_queue(
        self,
        message: str,
        user_id: str | None = None,
        symbol: str | None = None,
    ) -> None:
        if user_id and symbol:
            raise ValueError(
                "user_id and symbol cannot be set at the same time"
            )
        elif not user_id and not symbol:
            raise ValueError("user_id or symbol must be set")
        elif user_id:
            routing_key = user_id
        else:
            routing_key = self.create_queue_name(symbol)

        await self.send_message(message, routing_key=routing_key)


pika_client = PikaClient()
