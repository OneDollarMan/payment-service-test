from faststream import FastStream
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.payment_repository import PaymentRepository
from src.broker import build_broker, build_exchange, build_queue, PaymentCreatedEvent
from src.core.db import async_session_maker
from src.services.payment_consumer_service import PaymentConsumerService


def build_payment_consumer_service(session: AsyncSession) -> PaymentConsumerService:
    return PaymentConsumerService(session, PaymentRepository())


def build_runner():
    broker = build_broker()
    exchange = build_exchange()
    queue = build_queue()
    app = FastStream(broker)

    @broker.subscriber(queue, exchange, no_reply=True)
    async def consume_payment_created(event: PaymentCreatedEvent) -> None:
        async with async_session_maker() as session:
            payment_consumer_service = build_payment_consumer_service(session)
            await payment_consumer_service.handle_payment_created(event)
    return app


runner = build_runner()