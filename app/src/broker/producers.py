from src.broker.contracts import PaymentCreatedEvent
from src.broker.rabbit_broker import broker, payments_new_queue


class PaymentEventProducer:
    queue = payments_new_queue

    async def publish(self, payload: PaymentCreatedEvent) -> None:
        await broker.publish(payload.model_dump(), queue=self.queue, persist=True)