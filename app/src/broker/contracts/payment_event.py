import uuid
from typing import Literal
from pydantic import BaseModel, ConfigDict


class PaymentCreatedEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    aggregate_type: Literal["payment"]
    aggregate_id: uuid.UUID
    event_name: Literal["payment.created"]
