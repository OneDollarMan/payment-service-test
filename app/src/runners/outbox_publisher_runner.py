import asyncio
from faststream import FastStream
from src.broker import PaymentEventProducer, broker
from src.core.db import async_session_maker
from src.repositories.outbox_repository import OutboxMessageRepository
from src.services.outbox_publisher_service import OutboxPublisherService

publisher_task: asyncio.Task | None = None


async def start_outbox_publisher() -> None:
    global publisher_task
    publisher_task = asyncio.create_task(
        publish_outbox_messages_forever(),
        name="outbox-publisher",
    )


async def stop_outbox_publisher() -> None:
    global publisher_task
    if publisher_task is not None:
        publisher_task.cancel()
        try:
            await publisher_task
        except asyncio.CancelledError:
            pass
        publisher_task = None


app = FastStream(
    broker,
    after_startup=[start_outbox_publisher],
    on_shutdown=[stop_outbox_publisher],
)

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
