from __future__ import annotations

import asyncio
import random
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.outbox_repository import OutboxMessageRepository
from src.core.config import PaymentStatusEnum
from src.core.exceptions import IdempotencyConflictError, PaymentNotFoundError
from src.models.payment import Payment
from src.repositories.payment_repository import PaymentRepository

if TYPE_CHECKING:
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
                event_name=self.outbox_event_payment_created,
                payload=self._build_payment_created_payload(payment),
            )
            await self._session.commit()
            return payment
        except IntegrityError:
            await self._session.rollback()
            existing_payment = await self._ensure_idempotent_request(idempotency_key, schema)
            if existing_payment:
                return existing_payment
            raise

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

    async def process_payment(self, payment_id: uuid.UUID) -> Payment:
        await self.get_payment(payment_id)
        await asyncio.sleep(random.randint(2, 5))
        if random.randint(0, 9) == 0:
            payment = await self._payment_repository.update_status(self._session, payment_id, PaymentStatusEnum.FAILED)
            await self._session.commit()
            if not payment:
                raise PaymentNotFoundError(f'Payment {payment_id} not found')
            return payment

        payment = await self._payment_repository.update_status(self._session, payment_id, PaymentStatusEnum.SUCCEEDED)
        await self._session.commit()
        if not payment:
            raise PaymentNotFoundError(f'Payment {payment_id} not found')
        return payment

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

    @staticmethod
    def _build_payment_created_payload(payment: Payment) -> dict:
        return {
            "event_name": "payment.created",
            "payment_id": str(payment.id),
            "amount": str(payment.amount),
            "currency": payment.currency,
            "description": payment.description,
            "meta": payment.meta,
            "status": payment.status,
            "idempotency_key": payment.idempotency_key,
            "webhook_url": payment.webhook_url,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
        }
