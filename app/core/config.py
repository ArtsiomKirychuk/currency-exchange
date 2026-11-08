from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from sqlalchemy import URL


class Settings(BaseSettings):
    debug: bool = False
    db_user: str
    db_password: str
    db_host: str
    db_name: str
    db_port: int

    nbrb_base_url: str

    scheduler_timezone: str = "Europe/Minsk"
    scheduler_hour: int = 0
    scheduler_minute: int = 5

    expire_deal_in_minutes: int = 5
    overdue_deals_expiration_minutes: int = 1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def build_db_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg", 
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
