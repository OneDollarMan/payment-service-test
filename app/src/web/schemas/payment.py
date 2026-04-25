import uuid
from decimal import Decimal
from typing import Literal, Annotated
from pydantic import BaseModel, StringConstraints
from pydantic_core.core_schema import UrlSchema


class PaymentCreateSchema(BaseModel):
    amount: Decimal
    currency: Literal["RUB", "EUR", "USD"]
    description: Annotated[str, StringConstraints(max_length=255)]
    meta: dict
    webhook_url: UrlSchema


class PaymentReadSchema(BaseModel):
    id: uuid.UUID
    amount: Decimal
    currency: Literal["RUB", "EUR", "USD"]
    description: str
    meta: dict
    webhook_url: UrlSchema
