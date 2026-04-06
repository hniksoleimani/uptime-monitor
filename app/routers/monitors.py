import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.monitor import Monitor
from app.schemas.monitor import MonitorCreate, MonitorUpdate, MonitorResponse

router = APIRouter(prefix="/api/monitors", tags=["monitors"])


@router.get("", response_model=list[MonitorResponse])
async def list_monitors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Monitor).order_by(Monitor.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=MonitorResponse, status_code=201)
async def create_monitor(data: MonitorCreate, db: AsyncSession = Depends(get_db)):
    monitor = Monitor(**data.model_dump())
    db.add(monitor)
    await db.flush()          # sends INSERT to DB, populates id/defaults
    await db.refresh(monitor) # reload from DB to get server-set fields
    return monitor


@router.get("/{monitor_id}", response_model=MonitorResponse)
async def get_monitor(monitor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    monitor = await db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return monitor


@router.put("/{monitor_id}", response_model=MonitorResponse)
async def update_monitor(
    monitor_id: uuid.UUID,
    data: MonitorUpdate,
    db: AsyncSession = Depends(get_db),
):
    monitor = await db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    # Only update fields that were actually sent (not None)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(monitor, field, value)

    await db.flush()
    await db.refresh(monitor)
    return monitor


@router.delete("/{monitor_id}", status_code=204)
async def delete_monitor(monitor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    monitor = await db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    await db.delete(monitor)
