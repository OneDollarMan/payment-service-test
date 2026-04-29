from src.broker import FastStream, broker
from src.runners import payment_consumer_runner as _payment_consumer_runner  # noqa: F401


app = FastStream(broker)
