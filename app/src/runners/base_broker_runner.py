import asyncio
from abc import ABC, abstractmethod
from src.broker import broker
from src.core.logger import build_logger


class BaseBrokerRunner(ABC):
    def __init__(self):
        self._logger = build_logger(self.__class__.__name__)

    async def run(self, *args, **kwargs) -> None:
        await self._connect_broker_with_retry()
        try:
            await self._run(*args, **kwargs)
        finally:
            await broker.close()

    async def _connect_broker_with_retry(
            self,
            initial_delay_seconds: int = 1,
            max_delay_seconds: int = 30,
    ) -> None:
        retry_delay = initial_delay_seconds
        while True:
            try:
                await broker.connect()
                self._logger.info("Connected to RabbitMQ broker")
                return
            except Exception as exc:
                self._logger.warning(
                    "RabbitMQ broker is unavailable, retry in %s seconds: %s",
                    retry_delay,
                    exc,
                )
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_delay_seconds)

    @abstractmethod
    async def _run(self, *args, **kwargs) -> None:
        raise NotImplementedError
