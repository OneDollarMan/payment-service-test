import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.payment import Payment


class PaymentRepository:

    async def create(self, session: AsyncSession) -> Payment:
        ...

    async def get_by_id(self, session: AsyncSession, payment_id: uuid.UUID) -> Payment | None:
        return await session.get(Payment, payment_id)
