import asyncio
from src.brokers.faststream_broker import broker
from src.brokers.payment_producer import PaymentEventProducer
from src.core.db import async_session_maker
from src.core.logger import build_logger
from src.repositories.outbox_repository import OutboxMessageRepository
from src.services.outbox_publisher_service import OutboxPublisherService


class OutboxPublisherRunner:
    def __init__(self):
        self._logger = build_logger(self.__class__.__name__)

    async def run(self, poll_interval_seconds: int = 1) -> None:
        await self._connect_broker_with_retry()
        try:
            while True:
                async with async_session_maker() as session:
                    service = OutboxPublisherService(
                        session=session,
                        outbox_repository=OutboxMessageRepository(),
                        payment_event_producer=PaymentEventProducer(),
                    )
                    await service.publish_pending_messages()

                await asyncio.sleep(poll_interval_seconds)
        finally:
            await broker.close()

    async def _connect_broker_with_retry(
            self,
            initial_delay_seconds: int = 1,
            max_delay_seconds: int = 30,
    ) -> None:
        retry_delay = initial_delay_seconds
        while True:
            try:
                await broker.connect()
                self._logger.info("Connected to RabbitMQ broker")
                return
            except Exception as exc:
                self._logger.warning(
                    "RabbitMQ broker is unavailable, retry in %s seconds: %s",
                    retry_delay,
                    exc,
                )
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_delay_seconds)
