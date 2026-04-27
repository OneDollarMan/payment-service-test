import asyncio
import sys
from src.runners.outbox_publisher_runner import OutboxPublisherRunner
from src.runners.payment_consumer_runner import PaymentConsumerRunner


async def run_outbox_publisher(poll_interval_seconds: int = 1) -> None:
    await OutboxPublisherRunner().run(poll_interval_seconds=poll_interval_seconds)


async def run_payment_consumer() -> None:
    await PaymentConsumerRunner().run()


if __name__ == "__main__":
    task_name = sys.argv[1] if len(sys.argv) > 1 else "producer"
    if task_name == "producer":
        asyncio.run(run_outbox_publisher())
    elif task_name == "consumer":
        asyncio.run(run_payment_consumer())
    else:
        raise SystemExit(f"Unknown task runner: {task_name}")
