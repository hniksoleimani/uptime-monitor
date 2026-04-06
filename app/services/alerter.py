import logging
import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Telegram Bot API URL
_BASE_URL = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"


async def send_alert(monitor_name: str, is_up: bool, detail: str = ""):
    """Send a Telegram notification. Silently skips if bot token is not configured."""
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.debug("Telegram not configured, skipping alert")
        return

    emoji = "\u2705" if is_up else "\U0001f534"
    status = "UP" if is_up else "DOWN"
    text = f"{emoji} *{monitor_name}* is {status}"
    if detail:
        text += f"\n`{detail}`"

    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                _BASE_URL,
                json={
                    "chat_id": settings.telegram_chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                },
                timeout=10,
            )
        logger.info(f"Telegram alert sent: {monitor_name} {status}")
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")
