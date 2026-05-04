import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import PaymentStatusEnum
from src.core.exceptions import PaymentNotFoundError
from src.models import Payment
from src.repositories.payment_repository import PaymentRepository


class PaymentStatusService:

    def __init__(
            self,
            session: AsyncSession,
            payment_repository: PaymentRepository,
    ):
        self._session = session
        self._payment_repository = payment_repository

    async def get_payment(self, payment_id: uuid.UUID) -> Payment:
        payment = await self._payment_repository.get_by_id(self._session, payment_id)
        if not payment:
            raise PaymentNotFoundError(f'Payment {payment_id} not found')
        return payment

    async def set_payment_status(
            self,
            payment: Payment,
            status: PaymentStatusEnum,
    ) -> Payment:
        payment = await self._payment_repository.update_loaded_status(self._session, payment, status)
        await self._session.commit()
        return payment
