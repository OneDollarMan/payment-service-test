from datetime import datetime
import uuid
from decimal import Decimal
from sqlalchemy import UUID, Double, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, Mapped
from src.core.db import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount: Mapped[Decimal] = mapped_column(Double)
    currency: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    meta: Mapped[dict] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String)
    idempotency_key: Mapped[str] = mapped_column(String)
    webhook_url: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
