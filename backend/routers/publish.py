"""Endpoint pour publier sur TikTok via upload-post.com."""

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from upload_post_client import UploadPostConfigError, upload_tiktok_carousel

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/publish")
async def publish_carousel(
    title: str = Form(...),
    description: str = Form(...),
    post_mode: str = Form("DIRECT_POST"),
    upload_post_user: str | None = Form(None),
    images: list[UploadFile] = File(...),
):
    """
    Publie le carousel sur TikTok.
    Les images sont envoyées en multipart/form-data sous le nom 'images'.
    upload_post_user : compte upload-post.com (optionnel, sinon UPLOAD_POST_USER).
    """
    if not images or len(images) == 0:
        raise HTTPException(status_code=400, detail="Aucune image fournie")

    logger.info(
        "Publish request received | post_mode=%s | upload_post_user=%s | images=%s | title_len=%s | desc_len=%s",
        post_mode,
        upload_post_user or "(env default)",
        len(images),
        len(title or ""),
        len(description or ""),
    )
    logger.info("Publish images filenames: %s", [img.filename for img in images])

    with tempfile.TemporaryDirectory() as tmpdir:
        paths = []
        for i, img in enumerate(images):
            ext = ".jpg"
            if img.filename and img.filename.lower().endswith(".png"):
                ext = ".png"
            path = Path(tmpdir) / f"slide_{i:02d}{ext}"
            try:
                content = await img.read()
            except Exception as e:
                logger.exception("Failed to read uploaded image %s (%s): %s", i, img.filename, e)
                raise HTTPException(status_code=400, detail=f"Impossible de lire l'image {i}")
            path.write_bytes(content)
            paths.append(path)
            logger.info(
                "Saved image %s to %s (%s bytes)",
                i,
                path.name,
                len(content),
            )

        try:
            logger.info("Calling upload-post | slides=%s | mode=%s | user=%s", len(paths), post_mode, upload_post_user or "(env default)")
            result = upload_tiktok_carousel(
                image_paths=paths,
                title=title,
                description=description,
                post_mode=post_mode,
                user=upload_post_user if upload_post_user else None,
            )
            logger.info("Publish success | result_type=%s", type(result).__name__)
            return {"success": True, "result": result}
        except UploadPostConfigError as e:
            logger.warning("Publish config error: %s", e)
            raise HTTPException(status_code=503, detail=str(e))
        except Exception as e:
            logger.exception("Publish failed: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
