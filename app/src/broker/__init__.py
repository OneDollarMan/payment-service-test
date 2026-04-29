from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue
from src.broker.contracts.payment_event import PaymentCreatedEvent
from src.core.config import settings

broker = RabbitBroker(settings.broker_url)

payments_new_queue = RabbitQueue(
    name="payments.new",
    durable=True,
    auto_delete=False,
    exclusive=False,
)


class PaymentEventProducer:
    queue = payments_new_queue

    async def publish(self, payload: PaymentCreatedEvent) -> None:
        await broker.publish(payload.model_dump(), queue=self.queue, persist=True)


__all__ = ["FastStream", "broker", "payments_new_queue", "PaymentCreatedEvent", "PaymentEventProducer"]
