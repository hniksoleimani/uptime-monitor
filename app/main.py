import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.config import get_settings
from app.database import engine, Base, async_session
from app.models import Monitor, MonitorStatus  # noqa: F401 — ensures models registered
from app.routers import monitors, results, incidents, status
from app.services.scheduler import run_check

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def _schedule_all_monitors():
    """Load all active monitors from DB and schedule their checks."""
    async with async_session() as db:
        stmt = select(Monitor).where(Monitor.status != MonitorStatus.paused)
        result = await db.execute(stmt)
        monitors_list = result.scalars().all()

    for mon in monitors_list:
        scheduler.add_job(
            run_check,
            "interval",
            seconds=mon.interval_seconds,
            args=[mon.id],
            id=str(mon.id),
            replace_existing=True,
        )
    logger.info(f"Scheduled {len(monitors_list)} monitor(s)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # 1. Create tables (dev convenience — use Alembic migrations in prod)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready")

    # 2. Start the scheduler
    await _schedule_all_monitors()
    scheduler.start()
    logger.info("Scheduler started")

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    await engine.dispose()
    logger.info("Shutdown complete")


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

# Register routers
app.include_router(monitors.router)
app.include_router(results.router)
app.include_router(incidents.router)
app.include_router(status.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
