"""Endpoints pour l'automatisation Google Sheets + publication planifiée."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.services.automation_pipeline import generate_job_carousel
from backend.services.automation_scheduler import (
    assign_schedules,
    compute_daily_slot_times,
    generate_pending_jobs,
    publish_job,
    run_due_jobs,
)
from backend.services.automation_store import (
    DEFAULT_CONFIG,
    append_job_log,
    delete_job,
    get_config,
    get_job,
    list_jobs,
    save_config,
    update_job,
    upsert_jobs_from_topics,
)
from backend.services.sheets_importer import fetch_sheet_rows

router = APIRouter()
logger = logging.getLogger(__name__)


class AutomationConfigModel(BaseModel):
    sheet_csv_url: str = ""
    enabled: bool = False
    posts_per_day: int = Field(3, ge=1, le=10)
    start_hour: int = Field(8, ge=0, le=23)
    end_hour: int = Field(18, ge=1, le=23)
    default_content_type: str = "care-guide"
    image_model: str = "runware"
    upload_post_user: str = "leftonreadgirl"
    upload_post_users: list[str] = Field(default_factory=lambda: ["leftonreadgirl"])
    post_mode: str = "DIRECT_POST"
    privacy_level: str = "PUBLIC_TO_EVERYONE"
    auto_add_music: bool = True
    reference_image: str = "random"
    auto_generate_on_sync: bool = False
    timezone: str = "Europe/Paris"
    scheduler_interval_seconds: int = Field(300, ge=60, le=3600)


class SyncSheetRequest(BaseModel):
    sheet_csv_url: str | None = None


class UpdateJobScheduleRequest(BaseModel):
    scheduled_at: str


@router.get("/automation/config")
def get_automation_config():
    config = get_config()
    slots = compute_daily_slot_times(
        int(config.get("posts_per_day", 3)),
        int(config.get("start_hour", 8)),
        int(config.get("end_hour", 18)),
    )
    return {
        "config": config,
        "slot_times": [t.strftime("%H:%M") for t in slots],
        "defaults": DEFAULT_CONFIG,
    }


@router.post("/automation/config")
def update_automation_config(body: AutomationConfigModel):
    if body.start_hour >= body.end_hour:
        raise HTTPException(status_code=400, detail="start_hour doit être inférieur à end_hour")
    if not body.upload_post_users:
        raise HTTPException(status_code=400, detail="Sélectionne au moins un compte TikTok")
    payload = body.model_dump()
    payload["upload_post_user"] = body.upload_post_users[0]
    saved = save_config(payload)
    return {"config": saved}


@router.get("/automation/jobs")
def get_automation_jobs():
    jobs = list_jobs()
    jobs.sort(key=lambda j: j.get("scheduled_at") or j.get("created_at") or "", reverse=False)
    return {"jobs": jobs, "total": len(jobs)}


def _list_job_slides(job: dict[str, Any]) -> list[dict[str, str]]:
    carousel_dir = job.get("carousel_dir")
    if not carousel_dir:
        return []
    path = Path(carousel_dir)
    if not path.is_dir():
        return []
    job_id = job["id"]
    return [
        {
            "filename": p.name,
            "url": f"/api/automation/jobs/{job_id}/slides/{p.name}",
        }
        for p in sorted(path.glob("slide_*.jpg"))
    ]


@router.get("/automation/jobs/{job_id}")
def get_automation_job(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job introuvable")
    return {"job": job, "slides": _list_job_slides(job)}


@router.get("/automation/jobs/{job_id}/slides/{filename}")
def get_automation_job_slide(job_id: str, filename: str):
    if not re.fullmatch(r"slide_\d{2}\.jpg", filename):
        raise HTTPException(status_code=400, detail="Nom de fichier invalide")
    job = get_job(job_id)
    if not job or not job.get("carousel_dir"):
        raise HTTPException(status_code=404, detail="Job ou carousel introuvable")
    path = Path(job["carousel_dir"]) / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Slide introuvable")
    return FileResponse(path, media_type="image/jpeg")


@router.post("/automation/sync-sheet")
async def sync_sheet(body: SyncSheetRequest | None = None):
    config = get_config()
    csv_url = (body.sheet_csv_url if body and body.sheet_csv_url else None) or config.get("sheet_csv_url")
    if not csv_url:
        raise HTTPException(status_code=400, detail="URL Google Sheet CSV requise")

    if body and body.sheet_csv_url:
        config = save_config({**config, "sheet_csv_url": body.sheet_csv_url})

    try:
        rows = fetch_sheet_rows(csv_url)
    except Exception as e:
        logger.exception("Sync sheet failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e

    added, skipped = upsert_jobs_from_topics(rows, config)
    scheduled = assign_schedules()

    return {
        "success": True,
        "imported": added,
        "skipped": skipped,
        "scheduled": scheduled,
        "generated": 0,
        "rows_in_sheet": len(rows),
    }


@router.delete("/automation/jobs/{job_id}")
def delete_automation_job(job_id: str):
    if not delete_job(job_id):
        raise HTTPException(status_code=404, detail="Job introuvable")
    return {"success": True}


@router.patch("/automation/jobs/{job_id}/schedule")
def update_job_schedule(job_id: str, body: UpdateJobScheduleRequest):
    from datetime import datetime, timezone

    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job introuvable")
    if job.get("status") == "published":
        raise HTTPException(status_code=400, detail="Impossible de modifier l'heure d'un sujet déjà publié")

    raw = body.scheduled_at.strip()
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            config = get_config()
            from zoneinfo import ZoneInfo

            parsed = parsed.replace(tzinfo=ZoneInfo(config.get("timezone", "Europe/Paris")))
        scheduled_iso = parsed.isoformat()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Date invalide: {e}") from e

    updates: dict[str, Any] = {"scheduled_at": scheduled_iso}
    if job.get("status") in {"imported", "failed"}:
        updates["status"] = "scheduled"
        updates["error"] = None

    updated = update_job(job_id, **updates)
    append_job_log(
        job_id,
        f"Heure planifiée modifiée manuellement → {parsed.strftime('%d/%m/%Y %H:%M')}",
        "info",
    )
    return {"success": True, "job": updated}


@router.post("/automation/jobs/{job_id}/generate")
async def generate_job(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job introuvable")
    if job.get("status") == "published":
        raise HTTPException(status_code=400, detail="Job déjà publié")

    config = get_config()
    try:
        updated = await generate_job_carousel(job, config)
        return {"success": True, "job": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/automation/jobs/{job_id}/publish")
async def publish_job_endpoint(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job introuvable")
    if job.get("status") not in {"ready", "scheduled", "failed"}:
        raise HTTPException(status_code=400, detail=f"Statut incompatible: {job.get('status')}")

    config = get_config()
    if job.get("status") != "ready" or not job.get("carousel_dir"):
        try:
            job = await generate_job_carousel(job, config)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Génération échouée: {e}") from e

    try:
        updated = await publish_job(job, config)
        return {"success": True, "job": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/automation/generate-pending")
async def generate_pending(limit: int = 5):
    count = await generate_pending_jobs(limit=limit)
    return {"success": True, "generated": count}


@router.post("/automation/run-due")
async def run_due():
    result = await run_due_jobs()
    return {"success": True, **result}


@router.post("/automation/assign-schedules")
def assign_schedules_endpoint():
    count = assign_schedules()
    return {"success": True, "scheduled": count}
