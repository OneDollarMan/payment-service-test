import uuid
from src.core.db import async_session_maker
from src.core.logger import build_logger
from src.repositories.outbox_repository import OutboxMessageRepository
from src.repositories.payment_repository import PaymentRepository
from src.services.payment_service import PaymentService
from src.clients.webhook_client import WebhookClient


class PaymentConsumerService:
    def __init__(self, webhook_client: WebhookClient):
        self._webhook_client = webhook_client
        self._logger = build_logger(self.__class__.__name__)

    async def handle_payment_created(self, payload: dict) -> None:
        payment_id = uuid.UUID(payload["payment_id"])

        async with async_session_maker() as session:
            payment_service = PaymentService(
                session=session,
                payment_repository=PaymentRepository(),
                outbox_repository=OutboxMessageRepository(),
            )
            payment = await payment_service.process_payment(payment_id)

        await self._webhook_client.notify_payment_processed(payment)
        self._logger.info(
            "Processed payment id=%s status=%s webhook_url=%s",
            payment.id,
            payment.status,
            payment.webhook_url,
        )
