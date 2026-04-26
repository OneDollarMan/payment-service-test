import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal, Annotated
from pydantic import BaseModel, StringConstraints, HttpUrl


class PaymentCreateRequest(BaseModel):
    amount: Decimal
    currency: Literal["RUB", "EUR", "USD"]
    description: Annotated[str, StringConstraints(max_length=255)]
    meta: dict
    webhook_url: HttpUrl


class PaymentCreateResponse(BaseModel):
    id: uuid.UUID
    status: str
    created_at: datetime


class PaymentReadSchema(BaseModel):
    id: uuid.UUID
    amount: Decimal
    currency: Literal["RUB", "EUR", "USD"]
    description: str
    meta: dict
    status: str
    idempotency_key: str
    webhook_url: HttpUrl
    created_at: datetime
    processed_at: datetime | None