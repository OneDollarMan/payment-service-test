from dataclasses import dataclass
from decimal import Decimal


@dataclass
class PaymentCreateCommand:
    amount: Decimal
    currency: str
    description: str
    meta: dict
    webhook_url: str