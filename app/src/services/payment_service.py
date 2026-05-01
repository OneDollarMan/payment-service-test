from __future__ import annotations
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.payment_status_service import PaymentStatusService
from src.repositories.outbox_repository import OutboxMessageRepository
from src.core.exceptions import IdempotencyConflictError
from src.models.payment import Payment
from src.repositories.payment_repository import PaymentRepository
from src.web.schemas.payment import PaymentCreateRequest


class PaymentService(PaymentStatusService):
    def __init__(
            self,
            session: AsyncSession,
            payment_repository: PaymentRepository,
            outbox_repository: OutboxMessageRepository
    ):
        super().__init__(session, payment_repository)
        self._outbox_repository = outbox_repository
        self.outbox_aggregate_type = 'payment'
        self.outbox_event_payment_created = 'payment.created'

    async def create_payment(self, idempotency_key: str, schema: PaymentCreateRequest) -> Payment:
        existing_payment = await self._ensure_idempotent_request(idempotency_key, schema)
        if existing_payment:
            return existing_payment

        payment = await self._payment_repository.create(
            session=self._session,
            idempotency_key=idempotency_key,
            amount=schema.amount,
            currency=schema.currency,
            description=schema.description,
            meta=schema.meta,
            webhook_url=str(schema.webhook_url),
        )
        try:
            await self._outbox_repository.create(
                session=self._session,
                aggregate_type=self.outbox_aggregate_type,
                aggregate_id=payment.id,
                event_name=self.outbox_event_payment_created
            )
            await self._session.commit()
            return payment
        except IntegrityError:
            await self._session.rollback()
            existing_payment = await self._ensure_idempotent_request(idempotency_key, schema)
            if existing_payment:
                return existing_payment
            raise

    async def _ensure_idempotent_request(
            self,
            idempotency_key: str,
            schema: PaymentCreateRequest,
    ) -> Payment | None:
        payment = await self._payment_repository.get_by_idempotency_key(self._session, idempotency_key)
        if payment and not self._payment_matches_request(payment, schema):
            raise IdempotencyConflictError(
                "Idempotency-Key is already used for another payment payload"
            )
        return payment

    @staticmethod
    def _payment_matches_request(payment: Payment, schema: PaymentCreateRequest) -> bool:
        return (
            Decimal(payment.amount) == schema.amount
            and payment.currency == schema.currency
            and payment.description == schema.description
            and payment.meta == schema.meta
            and payment.webhook_url == str(schema.webhook_url)
        )
