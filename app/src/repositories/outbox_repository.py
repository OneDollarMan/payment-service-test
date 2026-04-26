import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import OutboxMessage


class OutboxMessageRepository:

    async def create(
            self, session: AsyncSession, aggregate_type: str, aggregate_id: uuid.UUID, event_name: str, payload: dict
    ) -> OutboxMessage:
        outbox_message = OutboxMessage(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_name=event_name,
            payload=payload
        )
        session.add(outbox_message)
        await session.flush()
        await session.refresh(outbox_message)
        return outbox_message