from __future__ import annotations
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.types import AggType, EventNameType
from src.services.commands import PaymentCreateCommand
from src.services.payment_status_service import PaymentStatusService
from src.repositories.outbox_repository import OutboxMessageRepository
from src.core.exceptions import IdempotencyConflictError
from src.models.payment import Payment
from src.repositories.payment_repository import PaymentRepository


class PaymentService(PaymentStatusService):
    def __init__(
            self,
            session: AsyncSession,
            payment_repository: PaymentRepository,
            outbox_repository: OutboxMessageRepository
    ):
        super().__init__(session, payment_repository)
        self._outbox_repository = outbox_repository
        self.outbox_aggregate_type: AggType = 'payment'
        self.outbox_event_payment_created: EventNameType = 'payment.created'

    async def create_payment(self, idempotency_key: str, command: PaymentCreateCommand) -> Payment:
        existing_payment = await self._ensure_idempotent_request(idempotency_key, command)
        if existing_payment:
            return existing_payment

        payment = await self._payment_repository.create(
            session=self._session,
            idempotency_key=idempotency_key,
            amount=command.amount,
            currency=command.currency,
            description=command.description,
            meta=command.meta,
            webhook_url=str(command.webhook_url),
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
            existing_payment = await self._ensure_idempotent_request(idempotency_key, command)
            if existing_payment:
                return existing_payment
            raise

    async def _ensure_idempotent_request(
            self,
            idempotency_key: str,
            command: PaymentCreateCommand,
    ) -> Payment | None:
        payment = await self._payment_repository.get_by_idempotency_key(self._session, idempotency_key)
        if payment and not self._payment_matches_request(payment, command):
            raise IdempotencyConflictError(
                "Idempotency-Key is already used for another payment payload"
            )
        return payment

    @staticmethod
    def _payment_matches_request(payment: Payment, command: PaymentCreateCommand) -> bool:
        return (
            Decimal(payment.amount) == command.amount
            and payment.currency == command.currency
            and payment.description == command.description
            and payment.meta == command.meta
            and payment.webhook_url == str(command.webhook_url)
        )
