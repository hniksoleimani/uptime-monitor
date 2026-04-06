import time
import httpx

from app.checkers.base import BaseChecker, CheckResultData


class HttpChecker(BaseChecker):
    async def check(self, url: str, timeout_ms: int) -> CheckResultData:
        timeout_sec = timeout_ms / 1000
        start = time.monotonic()

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=timeout_sec, follow_redirects=True)
            elapsed = (time.monotonic() - start) * 1000  # ms

            return CheckResultData(
                is_up=resp.status_code < 400,
                response_time_ms=round(elapsed, 1),
                status_code=resp.status_code,
            )
        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            return CheckResultData(
                is_up=False,
                response_time_ms=round(elapsed, 1),
                error_message=str(e)[:1024],
            )
