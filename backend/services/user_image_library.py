"""Bibliothèque d'images utilisateur persistée sur disque."""

from __future__ import annotations

import json
import mimetypes
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"
USER_IMAGES_DIR = DATA_DIR / "user_images"
INDEX_FILE = DATA_DIR / "user_image_library.json"

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}
MAX_BYTES = 15 * 1024 * 1024


def _atomic_write(path: Path, data: Any) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _read_index() -> list[dict[str, Any]]:
    if not INDEX_FILE.is_file():
        return []
    try:
        data = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _write_index(entries: list[dict[str, Any]]) -> None:
    _atomic_write(INDEX_FILE, entries)


def _guess_mime(filename: str, fallback: str | None) -> str:
    if fallback and fallback in ALLOWED_MIME:
        return fallback
    guessed, _ = mimetypes.guess_type(filename)
    if guessed in ALLOWED_MIME:
        return guessed
    ext = Path(filename).suffix.lower()
    if ext in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    if ext == ".webp":
        return "image/webp"
    raise ValueError("Format non supporté (jpeg, png, webp uniquement)")


def list_images() -> list[dict[str, Any]]:
    entries = _read_index()
    valid: list[dict[str, Any]] = []
    changed = False
    for entry in entries:
        image_id = entry.get("id")
        stored = entry.get("stored_filename")
        if not image_id or not stored:
            changed = True
            continue
        path = USER_IMAGES_DIR / stored
        if not path.is_file():
            changed = True
            continue
        valid.append(
            {
                "id": image_id,
                "filename": entry.get("filename") or stored,
                "mime": entry.get("mime") or "image/jpeg",
                "created_at": entry.get("created_at") or "",
                "size_bytes": path.stat().st_size,
                "url": f"/api/user-images/{image_id}",
            }
        )
    if changed:
        _write_index(
            [
                {
                    "id": e["id"],
                    "filename": e.get("filename") or e.get("stored_filename"),
                    "stored_filename": e.get("stored_filename"),
                    "mime": e.get("mime"),
                    "created_at": e.get("created_at"),
                }
                for e in entries
                if e.get("id")
                and e.get("stored_filename")
                and (USER_IMAGES_DIR / e["stored_filename"]).is_file()
            ]
        )
    valid.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return valid


def get_image_path(image_id: str) -> Path | None:
    for entry in _read_index():
        if entry.get("id") == image_id:
            path = USER_IMAGES_DIR / entry.get("stored_filename", "")
            return path if path.is_file() else None
    return None


def get_image_meta(image_id: str) -> dict[str, Any] | None:
    for entry in _read_index():
        if entry.get("id") == image_id:
            path = USER_IMAGES_DIR / entry.get("stored_filename", "")
            if not path.is_file():
                return None
            return {
                **entry,
                "size_bytes": path.stat().st_size,
                "url": f"/api/user-images/{image_id}",
            }
    return None


def add_image(content: bytes, filename: str, mime: str | None = None) -> dict[str, Any]:
    if len(content) > MAX_BYTES:
        raise ValueError(f"Image trop lourde (max {MAX_BYTES // (1024 * 1024)} Mo)")
    if len(content) < 32:
        raise ValueError("Fichier vide ou invalide")

    safe_name = Path(filename).name or "image.jpg"
    ext = Path(safe_name).suffix.lower()
    if ext not in ALLOWED_EXT:
        raise ValueError("Extension non supportée (jpg, png, webp)")

    resolved_mime = _guess_mime(safe_name, mime)
    image_id = str(uuid.uuid4())
    stored_filename = f"{image_id}{ext}"

    USER_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    (USER_IMAGES_DIR / stored_filename).write_bytes(content)

    entry = {
        "id": image_id,
        "filename": safe_name,
        "stored_filename": stored_filename,
        "mime": resolved_mime,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    entries = _read_index()
    entries.append(entry)
    _write_index(entries)

    return {
        "id": image_id,
        "filename": safe_name,
        "mime": resolved_mime,
        "created_at": entry["created_at"],
        "size_bytes": len(content),
        "url": f"/api/user-images/{image_id}",
    }


def delete_image(image_id: str) -> bool:
    entries = _read_index()
    kept: list[dict[str, Any]] = []
    deleted = False
    for entry in entries:
        if entry.get("id") == image_id:
            path = USER_IMAGES_DIR / entry.get("stored_filename", "")
            if path.is_file():
                path.unlink()
            deleted = True
            continue
        kept.append(entry)
    if deleted:
        _write_index(kept)
    return deleted


def resolve_user_image_b64(image_id: str) -> str | None:
    """Charge une image bibliothèque en base64 (sans préfixe data:)."""
    path = get_image_path(image_id)
    if not path:
        return None
    import base64

    return base64.b64encode(path.read_bytes()).decode()
