from src.broker.contracts import PaymentCreatedEvent
from src.broker.rabbit_broker import broker, payments_exchange


class PaymentEventProducer:
    exchange = payments_exchange
    routing_key = "payment.created"

    async def publish(self, payload: PaymentCreatedEvent) -> None:
        await broker.publish(
            payload.model_dump(),
            exchange=self.exchange,
            routing_key=self.routing_key,
            persist=True,
        )
