import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CheckType(str, enum.Enum):
    http = "http"
    tcp = "tcp"
    ping = "ping"


class MonitorStatus(str, enum.Enum):
    up = "up"
    down = "down"
    paused = "paused"


class Monitor(Base):
    __tablename__ = "monitors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(2048))
    check_type: Mapped[CheckType] = mapped_column(
        Enum(CheckType), default=CheckType.http
    )
    interval_seconds: Mapped[int] = mapped_column(Integer, default=60)
    timeout_ms: Mapped[int] = mapped_column(Integer, default=5000)
    status: Mapped[MonitorStatus] = mapped_column(
        Enum(MonitorStatus), default=MonitorStatus.up
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships — lazy="selectin" avoids async lazy-load issues
    check_results = relationship("CheckResult", back_populates="monitor", lazy="selectin")
    incidents = relationship("Incident", back_populates="monitor", lazy="selectin")

    def __repr__(self):
        return f"<Monitor {self.name} ({self.check_type.value}://{self.url})>"
