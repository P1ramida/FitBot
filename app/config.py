from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import cached_property
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

class DatabaseConfig(BaseConfig):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

class BotConfig(BaseConfig):
    BOT_TOKEN: str
    AI_TOKEN: str


class Config(BaseSettings):
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    bot: BotConfig = Field(default_factory=BotConfig)

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db.DB_USER}:{self.db.DB_PASS}"
            f"@{self.db.DB_HOST}:{self.db.DB_PORT}/{self.db.DB_NAME}"
        )

    @classmethod
    def load(cls) -> "Config":
        return cls()

CONFIG = Config.load()