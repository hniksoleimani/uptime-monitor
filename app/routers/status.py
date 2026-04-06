from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.monitor import Monitor
from app.schemas.monitor import MonitorResponse

router = APIRouter(tags=["status"])


@router.get("/api/status", response_model=list[MonitorResponse])
async def public_status(db: AsyncSession = Depends(get_db)):
    """Public endpoint — returns all monitors with current status."""
    result = await db.execute(select(Monitor).order_by(Monitor.name))
    return result.scalars().all()
