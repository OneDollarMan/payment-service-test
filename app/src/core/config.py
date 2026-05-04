from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", env_file=".env.dev")

    postgres_user: str = Field(default='postgres', validation_alias="POSTGRES_USER")
    postgres_password: str = Field(default='postgres', validation_alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(default='payment-service-db', validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(default='5432', validation_alias="PGPORT")
    postgres_db: str = Field(default='payment-service', validation_alias="POSTGRES_DB")
    broker_url: str = Field(default='amqp://rabbit:rabbit@payment-service-rabbitmq:5672/', validation_alias="BROKER_URL")
    auth_api_key: str = Field(default='key', validation_alias="AUTH_API_KEY")

    outbox_publish_max_attempts: int = Field(default=5, validation_alias="OUTBOX_PUBLISH_MAX_ATTEMPTS")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

settings = Settings()


class PaymentStatusEnum(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class OutboxMessageStatusEnum(str, Enum):
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"