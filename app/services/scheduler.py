import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.monitor import Monitor, MonitorStatus
from app.models.check_result import CheckResult
from app.models.incident import Incident
from app.checkers import get_checker

logger = logging.getLogger(__name__)


async def run_check(monitor_id):
    """Run a single health check for one monitor. Called by APScheduler."""
    async with async_session() as db:
        monitor = await db.get(Monitor, monitor_id)
        if not monitor or monitor.status == MonitorStatus.paused:
            return

        # Run the appropriate checker
        checker = get_checker(monitor.check_type)
        result_data = await checker.check(monitor.url, monitor.timeout_ms)

        # Save check result
        check_result = CheckResult(
            monitor_id=monitor.id,
            status_code=result_data.status_code,
            response_time_ms=result_data.response_time_ms,
            is_up=result_data.is_up,
            error_message=result_data.error_message,
        )
        db.add(check_result)

        # Detect state changes (up→down or down→up)
        was_up = monitor.status == MonitorStatus.up

        if was_up and not result_data.is_up:
            # --- WENT DOWN ---
            monitor.status = MonitorStatus.down
            incident = Incident(
                monitor_id=monitor.id,
                cause=result_data.error_message,
            )
            db.add(incident)
            logger.warning(f"Monitor '{monitor.name}' is DOWN: {result_data.error_message}")

        elif not was_up and result_data.is_up:
            # --- CAME BACK UP ---
            monitor.status = MonitorStatus.up
            # Resolve the latest open incident
            stmt = (
                select(Incident)
                .where(
                    Incident.monitor_id == monitor.id,
                    Incident.resolved_at.is_(None),
                )
                .order_by(Incident.started_at.desc())
                .limit(1)
            )
            result = await db.execute(stmt)
            incident = result.scalar_one_or_none()
            if incident:
                incident.resolved_at = datetime.now(timezone.utc)
            logger.info(f"Monitor '{monitor.name}' is back UP")

        await db.commit()
