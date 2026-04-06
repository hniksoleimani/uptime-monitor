# Import all models here so that Base.metadata picks them up
# This is required for Alembic migrations to detect all tables
from app.models.monitor import Monitor, CheckType, MonitorStatus
from app.models.check_result import CheckResult
from app.models.incident import Incident

__all__ = ["Monitor", "CheckType", "MonitorStatus", "CheckResult", "Incident"]