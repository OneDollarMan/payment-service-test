import asyncio
import random
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.outbox_repository import OutboxMessageRepository
from src.core.config import PaymentStatusEnum
from src.core.exceptions import PaymentNotFoundError
from src.models.payment import Payment
from src.repositories.payment_repository import PaymentRepository
from src.web.schemas.payment import PaymentCreateRequest


class PaymentService:
    def __init__(
            self,
            session: AsyncSession,
            payment_repository: PaymentRepository,
            outbox_repository: OutboxMessageRepository
    ):
        self._session = session
        self._payment_repository = payment_repository
        self._outbox_repository = outbox_repository
        self.outbox_aggregate_type = 'payment'
        self.outbox_event_payment_created = 'payment.created'

    async def create_payment(self, idempotency_key: str, schema: PaymentCreateRequest) -> Payment:
        payment = await self._payment_repository.create(
            session=self._session, idempotency_key=idempotency_key, amount=schema.amount, currency=schema.currency,
            description=schema.description, meta=schema.meta, webhook_url=str(schema.webhook_url)
        )
        await self._outbox_repository.create(
            session=self._session, aggregate_type=self.outbox_aggregate_type,
            aggregate_id=payment.id, event_name=self.outbox_event_payment_created, payload={}
        )
        await self._session.commit()
        return payment

    async def get_payment(self, payment_id: uuid.UUID) -> Payment:
        payment = await self._payment_repository.get_by_id(self._session, payment_id)
        if not payment:
            raise PaymentNotFoundError(f'Payment {payment_id} not found')
        return payment

    async def update_payment_status(self, payment_id: uuid.UUID, status: PaymentStatusEnum) -> Payment:
        payment = await self._payment_repository.update_status(self._session, payment_id, status)
        if not payment:
            raise PaymentNotFoundError(f'Payment {payment_id} not found')
        await self._session.commit()
        return payment

    async def process_payment(self, payment_id: uuid.UUID) -> int:
        await self.get_payment(payment_id)
        await asyncio.sleep(random.randint(2, 5))
        if random.randint(0, 9) == 0:
            raise Exception(f'Payment {payment_id} failed')

        await self._payment_repository.update_status(self._session, payment_id, PaymentStatusEnum.SUCCESS)
        await self._session.commit()
        return 0