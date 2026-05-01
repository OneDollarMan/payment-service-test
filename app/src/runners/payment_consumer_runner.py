from faststream import FastStream
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.payment_service import PaymentService
from src.repositories.outbox_repository import OutboxMessageRepository
from src.repositories.payment_repository import PaymentRepository
from src.broker import broker, payments_exchange, payments_new_queue, PaymentCreatedEvent
from src.core.db import async_session_maker
from src.services.payment_consumer_service import PaymentConsumerService

app = FastStream(broker)


def build_payment_consumer_service(session: AsyncSession) -> PaymentConsumerService:
    payment_repository = PaymentRepository()
    outbox_repository = OutboxMessageRepository()

    payment_service = PaymentService(
        session=session,
        payment_repository=payment_repository,
        outbox_repository=outbox_repository,
    )
    return PaymentConsumerService(payment_service=payment_service)


@broker.subscriber(payments_new_queue, payments_exchange, no_reply=True)
async def consume_payment_created(event: PaymentCreatedEvent) -> None:
    async with async_session_maker() as session:
        payment_consumer_service = build_payment_consumer_service(session)
        await payment_consumer_service.handle_payment_created(event)
