import uuid
from fastapi import APIRouter, Depends
from starlette import status
from src.services.commands import PaymentCreateCommand
from src.services.payment_service import PaymentService
from src.web.schemas.payment import PaymentCreateRequest, PaymentCreateResponse, PaymentReadSchema
from src.web.deps import get_payment_service, get_idempotency_key

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


@router.post("/", response_model=PaymentCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_payment(
        schema: PaymentCreateRequest,
        idempotency_key: str = Depends(get_idempotency_key),
        service: PaymentService = Depends(get_payment_service)):
    command = PaymentCreateCommand(
        amount=schema.amount,
        currency=schema.currency,
        description=schema.description,
        meta=schema.meta,
        webhook_url=str(schema.webhook_url)
    )
    return await service.create_payment(idempotency_key, command)


@router.get("/{payment_id}", response_model=PaymentReadSchema)
async def get_payment(payment_id: uuid.UUID, service: PaymentService = Depends(get_payment_service)):
    return await service.get_payment(payment_id)
