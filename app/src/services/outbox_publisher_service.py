from src.core.config import settings
from src.core.logger import build_logger
from src.broker import PaymentEventProducer, PaymentCreatedEvent
from src.repositories.outbox_repository import OutboxMessageRepository
from sqlalchemy.ext.asyncio import AsyncSession


class OutboxPublisherService:
    def __init__(
            self,
            session: AsyncSession,
            outbox_repository: OutboxMessageRepository,
            payment_event_producer: PaymentEventProducer,
    ):
        self._session = session
        self._outbox_repository = outbox_repository
        self._payment_event_producer = payment_event_producer
        self._logger = build_logger(self.__class__.__name__)

    async def publish_pending_messages(self, limit: int = 100) -> int:
        outbox_messages = await self._outbox_repository.get_pending_batch(self._session, limit=limit)
        published_count = 0

        for outbox_message in outbox_messages:
            try:
                await self._payment_event_producer.publish(
                    payload=PaymentCreatedEvent(
                        message_id=outbox_message.id,
                        aggregate_type=outbox_message.aggregate_type,
                        aggregate_id=outbox_message.aggregate_id,
                        event_name=outbox_message.event_name,
                    )
                )
                await self._outbox_repository.mark_as_published(self._session, outbox_message)
                await self._session.commit()
                self._logger.info(
                    "Published outbox message id=%s event=%s aggregate_id=%s",
                    outbox_message.id,
                    outbox_message.event_name,
                    outbox_message.aggregate_id,
                )
                published_count += 1
            except Exception as exc:
                self._logger.error(f'Error publishing {outbox_message.id=}: {repr(exc)}')
                await self._session.rollback()
                await self._session.refresh(outbox_message)
                await self._outbox_repository.mark_as_failed(self._session, outbox_message, str(exc), settings.outbox_publish_max_attempts)
                await self._session.commit()

        return published_count
