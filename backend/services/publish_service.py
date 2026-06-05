"""Publication TikTok depuis des chemins de fichiers locaux."""

from __future__ import annotations

import logging
from pathlib import Path

from upload_post_client import UploadPostConfigError, upload_tiktok_carousel

logger = logging.getLogger(__name__)


def publish_carousel_from_paths(
    image_paths: list[Path],
    title: str,
    description: str,
    *,
    post_mode: str = "DIRECT_POST",
    upload_post_user: str | None = None,
    privacy_level: str = "PUBLIC_TO_EVERYONE",
    auto_add_music: bool = True,
) -> dict:
    """Publie un carousel à partir de fichiers JPEG/PNG sur disque."""
    if not image_paths:
        raise ValueError("Aucune image à publier")
    sorted_paths = sorted(image_paths, key=lambda p: p.name)
    logger.info(
        "Publishing carousel | slides=%s | user=%s | mode=%s",
        len(sorted_paths),
        upload_post_user or "(env default)",
        post_mode,
    )
    return upload_tiktok_carousel(
        image_paths=sorted_paths,
        title=title,
        description=description,
        post_mode=post_mode,
        user=upload_post_user,
        privacy_level=privacy_level,
        auto_add_music=auto_add_music,
    )
