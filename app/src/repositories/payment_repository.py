import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.payment import Payment


class PaymentRepository:

    async def create(
            self,
            session: AsyncSession,
            amount: Decimal,
            currency: str,
            description: str,
            meta: dict,
            idempotency_key: str,
            webhook_url: str,
    ) -> Payment:
        payment = Payment(
            amount=amount,
            currency=currency,
            description=description,
            meta=meta,
            idempotency_key=idempotency_key,
            webhook_url=webhook_url,
        )
        session.add(payment)
        await session.flush()
        await session.refresh(payment)
        return payment

    async def get_by_id(self, session: AsyncSession, payment_id: uuid.UUID) -> Payment | None:
        return await session.get(Payment, payment_id)

    async def update_status(self, session: AsyncSession, payment_id: uuid.UUID, status: str) -> Payment | None:
        payment = await self.get_by_id(session, payment_id)
        if not payment:
            return None

        payment.status = status
        await session.flush()
        await session.refresh(payment)
        return payment
