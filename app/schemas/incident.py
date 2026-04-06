import uuid
from datetime import datetime

from pydantic import BaseModel


class IncidentResponse(BaseModel):
    id: uuid.UUID
    monitor_id: uuid.UUID
    started_at: datetime
    resolved_at: datetime | None
    cause: str | None
    alert_sent: bool

    model_config = {"from_attributes": True}
