import uuid
from pydantic import BaseModel
from src.core.types import AggType, EventNameType


class PaymentCreatedEvent(BaseModel):
    message_id: uuid.UUID
    aggregate_type: AggType
    aggregate_id: uuid.UUID
    event_name: EventNameType
