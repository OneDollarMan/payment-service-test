import asyncio
import random
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.payment_repository import PaymentRepository
from src.services.payment_status_service import PaymentStatusService
from src.core.config import PaymentStatusEnum
from src.core.exceptions import PaymentNotFoundError
from src.models import Payment
from src.broker.contracts.payment_event import PaymentCreatedEvent
from src.core.logger import build_logger


class PaymentConsumerService(PaymentStatusService):
    def __init__(
            self,
            session: AsyncSession,
            payment_repository: PaymentRepository):
        super().__init__(session, payment_repository)
        self._logger = build_logger(self.__class__.__name__)

    async def handle_payment_created(self, event: PaymentCreatedEvent) -> None:
        payment_id = event.aggregate_id
        payment = await self.process_payment(payment_id)
        await self._notify_payment_processed(payment)
        self._logger.info(
            "Processed payment id=%s status=%s webhook_url=%s",
            payment.id,
            payment.status,
            payment.webhook_url,
        )

    async def _notify_payment_processed(self, payment: Payment) -> None:
        payload = {
            "payment_id": str(payment.id),
            "status": payment.status,
            "amount": str(payment.amount),
            "currency": payment.currency,
            "description": payment.description,
            "meta": payment.meta,
            "processed_at": payment.processed_at.isoformat() if payment.processed_at else None,
        }
        async with AsyncClient() as client:
            response = await client.post(payment.webhook_url, json=payload)
            response.raise_for_status()

    async def process_payment(self, payment_id: uuid.UUID) -> Payment:
        await self.get_payment(payment_id)
        await asyncio.sleep(random.randint(2, 5))
        if random.randint(0, 9) == 0:
            payment = await self.update_payment_status(payment_id, PaymentStatusEnum.FAILED)
            if not payment:
                raise PaymentNotFoundError(f'Payment {payment_id} not found')
            return payment

        payment = await self.update_payment_status(payment_id, PaymentStatusEnum.SUCCEEDED)
        if not payment:
            raise PaymentNotFoundError(f'Payment {payment_id} not found')
        return payment