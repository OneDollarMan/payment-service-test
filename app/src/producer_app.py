import asyncio
from src.broker import FastStream, broker
from src.runners.outbox_publisher_runner import OutboxPublisherRunner

publisher_task: asyncio.Task | None = None


async def start_outbox_publisher() -> None:
    global publisher_task
    publisher_task = asyncio.create_task(
        OutboxPublisherRunner()._run(),
        name="outbox-publisher",
    )


async def stop_outbox_publisher() -> None:
    global publisher_task
    if publisher_task is not None:
        publisher_task.cancel()
        try:
            await publisher_task
        except asyncio.CancelledError:
            pass
        publisher_task = None


app = FastStream(
    broker,
    after_startup=[start_outbox_publisher],
    on_shutdown=[stop_outbox_publisher],
)
