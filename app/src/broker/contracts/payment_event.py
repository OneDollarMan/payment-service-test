import uuid
from pydantic import BaseModel, ConfigDict
from src.core.types import AggType, EventNameType


class PaymentCreatedEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    aggregate_type: AggType
    aggregate_id: uuid.UUID
    event_name: EventNameType
