"""Pipeline complet: contenu Gemini → images → overlay carousel → sauvegarde."""

from __future__ import annotations

import asyncio
import base64
import logging
import os
import random
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gemini_text_generator import GeminiConfigError, generate_carousel_content
from image_overlay import create_intro_image, create_tip_image

from backend.routers.images import (
    IMAGE_MODEL_RUNWARE,
    _generate_one_image_sync,
    _get_reference_for_first_image,
    _normalize_image_model,
    _try_grok_fallback_sync,
)
from backend.routers.templates import get_girls_images
from backend.services.automation_store import append_job_log, carousel_dir_for_job, update_job

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = ROOT / "backend" / "templates"
LEAFEE_IMAGE = ROOT / "assets" / "leafee.jpg"
MAX_CONCURRENT_IMAGE_GENERATIONS = 6
MAX_CONCURRENT_CAROUSEL_RENDERS = max(
    1, int(os.getenv("CAROUSEL_RENDER_CONCURRENCY", "1"))
)

SEVEN_SLIDE_TYPES = {"top-x", "top-signs", "decor", "astrology"}


def resolve_reference_image(config: dict[str, Any]) -> str:
    """Choisit l'image fille de référence (aléatoire par défaut)."""
    available = [img["id"] for img in get_girls_images()]
    if not available:
        return "fille1"
    ref = (config.get("reference_image") or "random").strip()
    if ref == "random":
        return random.choice(available)
    if ref in available:
        return ref
    return random.choice(available)


def num_slides_for_content_type(content_type: str) -> int:
    return 7 if content_type in SEVEN_SLIDE_TYPES else 6


def leafee_slide_index(tips: list[Any]) -> int:
    for i, tip in enumerate(tips):
        tag = tip.tag if hasattr(tip, "tag") else tip.get("tag", "")
        if tag == "LEAFEE":
            return i + 1
    return -1


def build_slides_content(content: Any) -> list[dict[str, Any]]:
    slides: list[dict[str, Any]] = [
        {
            "type": "intro",
            "title": content.intro_title,
            "body": content.intro_body,
            "template_id": "leafee-v2",
        }
    ]
    for tip in content.tips:
        tag = tip.tag if hasattr(tip, "tag") else tip.get("tag", "")
        body = tip.body if hasattr(tip, "body") else tip.get("body", "")
        slides.append({"type": "tip", "tag": tag, "body": body, "template_id": "leafee-v2"})
    return slides


async def _generate_images_for_prompts(
    prompts: list[str],
    image_model: str,
    reference_image: str | None,
) -> list[Path]:
    """Génère les images de fond et retourne les chemins temporaires."""
    import os
    import tempfile

    normalized_model = _normalize_image_model(image_model)
    uses_replicate = normalized_model in {"replicate-gpt-image-2", "replicate-grok-imagine-image"}
    api_key_name = "REPLICATE_API_TOKEN" if uses_replicate else "RUNWARE_API_KEY"
    api_key = os.getenv("REPLICATE_API_TOKEN") or os.getenv("REPLICATE_API_KEY") if uses_replicate else os.getenv(api_key_name)
    ref_images = _get_reference_for_first_image([reference_image] if reference_image else None)

    tmpdir = Path(tempfile.mkdtemp(prefix="automation_bg_"))
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_IMAGE_GENERATIONS)
    results: list[Path | None] = [None] * len(prompts)

    async def generate_one(i: int, prompt: str) -> None:
        if not prompt.strip():
            return
        async with semaphore:
            last_error = None
            result = None
            if api_key:
                try:
                    result = await asyncio.to_thread(
                        _generate_one_image_sync,
                        api_key,
                        prompt,
                        normalized_model,
                        image_index=i,
                        reference_images=ref_images if i == 0 else None,
                    )
                except Exception as e:
                    last_error = str(e)
            if not result:
                try:
                    result = await asyncio.to_thread(
                        _try_grok_fallback_sync,
                        prompt,
                        image_index=i,
                        reference_images=ref_images if i == 0 else None,
                        reason=last_error,
                    )
                except Exception as e:
                    raise RuntimeError(f"Génération image slide {i + 1} échouée: {e}") from e
            if not result or not result.get("base64"):
                raise RuntimeError(f"Génération image slide {i + 1} échouée: {last_error or 'aucune image'}")

            ext = ".png" if (result.get("mime") or "").endswith("png") else ".jpg"
            out = tmpdir / f"bg_{i:02d}{ext}"
            out.write_bytes(base64.b64decode(result["base64"]))
            results[i] = out

    await asyncio.gather(*(generate_one(i, p) for i, p in enumerate(prompts)))

    filled: list[Path] = []
    for i, path in enumerate(results):
        if path is None:
            raise RuntimeError(f"Image manquante pour la slide {i + 1}")
        filled.append(path)
    return filled


async def _render_carousel_slides(
    slides_content: list[dict[str, Any]],
    bg_paths: list[Path],
    output_dir: Path,
) -> list[Path]:
    fallback_intro = TEMPLATES_DIR / "intro" / "leafee-v2.html"
    fallback_tip = TEMPLATES_DIR / "tip" / "leafee-v2.html"
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_CAROUSEL_RENDERS)

    async def render_slide(i: int, slide: dict[str, Any]) -> Path:
        out_path = output_dir / f"slide_{i:02d}.jpg"
        slide_type = slide.get("type", "tip")
        if i == 0:
            slide_type = "intro"
        template_id = slide.get("template_id", "leafee-v2")
        bg_index = i if i < len(bg_paths) else len(bg_paths) - 1

        async with semaphore:
            if slide_type == "intro":
                intro_tpl = TEMPLATES_DIR / "intro" / f"{template_id}.html"
                tpl = intro_tpl if intro_tpl.exists() else fallback_intro
                await asyncio.to_thread(
                    create_intro_image,
                    background_path=bg_paths[bg_index],
                    title=slide.get("title", "Care Guide"),
                    body=slide.get("body", ""),
                    output_path=out_path,
                    template_html_path=tpl if tpl.exists() else None,
                    title_bg_color=slide.get("title_bg_color"),
                )
            else:
                tip_tpl = TEMPLATES_DIR / "tip" / f"{template_id}.html"
                tpl = tip_tpl if tip_tpl.exists() else fallback_tip
                await asyncio.to_thread(
                    create_tip_image,
                    background_path=bg_paths[bg_index],
                    tag=slide.get("tag", "TIP"),
                    body=slide.get("body", ""),
                    output_path=out_path,
                    template_html_path=tpl if tpl.exists() else None,
                    title_bg_color=slide.get("title_bg_color"),
                )
        return out_path

    return list(await asyncio.gather(*(render_slide(i, s) for i, s in enumerate(slides_content))))


def _save_history_entry(keyword: str, content_type: str, num_slides: int, content: Any) -> str:
    from backend.routers.content import _read_history, _write_history

    entry_id = str(uuid.uuid4())
    entry = {
        "id": entry_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "keyword": keyword,
        "content_type": content_type,
        "num_slides": num_slides,
        "custom_prompt": None,
        "content": {
            "intro_title": content.intro_title,
            "intro_body": content.intro_body,
            "tips": [{"tag": t.tag, "body": t.body} for t in content.tips],
            "caption": content.caption,
            "tiktok_description": content.tiktok_description,
            "image_prompts": content.image_prompts,
            "history_id": entry_id,
        },
        "generated_images": [],
    }
    _write_history([entry, *_read_history()])
    return entry_id


async def generate_job_carousel(job: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """Génère le carousel complet pour un job et met à jour son statut."""
    job_id = job["id"]
    topic = job["topic"]
    content_type = job.get("content_type") or config["default_content_type"]
    image_model = config.get("image_model", IMAGE_MODEL_RUNWARE)
    reference_image = resolve_reference_image(config)

    update_job(job_id, status="generating", error=None)
    append_job_log(job_id, "Début génération du carousel", "info")
    append_job_log(job_id, f"Référence selfie: {reference_image}", "info")

    try:
        num_slides = num_slides_for_content_type(content_type)
        append_job_log(job_id, f"Génération contenu Gemini ({content_type}, {num_slides} slides)", "info")
        content = generate_carousel_content(
            keyword=topic,
            num_slides=num_slides,
            content_type=content_type,
            use_cache=False,
            variation_index=0,
        )
        history_id = _save_history_entry(topic, content_type, num_slides, content)
        slides_content = build_slides_content(content)
        prompts = content.image_prompts or []

        if not prompts or not any(p.strip() for p in prompts):
            raise RuntimeError("Aucun prompt image retourné par Gemini")

        append_job_log(job_id, f"Génération de {len(prompts)} image(s) ({image_model})", "info")
        bg_paths = await _generate_images_for_prompts(prompts, image_model, reference_image)

        leafee_idx = leafee_slide_index(content.tips)
        if leafee_idx >= 0 and LEAFEE_IMAGE.is_file():
            shutil.copy(LEAFEE_IMAGE, bg_paths[leafee_idx])

        output_dir = carousel_dir_for_job(job_id)
        for old in output_dir.glob("slide_*.jpg"):
            old.unlink(missing_ok=True)

        append_job_log(job_id, "Rendu des slides (overlay texte)", "info")
        slide_paths = await _render_carousel_slides(slides_content, bg_paths, output_dir)
        append_job_log(job_id, f"Carousel prêt ({len(slide_paths)} slides)", "success")

        return update_job(
            job_id,
            status="ready",
            history_id=history_id,
            carousel_dir=str(output_dir),
            caption=content.caption,
            tiktok_description=content.tiktok_description,
            slide_count=len(slide_paths),
            image_model=image_model,
            text_model="gemini",
            reference_image=reference_image,
            error=None,
        ) or job
    except GeminiConfigError as e:
        append_job_log(job_id, f"Erreur Gemini: {e}", "error")
        update_job(job_id, status="failed", error=str(e))
        raise
    except Exception as e:
        logger.exception("Pipeline failed for job %s: %s", job_id, e)
        append_job_log(job_id, f"Génération échouée: {e}", "error")
        update_job(job_id, status="failed", error=str(e))
        raise
