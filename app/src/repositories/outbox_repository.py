import uuid
from datetime import datetime, timezone
from sqlalchemy import select
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

    async def get_pending_batch(self, session: AsyncSession, limit: int = 100) -> list[OutboxMessage]:
        stmt = (
            select(OutboxMessage)
            .where(OutboxMessage.status == "PENDING")
            .order_by(OutboxMessage.created_at)
            .limit(limit)
        )
        result = await session.scalars(stmt)
        return list(result)

    async def mark_as_published(self, session: AsyncSession, outbox_message: OutboxMessage) -> OutboxMessage:
        outbox_message.status = "PUBLISHED"
        outbox_message.processed_at = datetime.now(timezone.utc)
        outbox_message.error_message = None
        await session.flush()
        await session.refresh(outbox_message)
        return outbox_message

    async def mark_as_failed(
            self,
            session: AsyncSession,
            outbox_message: OutboxMessage,
            error_message: str,
    ) -> OutboxMessage:
        outbox_message.attempts += 1
        outbox_message.error_message = error_message
        await session.flush()
        await session.refresh(outbox_message)
        return outbox_message
