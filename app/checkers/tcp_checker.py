import time
import asyncio
from urllib.parse import urlparse

from app.checkers.base import BaseChecker, CheckResultData


class TcpChecker(BaseChecker):
    async def check(self, url: str, timeout_ms: int) -> CheckResultData:
        # Parse host:port from url — expects "host:port" or "scheme://host:port"
        parsed = urlparse(url if "://" in url else f"tcp://{url}")
        host = parsed.hostname or url
        port = parsed.port or 80
        timeout_sec = timeout_ms / 1000
        start = time.monotonic()

        try:
            # Just open and immediately close a TCP connection
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=timeout_sec,
            )
            writer.close()
            await writer.wait_closed()
            elapsed = (time.monotonic() - start) * 1000

            return CheckResultData(is_up=True, response_time_ms=round(elapsed, 1))
        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            return CheckResultData(
                is_up=False,
                response_time_ms=round(elapsed, 1),
                error_message=str(e)[:1024],
            )
