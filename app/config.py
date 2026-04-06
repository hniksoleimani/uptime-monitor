from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "Uptime Monitor"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://uptime:uptime@localhost:5432/uptime_monitor"

    # Scheduler
    default_check_interval: int = 60  # seconds

    # Telegram alerts
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
