import time
import asyncio
import re
from urllib.parse import urlparse

from app.checkers.base import BaseChecker, CheckResultData


class PingChecker(BaseChecker):
    async def check(self, url: str, timeout_ms: int) -> CheckResultData:
        # Extract hostname
        parsed = urlparse(url if "://" in url else f"ping://{url}")
        host = parsed.hostname or url
        timeout_sec = max(1, int(timeout_ms / 1000))
        start = time.monotonic()

        try:
            # -c 1 = one packet, -W = timeout in seconds
            proc = await asyncio.create_subprocess_exec(
                "ping", "-c", "1", "-W", str(timeout_sec), host,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            elapsed = (time.monotonic() - start) * 1000

            if proc.returncode == 0:
                # Try to parse actual RTT from ping output: "time=12.3 ms"
                match = re.search(r"time[=<]([\d.]+)", stdout.decode())
                rt = float(match.group(1)) if match else elapsed
                return CheckResultData(is_up=True, response_time_ms=round(rt, 1))
            else:
                return CheckResultData(
                    is_up=False,
                    response_time_ms=round(elapsed, 1),
                    error_message="Ping failed (host unreachable or timeout)",
                )
        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            return CheckResultData(
                is_up=False,
                response_time_ms=round(elapsed, 1),
                error_message=str(e)[:1024],
            )
