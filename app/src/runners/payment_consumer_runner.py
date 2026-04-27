from src.brokers.faststream_broker import broker
from src.clients.webhook_client import WebhookClient
from src.core.logger import build_logger
from src.runners.base_broker_runner import BaseBrokerRunner
from src.services.payment_consumer_service import PaymentConsumerService

logger = build_logger("payment-consumer")
payment_consumer_service = PaymentConsumerService(webhook_client=WebhookClient())


@broker.subscriber("payments.new")
async def consume_payment_created(payload: dict) -> None:
    await payment_consumer_service.handle_payment_created(payload)


class PaymentConsumerRunner(BaseBrokerRunner):
    async def _run(self) -> None:
        self._logger.info("Starting payment consumer")
        await broker.start()
