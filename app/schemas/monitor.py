import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.monitor import CheckType, MonitorStatus


# --- Request schemas ---

class MonitorCreate(BaseModel):
    """POST /api/monitors request body."""
    name: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., min_length=1, max_length=2048)
    check_type: CheckType = CheckType.http
    interval_seconds: int = Field(default=60, ge=10, le=3600)
    timeout_ms: int = Field(default=5000, ge=500, le=30000)


class MonitorUpdate(BaseModel):
    """PUT /api/monitors/{id} — all fields optional."""
    name: str | None = Field(None, min_length=1, max_length=255)
    url: str | None = Field(None, min_length=1, max_length=2048)
    check_type: CheckType | None = None
    interval_seconds: int | None = Field(None, ge=10, le=3600)
    timeout_ms: int | None = Field(None, ge=500, le=30000)
    status: MonitorStatus | None = None


# --- Response schemas ---

class MonitorResponse(BaseModel):
    """Single monitor response."""
    id: uuid.UUID
    name: str
    url: str
    check_type: CheckType
    interval_seconds: int
    timeout_ms: int
    status: MonitorStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}  # allows ORM model → Pydantic
