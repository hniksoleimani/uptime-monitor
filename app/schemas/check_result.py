import uuid
from datetime import datetime

from pydantic import BaseModel


class CheckResultResponse(BaseModel):
    id: uuid.UUID
    monitor_id: uuid.UUID
    status_code: int | None
    response_time_ms: float
    is_up: bool
    error_message: str | None
    checked_at: datetime

    model_config = {"from_attributes": True}


class UptimeResponse(BaseModel):
    monitor_id: uuid.UUID
    period: str
    uptime_percentage: float
    total_checks: int
    successful_checks: int
    avg_response_time_ms: float
