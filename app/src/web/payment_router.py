import uuid
from fastapi import APIRouter, Depends
from src.services.payment_service import PaymentService
from src.web.schemas.payment import PaymentCreateSchema
from src.web.deps import get_payment_service

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


@router.post("/", )
async def create_payment(schema: PaymentCreateSchema, service: PaymentService = Depends(get_payment_service)):
    return {'status': 'created'}


@router.get("/{payment_id}")
async def get_payment(payment_id: uuid.UUID):
    return {'test': payment_id}