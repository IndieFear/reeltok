"""Planification et exécution automatique des publications."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from backend.services.automation_pipeline import generate_job_carousel
from backend.services.automation_store import append_job_log, get_config, list_jobs, save_jobs, update_job
from backend.services.publish_service import publish_carousel_from_paths

logger = logging.getLogger(__name__)

_scheduler_task: asyncio.Task | None = None
_scheduler_running = False


def compute_daily_slot_times(
    posts_per_day: int,
    start_hour: int,
    end_hour: int,
) -> list[time]:
    """Calcule les heures de publication pour une journée (ex: 8h, 13h, 18h)."""
    if posts_per_day <= 0:
        return []
    if posts_per_day == 1:
        mid_minutes = int(((start_hour + end_hour) / 2) * 60)
        return [time(mid_minutes // 60, mid_minutes % 60)]

    start_minutes = start_hour * 60
    end_minutes = end_hour * 60
    step = (end_minutes - start_minutes) / (posts_per_day - 1)
    slots: list[time] = []
    for i in range(posts_per_day):
        total = int(round(start_minutes + step * i))
        slots.append(time(total // 60, total % 60))
    return slots


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _local_now(tz_name: str) -> datetime:
    return datetime.now(ZoneInfo(tz_name))


def _next_slot_datetime(
    after: datetime,
    slot_times: list[time],
    tz_name: str,
) -> datetime:
    """Trouve le prochain créneau disponible après `after` (timezone locale)."""
    tz = ZoneInfo(tz_name)
    local_after = after.astimezone(tz)
    for day_offset in range(0, 366):
        day = (local_after.date() + timedelta(days=day_offset))
        for slot in slot_times:
            candidate = datetime.combine(day, slot, tzinfo=tz)
            if candidate > local_after:
                return candidate
    raise RuntimeError("Impossible de calculer un créneau de publication")


def assign_schedules() -> int:
    """Assigne des créneaux aux jobs importés. Retourne le nombre de jobs planifiés."""
    config = get_config()
    jobs = list_jobs()
    tz_name = config.get("timezone", "Europe/Paris")
    slot_times = compute_daily_slot_times(
        int(config.get("posts_per_day", 3)),
        int(config.get("start_hour", 8)),
        int(config.get("end_hour", 18)),
    )
    if not slot_times:
        return 0

    scheduled_times = [
        _parse_iso(j.get("scheduled_at"))
        for j in jobs
        if j.get("scheduled_at") and j.get("status") not in {"published", "skipped", "failed"}
    ]
    last_scheduled = max((t for t in scheduled_times if t), default=None)
    cursor = last_scheduled or _local_now(tz_name)

    changed = 0
    for job in jobs:
        if job.get("status") != "imported":
            continue
        next_slot = _next_slot_datetime(cursor, slot_times, tz_name)
        job["scheduled_at"] = next_slot.isoformat()
        job["status"] = "scheduled"
        logs = list(job.get("logs") or [])
        logs.append(
            {
                "at": datetime.now(timezone.utc).isoformat(),
                "level": "info",
                "message": f"Planifié pour {next_slot.strftime('%d/%m/%Y %H:%M')}",
            }
        )
        job["logs"] = logs[-100:]
        cursor = next_slot
        changed += 1

    if changed:
        save_jobs(jobs)
    return changed


async def generate_pending_jobs(limit: int = 3, *, only_due: bool = True) -> int:
    """Génère les carrousels pour les jobs dont l'heure de publication est passée."""
    config = get_config()
    jobs = list_jobs()
    now = datetime.now(timezone.utc)
    count = 0
    for job in jobs:
        if count >= limit:
            break
        if job.get("status") not in {"scheduled", "ready"}:
            continue
        if only_due:
            scheduled_at = _parse_iso(job.get("scheduled_at"))
            if not scheduled_at or scheduled_at > now:
                continue
        if job.get("carousel_dir") and Path(job["carousel_dir"]).exists():
            if job.get("status") != "ready":
                update_job(job["id"], status="ready")
            continue
        try:
            await generate_job_carousel(job, config)
            count += 1
        except Exception as e:
            logger.warning("Génération échouée pour %s: %s", job.get("topic"), e)
    return count


def resolve_publish_accounts(job: dict, config: dict) -> list[str]:
    """Comptes cibles : colonne Sheet > liste config > compte unique."""
    if job.get("account"):
        return [job["account"]]
    users = config.get("upload_post_users")
    if isinstance(users, list) and users:
        return users
    return [config.get("upload_post_user") or "leftonreadgirl"]


async def publish_job(job: dict, config: dict) -> dict:
    """Publie un job prêt sur un ou plusieurs comptes TikTok."""
    job_id = job["id"]
    carousel_dir = job.get("carousel_dir")
    if not carousel_dir:
        raise RuntimeError("Carousel non généré")

    paths = sorted(Path(carousel_dir).glob("slide_*.jpg"))
    if not paths:
        raise RuntimeError("Aucune slide trouvée sur disque")

    accounts = resolve_publish_accounts(job, config)
    title = job.get("caption") or job.get("topic", "Carousel")
    description = job.get("tiktok_description") or job.get("caption") or job.get("topic", "")

    update_job(job_id, status="publishing", error=None)
    append_job_log(job_id, f"Début publication sur {len(accounts)} compte(s)", "info")
    results: dict[str, dict] = {}
    errors: list[str] = []
    try:
        for account in accounts:
            try:
                append_job_log(job_id, f"Envoi vers @{account}…", "info")
                results[account] = publish_carousel_from_paths(
                    paths,
                    title=title,
                    description=description,
                    post_mode=config.get("post_mode", "DIRECT_POST"),
                    upload_post_user=account,
                    privacy_level=config.get("privacy_level", "PUBLIC_TO_EVERYONE"),
                    auto_add_music=bool(config.get("auto_add_music", True)),
                )
            except Exception as e:
                errors.append(f"@{account}: {e}")
                append_job_log(job_id, f"Échec @{account}: {e}", "error")

        if errors and len(errors) == len(accounts):
            raise RuntimeError("; ".join(errors))

        for account in results:
            append_job_log(job_id, f"Publié sur @{account}", "success")

        return update_job(
            job_id,
            status="published",
            published_at=datetime.now(timezone.utc).isoformat(),
            published_accounts=list(results.keys()),
            publish_result=results,
            error="; ".join(errors) if errors else None,
        ) or job
    except Exception as e:
        append_job_log(job_id, f"Publication échouée: {e}", "error")
        update_job(job_id, status="failed", error=str(e))
        raise


async def run_due_jobs() -> dict[str, int]:
    """Exécute génération et publication pour les jobs dus."""
    config = get_config()
    if not config.get("enabled"):
        return {"scheduled": 0, "generated": 0, "published": 0, "errors": 0}

    scheduled = assign_schedules()
    generated = 0
    published = 0
    errors = 0
    now = datetime.now(timezone.utc)
    jobs = list_jobs()

    for job in jobs:
        if job.get("status") not in {"scheduled", "ready"}:
            continue
        scheduled_at = _parse_iso(job.get("scheduled_at"))
        if not scheduled_at or scheduled_at > now:
            continue

        try:
            if not job.get("carousel_dir"):
                await generate_job_carousel(job, config)
                generated += 1
                job = next((j for j in list_jobs() if j["id"] == job["id"]), job)

            if job.get("status") == "ready":
                await publish_job(job, config)
                published += 1
        except Exception as e:
            logger.exception("Erreur job %s: %s", job.get("id"), e)
            errors += 1

    return {"scheduled": scheduled, "generated": generated, "published": published, "errors": errors}


async def _scheduler_loop() -> None:
    global _scheduler_running
    _scheduler_running = True
    logger.info("Automation scheduler démarré")
    while _scheduler_running:
        config = get_config()
        interval = max(60, int(config.get("scheduler_interval_seconds", 300)))
        try:
            if config.get("enabled"):
                result = await run_due_jobs()
                if any(result.values()):
                    logger.info("Scheduler tick: %s", result)
        except Exception as e:
            logger.exception("Erreur scheduler: %s", e)
        await asyncio.sleep(interval)


def start_scheduler() -> None:
    global _scheduler_task
    if _scheduler_task and not _scheduler_task.done():
        return
    _scheduler_task = asyncio.create_task(_scheduler_loop())


async def stop_scheduler() -> None:
    global _scheduler_running, _scheduler_task
    _scheduler_running = False
    if _scheduler_task:
        _scheduler_task.cancel()
        try:
            await _scheduler_task
        except asyncio.CancelledError:
            pass
        _scheduler_task = None
