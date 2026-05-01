from faststream.rabbit import RabbitBroker, RabbitExchange
from src.broker.contracts import PaymentCreatedEvent


class PaymentEventProducer:

    def __init__(self, broker: RabbitBroker, payments_exchange: RabbitExchange):
        self.broker = broker
        self.exchange = payments_exchange
        self.routing_key = "payment.created"

    async def publish(self, payload: PaymentCreatedEvent) -> None:
        await self.broker.publish(
            payload.model_dump(),
            exchange=self.exchange,
            routing_key=self.routing_key,
            persist=True,
        )
