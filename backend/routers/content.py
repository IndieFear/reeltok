"""Endpoint pour générer le contenu via Gemini."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel

from gemini_text_generator import (
    GeminiConfigError,
    generate_carousel_content,
)

router = APIRouter()

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"
HISTORY_FILE = DATA_DIR / "content_history.json"
MAX_HISTORY_ITEMS = 100


@router.get("/content-types")
def get_content_types():
    """Retourne la liste des types de contenu disponibles (guide, astrologie, déco, etc.)."""
    from backend.content_types.registry import list_content_types
    return list_content_types()


@router.get("/prompt-preview")
def get_prompt_preview(
    keyword: str = Query(..., min_length=1),
    content_type: str = Query("care-guide"),
    num_slides: int = Query(6, ge=1, le=10),
):
    """Retourne le prompt qui sera envoyé à Gemini (pour édition manuelle)."""
    from backend.content_types.registry import build_prompt_for_type
    try:
        prompt = build_prompt_for_type(content_type, keyword, num_slides, variation_index=0)
        return {"prompt": prompt}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class GenerateContentRequest(BaseModel):
    keyword: str
    num_slides: int = 6
    content_type: str = "care-guide"
    use_cache: bool = False
    variation_index: int = 0
    custom_prompt: str | None = None


class TipSlideResponse(BaseModel):
    tag: str
    body: str


class CarouselContentResponse(BaseModel):
    intro_title: str
    intro_body: str
    tips: list[TipSlideResponse]
    caption: str
    tiktok_description: str
    image_prompts: list[str]
    history_id: str | None = None


class GeneratedImageHistoryItem(BaseModel):
    slide_index: int
    image_model: str
    source_url: str
    filename: str | None = None
    mime: str | None = None
    generated_at: str


class ContentHistoryEntry(BaseModel):
    id: str
    created_at: str
    keyword: str
    content_type: str
    num_slides: int
    custom_prompt: str | None = None
    content: CarouselContentResponse
    generated_images: list[GeneratedImageHistoryItem] = []


class ContentHistoryListResponse(BaseModel):
    items: list[ContentHistoryEntry]


def _read_history() -> list[dict]:
    if not HISTORY_FILE.is_file():
        return []
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    return data


def _write_history(items: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = HISTORY_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(items[:MAX_HISTORY_ITEMS], ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(HISTORY_FILE)


def _save_history_entry(request: GenerateContentRequest, content: CarouselContentResponse) -> str:
    entry_id = str(uuid.uuid4())
    content.history_id = entry_id
    entry = {
        "id": entry_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "keyword": request.keyword,
        "content_type": request.content_type,
        "num_slides": request.num_slides,
        "custom_prompt": request.custom_prompt,
        "content": content.dict(),
        "generated_images": [],
    }
    _write_history([entry, *_read_history()])
    return entry_id


@router.get("/content-history", response_model=ContentHistoryListResponse)
def list_content_history():
    """Retourne les derniers contenus générés."""
    return {"items": _read_history()}


@router.get("/content-history/{history_id}", response_model=ContentHistoryEntry)
def get_content_history_entry(history_id: str):
    """Retourne un contenu généré à partir de son identifiant."""
    for entry in _read_history():
        if entry.get("id") == history_id:
            return entry
    raise HTTPException(status_code=404, detail="Historique introuvable")


@router.delete("/content-history/{history_id}")
def delete_content_history_entry(history_id: str):
    """Supprime un contenu généré de l'historique."""
    history = _read_history()
    next_history = [entry for entry in history if entry.get("id") != history_id]
    if len(next_history) == len(history):
        raise HTTPException(status_code=404, detail="Historique introuvable")
    _write_history(next_history)
    return {"success": True}


@router.get("/content-history/{history_id}/image/{slide_index}")
def get_content_history_image(history_id: str, slide_index: int):
    """Télécharge une image générée stockée dans l'historique."""
    for entry in _read_history():
        if entry.get("id") != history_id:
            continue
        for image in entry.get("generated_images", []):
            if image.get("slide_index") != slide_index:
                continue
            source_url = image.get("source_url")
            if not source_url:
                break
            try:
                resp = requests.get(source_url, timeout=60)
                resp.raise_for_status()
            except requests.RequestException as e:
                raise HTTPException(status_code=502, detail=f"Image historique inaccessible: {e}") from e
            media_type = image.get("mime") or resp.headers.get("content-type", "image/jpeg")
            return Response(content=resp.content, media_type=media_type)
        raise HTTPException(status_code=404, detail="Image historique introuvable")
    raise HTTPException(status_code=404, detail="Historique introuvable")


@router.post("/generate-content", response_model=CarouselContentResponse)
def generate_content(request: GenerateContentRequest):
    """Génère le contenu du carousel via Gemini (intro + tips + caption + description)."""
    try:
        content = generate_carousel_content(
            keyword=request.keyword,
            num_slides=request.num_slides,
            content_type=request.content_type,
            use_cache=request.use_cache,
            variation_index=request.variation_index,
            custom_prompt=request.custom_prompt,
        )
        response = CarouselContentResponse(
            intro_title=content.intro_title,
            intro_body=content.intro_body,
            tips=[TipSlideResponse(tag=t.tag, body=t.body) for t in content.tips],
            caption=content.caption,
            tiktok_description=content.tiktok_description,
            image_prompts=content.image_prompts,
        )
        _save_history_entry(request, response)
        return response
    except GeminiConfigError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
