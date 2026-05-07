from os import getenv
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: SecretStr
    db_echo: bool

    broker_host: str
    broker_port: int
    broker_user: str
    broker_password: SecretStr

    max_code_length: int
    max_attempts: int
    penalty_cap: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password.get_secret_value()}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def broker_url(self) -> str:
        return (
            f"amqp://{self.broker_user}:{self.broker_password.get_secret_value()}"
            f"@{self.broker_host}:{self.broker_port}//"
        )


def get_settings() -> Settings:
    env = getenv("APP_ENV", "dev")
    env_file_map = {
        "dev": ".env",
        "test": ".env.test",
    }
    return Settings(_env_file=env_file_map.get(env, ".env"))  # type: ignore


@lru_cache
def get_settings_cached() -> Settings:
    return get_settings()
