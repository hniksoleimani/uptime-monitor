import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.monitor import Monitor
from app.models.check_result import CheckResult
from app.schemas.check_result import CheckResultResponse, UptimeResponse

router = APIRouter(prefix="/api/monitors/{monitor_id}", tags=["results"])

# Map period strings to timedelta
PERIOD_MAP = {
    "1h": timedelta(hours=1),
    "6h": timedelta(hours=6),
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
}


@router.get("/results", response_model=list[CheckResultResponse])
async def get_results(
    monitor_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    # Verify monitor exists
    monitor = await db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    result = await db.execute(
        select(CheckResult)
        .where(CheckResult.monitor_id == monitor_id)
        .order_by(CheckResult.checked_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/uptime", response_model=UptimeResponse)
async def get_uptime(
    monitor_id: uuid.UUID,
    period: str = Query(default="24h", pattern="^(1h|6h|24h|7d|30d)$"),
    db: AsyncSession = Depends(get_db),
):
    monitor = await db.get(Monitor, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    since = datetime.now(timezone.utc) - PERIOD_MAP[period]

    # Single query: count total, count successes, average response time
    result = await db.execute(
        select(
            func.count(CheckResult.id).label("total"),
            func.count(CheckResult.id).filter(CheckResult.is_up.is_(True)).label("success"),
            func.coalesce(func.avg(CheckResult.response_time_ms), 0).label("avg_rt"),
        ).where(
            CheckResult.monitor_id == monitor_id,
            CheckResult.checked_at >= since,
        )
    )
    row = result.one()
    total = row.total
    success = row.success
    pct = (success / total * 100) if total > 0 else 100.0

    return UptimeResponse(
        monitor_id=monitor_id,
        period=period,
        uptime_percentage=round(pct, 2),
        total_checks=total,
        successful_checks=success,
        avg_response_time_ms=round(row.avg_rt, 1),
    )
