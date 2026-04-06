from app.checkers.base import BaseChecker, CheckResultData
from app.checkers.http_checker import HttpChecker
from app.checkers.tcp_checker import TcpChecker
from app.checkers.ping_checker import PingChecker
from app.models.monitor import CheckType

_CHECKERS: dict[CheckType, BaseChecker] = {
    CheckType.http: HttpChecker(),
    CheckType.tcp: TcpChecker(),
    CheckType.ping: PingChecker(),
}


def get_checker(check_type: CheckType) -> BaseChecker:
    """Factory — returns the right checker for the monitor's check_type."""
    return _CHECKERS[check_type]


__all__ = ["get_checker", "BaseChecker", "CheckResultData"]