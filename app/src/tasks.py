from celery import Celery
from src.core.config import settings

celery_app = Celery('payment-service-celery', broker=settings.celery_broker_url)
