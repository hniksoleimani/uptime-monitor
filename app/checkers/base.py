from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CheckResultData:
    """Checker output — not an ORM model, just a plain data container."""
    is_up: bool
    response_time_ms: float
    status_code: int | None = None
    error_message: str | None = None


class BaseChecker(ABC):
    @abstractmethod
    async def check(self, url: str, timeout_ms: int) -> CheckResultData:
        """Run a health check against the given URL/host. Must be implemented by subclasses."""
        ...
