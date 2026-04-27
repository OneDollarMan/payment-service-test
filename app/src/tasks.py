import asyncio
from src.runnsers.outbox_publisher_runner import OutboxPublisherRunner


async def run_outbox_publisher(poll_interval_seconds: int = 1) -> None:
    await OutboxPublisherRunner().run(poll_interval_seconds=poll_interval_seconds)


if __name__ == "__main__":
    asyncio.run(run_outbox_publisher())
