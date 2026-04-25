import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.error import PaymentNotFoundError
from src.models.payment import Payment
from src.repositories.payment_repository import PaymentRepository


class PaymentService:
    def __init__(
            self,
            session: AsyncSession,
            payment_repository: PaymentRepository,
            idempotency_key: str
    ):
        self._session = session
        self._payment_repository = payment_repository
        self._idempotency_key = idempotency_key


    async def create_payment(self):
        ...


    async def get_payment(self, payment_id: uuid.UUID) -> Payment:
        payment = await self._payment_repository.get_by_id(self._session, payment_id)
        if not payment:
            raise PaymentNotFoundError(f'Payment {payment_id} not found')
        return payment