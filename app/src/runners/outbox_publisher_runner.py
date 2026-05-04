import asyncio
from faststream import FastStream
from src.broker import PaymentEventProducer, build_broker, build_exchange
from src.core.db import async_session_maker
from src.core.logger import build_logger
from src.repositories.outbox_repository import OutboxMessageRepository
from src.services.outbox_publisher_service import OutboxPublisherService


def build_runner():
    broker = build_broker()
    exchange = build_exchange()
    logger = build_logger("OutboxPublisherRunner")
    payment_event_producer = PaymentEventProducer(broker, exchange)
    outbox_repository = OutboxMessageRepository()
    app = FastStream(broker)

    @app.after_startup
    async def publish_outbox_messages_forever(poll_interval_seconds: int = 1) -> None:
        while True:
            try:
                async with async_session_maker() as session:
                    service = OutboxPublisherService(
                        session=session,
                        outbox_repository=outbox_repository,
                        payment_event_producer=payment_event_producer,
                    )
                    await service.publish_pending_messages()
            except Exception:
                logger.exception("Outbox publisher loop iteration failed")
            finally:
                await asyncio.sleep(poll_interval_seconds)
    return app


runner = build_runner()
