import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.monitor import Monitor
from app.models.incident import Incident
from app.schemas.incident import IncidentResponse

router = APIRouter(tags=["incidents"])


@router.get("/api/incidents", response_model=list[IncidentResponse])
async def list_incidents(
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Incident).order_by(Incident.started_at.desc()).limit(limit)
    )
    return result.scalars().all()


@router.get(
    "/api/monitors/{monitor_id}/incidents",
    response_model=list[IncidentResponse],
)
async def list_monitor_incidents(
    monitor_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    monitor = await db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    result = await db.execute(
        select(Incident)
        .where(Incident.monitor_id == monitor_id)
        .order_by(Incident.started_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
