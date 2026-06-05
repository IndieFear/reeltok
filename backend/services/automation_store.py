"""Stockage JSON atomique pour la config et la file d'automatisation."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"
CONFIG_FILE = DATA_DIR / "automation_config.json"
QUEUE_FILE = DATA_DIR / "automation_queue.json"
CAROUSELS_DIR = DATA_DIR / "generated_carousels"

DEFAULT_CONFIG: dict[str, Any] = {
    "sheet_csv_url": "",
    "enabled": False,
    "posts_per_day": 3,
    "start_hour": 8,
    "end_hour": 18,
    "default_content_type": "care-guide",
    "image_model": "runware",
    "upload_post_user": "leftonreadgirl",
    "upload_post_users": ["leftonreadgirl"],
    "post_mode": "DIRECT_POST",
    "privacy_level": "PUBLIC_TO_EVERYONE",
    "auto_add_music": True,
    "reference_image": "random",
    "auto_generate_on_sync": False,
    "timezone": "Europe/Paris",
    "scheduler_interval_seconds": 300,
}

JOB_STATUSES = {
    "imported",
    "scheduled",
    "generating",
    "ready",
    "publishing",
    "published",
    "failed",
    "skipped",
}


def _atomic_write(path: Path, data: Any) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def get_config() -> dict[str, Any]:
    stored = _read_json(CONFIG_FILE, {})
    merged = {**DEFAULT_CONFIG, **stored}
    users = merged.get("upload_post_users")
    if not isinstance(users, list) or not users:
        merged["upload_post_users"] = [merged.get("upload_post_user") or "leftonreadgirl"]
    merged["upload_post_user"] = merged["upload_post_users"][0]
    return merged


def save_config(config: dict[str, Any]) -> dict[str, Any]:
    merged = {**DEFAULT_CONFIG, **config}
    _atomic_write(CONFIG_FILE, merged)
    return merged


def list_jobs() -> list[dict[str, Any]]:
    jobs = _read_json(QUEUE_FILE, [])
    return jobs if isinstance(jobs, list) else []


def save_jobs(jobs: list[dict[str, Any]]) -> None:
    _atomic_write(QUEUE_FILE, jobs)


def get_job(job_id: str) -> dict[str, Any] | None:
    for job in list_jobs():
        if job.get("id") == job_id:
            return job
    return None


def update_job(job_id: str, **updates: Any) -> dict[str, Any] | None:
    jobs = list_jobs()
    for i, job in enumerate(jobs):
        if job.get("id") == job_id:
            jobs[i] = {**job, **updates, "updated_at": _now_iso()}
            save_jobs(jobs)
            return jobs[i]
    return None


def append_job_log(job_id: str, message: str, level: str = "info") -> None:
    jobs = list_jobs()
    for i, job in enumerate(jobs):
        if job.get("id") != job_id:
            continue
        logs = list(job.get("logs") or [])
        logs.append({"at": _now_iso(), "level": level, "message": message})
        jobs[i] = {**job, "logs": logs[-100:], "updated_at": _now_iso()}
        save_jobs(jobs)
        return


def upsert_jobs_from_topics(topics: list[dict[str, Any]], config: dict[str, Any]) -> tuple[int, int]:
    """Importe les sujets sans doublon (topic + content_type). Retourne (added, skipped)."""
    jobs = list_jobs()
    existing_keys = {
        (j.get("topic", "").strip().lower(), j.get("content_type", config["default_content_type"]))
        for j in jobs
        if j.get("status") not in {"published", "skipped"}
    }
    added = 0
    skipped = 0
    for row in topics:
        topic = row.get("topic", "").strip()
        if not topic:
            skipped += 1
            continue
        content_type = row.get("content_type") or config["default_content_type"]
        key = (topic.lower(), content_type)
        if key in existing_keys:
            skipped += 1
            continue
        job = {
            "id": str(uuid.uuid4()),
            "topic": topic,
            "content_type": content_type,
            "account": row.get("account") or config.get("upload_post_user"),
            "status": "imported",
            "scheduled_at": None,
            "error": None,
            "history_id": None,
            "carousel_dir": None,
            "caption": None,
            "tiktok_description": None,
            "sheet_row": row.get("sheet_row"),
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "published_at": None,
            "logs": [
                {
                    "at": _now_iso(),
                    "level": "info",
                    "message": f"Sujet importé depuis le Sheet (ligne {row.get('sheet_row', '?')})",
                }
            ],
        }
        jobs.append(job)
        existing_keys.add(key)
        added += 1
    save_jobs(jobs)
    return added, skipped


def carousel_dir_for_job(job_id: str) -> Path:
    path = CAROUSELS_DIR / job_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def delete_job(job_id: str) -> bool:
    """Supprime un job et ses fichiers carousel associés."""
    import shutil

    jobs = list_jobs()
    target = next((j for j in jobs if j.get("id") == job_id), None)
    if not target:
        return False

    carousel_dir = target.get("carousel_dir")
    if carousel_dir:
        path = Path(carousel_dir)
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
    else:
        fallback = CAROUSELS_DIR / job_id
        if fallback.is_dir():
            shutil.rmtree(fallback, ignore_errors=True)

    save_jobs([j for j in jobs if j.get("id") != job_id])
    return True


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
