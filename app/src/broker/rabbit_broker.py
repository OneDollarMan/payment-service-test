from faststream.rabbit import RabbitBroker, RabbitQueue
from src.core.config import settings


broker = RabbitBroker(settings.broker_url)

payments_new_queue = RabbitQueue(
    name="payments.new",
    durable=True,
    auto_delete=False,
    exclusive=False,
)