from src.brokers.faststream_broker import broker


class PaymentEventProducer:
    queue_name = "payments.new"

    async def publish(self, payload: dict) -> None:
        await broker.publish(payload, queue=self.queue_name)
