import asyncio
from faststream import FastStream
from src.broker import PaymentEventProducer, broker
from src.core.db import async_session_maker
from src.repositories.outbox_repository import OutboxMessageRepository
from src.services.outbox_publisher_service import OutboxPublisherService

app = FastStream(broker)


@app.after_startup
async def publish_outbox_messages_forever(poll_interval_seconds: int = 1) -> None:
    while True:
        async with async_session_maker() as session:
            service = OutboxPublisherService(
                session=session,
                outbox_repository=OutboxMessageRepository(),
                payment_event_producer=PaymentEventProducer(),
            )
            await service.publish_pending_messages()

        await asyncio.sleep(poll_interval_seconds)
