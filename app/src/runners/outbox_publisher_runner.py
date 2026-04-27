import asyncio
from src.brokers.payment_producer import PaymentEventProducer
from src.core.db import async_session_maker
from src.repositories.outbox_repository import OutboxMessageRepository
from src.runners.base_broker_runner import BaseBrokerRunner
from src.services.outbox_publisher_service import OutboxPublisherService


class OutboxPublisherRunner(BaseBrokerRunner):
    async def _run(self, poll_interval_seconds: int = 1) -> None:
        while True:
            async with async_session_maker() as session:
                service = OutboxPublisherService(
                    session=session,
                    outbox_repository=OutboxMessageRepository(),
                    payment_event_producer=PaymentEventProducer(),
                )
                await service.publish_pending_messages()

            await asyncio.sleep(poll_interval_seconds)
