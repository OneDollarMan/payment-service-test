import asyncio
from src.repositories.outbox_repository import OutboxMessageRepository
from src.repositories.payment_repository import PaymentRepository
from src.broker import broker, payments_new_queue
from src.clients.webhook_client import WebhookClient
from src.core.db import async_session_maker
from src.runners.base_broker_runner import BaseBrokerRunner
from src.services.payment_consumer_service import PaymentConsumerService

payment_consumer_service = PaymentConsumerService(
    payment_repository=PaymentRepository(),
    outbox_message_repository=OutboxMessageRepository(),
    webhook_client=WebhookClient()
)


@broker.subscriber(payments_new_queue, no_reply=True)
async def consume_payment_created(payload: dict) -> None:
    async with async_session_maker() as session:
        await payment_consumer_service.handle_payment_created(session, payload)


class PaymentConsumerRunner(BaseBrokerRunner):
    async def _run(self) -> None:
        self._logger.info("Starting payment consumer")
        await broker.start()
        while True:
            await asyncio.sleep(1)
