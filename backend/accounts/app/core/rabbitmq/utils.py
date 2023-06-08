from aio_pika import IncomingMessage

from app.core.rabbitmq import pika_client
from app.repositories import BalanceRepository
from app.schemas import BalanceUpdateSchema, BalanceResponseSchema


async def consume_income_message(message: IncomingMessage, **kwargs) -> None:
    balance_repository: BalanceRepository = kwargs["balance_repository"]
    order = BalanceUpdateSchema.parse_raw(message.body)
    balance = await balance_repository.get_user_balance_by_currency(
        order.user_id, order.currency
    )
    balance.amount += order.amount
    new_balance = await balance_repository.update_balance(balance)
    await pika_client.send_message_to_websocket_queue(
        {
            "type": "update",
            "target": "balance",
            "data": BalanceResponseSchema.from_orm(new_balance).dict(),
        }
    )
