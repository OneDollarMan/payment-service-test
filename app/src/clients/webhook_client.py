from httpx import AsyncClient
from src.models.payment import Payment


class WebhookClient:

    @staticmethod
    async def notify_payment_processed(payment: Payment) -> None:
        payload = {
            "payment_id": str(payment.id),
            "status": payment.status,
            "amount": str(payment.amount),
            "currency": payment.currency,
            "description": payment.description,
            "meta": payment.meta,
            "processed_at": payment.processed_at.isoformat() if payment.processed_at else None,
        }
        async with AsyncClient() as client:
            response = await client.post(payment.webhook_url, json=payload)
            response.raise_for_status()
