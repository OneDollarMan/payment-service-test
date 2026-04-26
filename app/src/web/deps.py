from typing import AsyncGenerator, Annotated
from fastapi import Header, Depends, Security, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from src.repositories.payment_repository import PaymentRepository
from src.services.payment_service import PaymentService
from src.core.config import Settings
from src.core.db import async_session_maker


def get_settings() -> Settings:
    return Settings()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


def get_idempotency_key(idempotency_key: Annotated[str, Header()]) -> str:
    return idempotency_key


api_key_header = APIKeyHeader(name="X-API-Key")
def get_auth(
        api_key: str = Security(api_key_header),
        settings: Settings = Depends(get_settings)
) -> str:
    if api_key != settings.auth_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    return api_key


def get_payment_repository():
    return PaymentRepository()


def get_payment_service(
        session: AsyncSession = Depends(get_async_session),
        payment_repository: PaymentRepository = Depends(get_payment_repository),
        api_key: str = Security(get_auth)
) -> PaymentService:
    return PaymentService(session, payment_repository)