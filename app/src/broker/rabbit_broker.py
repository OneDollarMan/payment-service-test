from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue
from src.core.config import settings


broker = RabbitBroker(settings.broker_url)

payments_exchange = RabbitExchange(
    name="payments",
    type=ExchangeType.DIRECT,
    durable=True,
    auto_delete=False,
)

payments_new_queue = RabbitQueue(
    name="payments.new",
    durable=True,
    auto_delete=False,
    exclusive=False,
    routing_key="payment.created",
)
