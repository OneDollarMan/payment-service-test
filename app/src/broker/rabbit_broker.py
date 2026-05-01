from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue
from src.core.config import settings


def build_broker():
    return RabbitBroker(settings.broker_url)


def build_exchange():
    return RabbitExchange(
    name="payments",
    type=ExchangeType.DIRECT,
    durable=True,
    auto_delete=False,
)


def build_queue():
    return RabbitQueue(
        name="payments.new",
        durable=True,
        auto_delete=False,
        exclusive=False,
        routing_key="payment.created",
    )
