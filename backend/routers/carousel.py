"""Endpoint pour générer les slides du carousel."""

import asyncio
import base64
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from image_overlay import create_intro_image, create_tip_image

ROOT = Path(__file__).resolve().parent.parent.parent

router = APIRouter()
MAX_CONCURRENT_CAROUSEL_RENDERS = max(
    1, int(os.getenv("CAROUSEL_RENDER_CONCURRENCY", "1"))
)


class SlideContent(BaseModel):
    type: str  # "intro" | "tip"
    title: str | None = None
    body: str | None = None
    tag: str | None = None
    template_id: str = "leafee-v2"
    title_bg_color: str | None = None


@router.post("/generate-carousel")
async def generate_carousel_batch(
    slides_content: str = Form(...),
    images: list[UploadFile] = File(...),
):
    """
    Génère les images du carousel.
    slides_content: JSON array de { type, title?, body?, tag?, template_id }
    images: fichiers dans l'ordre (slide 1, 2, 3...)
    """
    import json

    try:
        content_list = json.loads(slides_content)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON invalide: {e}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        bg_paths: list[Path] = []
        for i, img in enumerate(images):
            ext = ".jpg"
            if img.filename and img.filename.lower().endswith(".png"):
                ext = ".png"
            path = tmp / f"bg_{i}{ext}"
            path.write_bytes(await img.read())
            bg_paths.append(path)

        if not bg_paths:
            raise HTTPException(
                status_code=400,
                detail="Au moins une image de fond est requise pour générer le carousel",
            )

        templates_dir = ROOT / "backend" / "templates"
        fallback_intro = templates_dir / "intro" / "leafee-v2.html"
        fallback_tip = templates_dir / "tip" / "leafee-v2.html"
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_CAROUSEL_RENDERS)

        async def render_slide(i: int, slide: dict) -> Path:
            out_path = tmp / f"slide_{i:02d}.jpg"
            slide_type = slide.get("type", "tip")
            if i == 0:
                slide_type = "intro"
            template_id = slide.get("template_id", "leafee-v2")

            bg_index = i if i < len(bg_paths) else len(bg_paths) - 1

            print(
                f"[carousel] Slide {i} type={slide_type} template_id={template_id} "
                f"title_bg_color={slide.get('title_bg_color')}"
            )

            async with semaphore:
                if slide_type == "intro":
                    intro_tpl = templates_dir / "intro" / f"{template_id}.html"
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
                    tip_tpl = templates_dir / "tip" / f"{template_id}.html"
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
            print(f"[carousel] Slide {i} terminée")
            return out_path

        output_paths = await asyncio.gather(
            *(render_slide(i, slide) for i, slide in enumerate(content_list))
        )

        result = []
        for p in output_paths:
            data = p.read_bytes()
            result.append({"base64": base64.b64encode(data).decode(), "filename": p.name})

        return {"slides": result}


def _resolve_template(slide_type: str, template_id: str) -> Path | None:
    """Résout le chemin du template : backend/templates puis fallback par défaut."""
    templates_dir = ROOT / "backend" / "templates"
    fallback_intro = templates_dir / "intro" / "leafee-v2.html"
    fallback_tip = templates_dir / "tip" / "leafee-v2.html"
    if slide_type == "intro":
        tpl = templates_dir / "intro" / f"{template_id}.html"
        return tpl if tpl.exists() else fallback_intro
    else:
        tpl = templates_dir / "tip" / f"{template_id}.html"
        return tpl if tpl.exists() else fallback_tip


@router.post("/preview-slide")
async def preview_slide(
    slide_content: str = Form(...),
    image: UploadFile = File(...),
):
    """
    Prévisualise une slide (intro ou tip).
    Utilise le même template que generate-carousel (template_id + backend/fallback).
    """
    import json

    try:
        content = json.loads(slide_content)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON invalide: {e}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        bg_path = tmp / "bg.jpg"
        bg_path.write_bytes(await image.read())

        out_path = tmp / "preview.jpg"
        slide_type = content.get("type", "tip")
        template_id = content.get("template_id", "leafee-v2")
        tpl = _resolve_template(slide_type, template_id)

        if slide_type == "intro":
            await asyncio.to_thread(
                create_intro_image,
                background_path=bg_path,
                title=content.get("title", "Care Guide"),
                body=content.get("body", ""),
                output_path=out_path,
                template_html_path=tpl,
                title_bg_color=content.get("title_bg_color"),
            )
        else:
            await asyncio.to_thread(
                create_tip_image,
                background_path=bg_path,
                tag=content.get("tag", "TIP"),
                body=content.get("body", ""),
                output_path=out_path,
                template_html_path=tpl,
                title_bg_color=content.get("title_bg_color"),
            )

        data = out_path.read_bytes()
        return {"base64": base64.b64encode(data).decode()}
