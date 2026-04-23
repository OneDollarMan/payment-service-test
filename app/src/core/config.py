from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", env_file=".env.dev")

    postgres_user: str = Field(default='postgres', validation_alias="POSTGRES_USER")
    postgres_password: str = Field(default='postgres', validation_alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(default='logistic-model-db', validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(default='5432', validation_alias="PGPORT")
    postgres_db: str = Field(default='rossko_logistic', validation_alias="POSTGRES_DB")
    celery_broker_url: str | None = Field(default=None, validation_alias="CELERY_BROKER_URL")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

settings = Settings()
