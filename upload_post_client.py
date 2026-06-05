from __future__ import annotations

import logging
import mimetypes
import os
from pathlib import Path
from typing import Iterable, List, Mapping, Optional

import requests


UPLOAD_PHOTOS_URL = "https://api.upload-post.com/api/upload_photos"
logger = logging.getLogger(__name__)


class UploadPostConfigError(RuntimeError):
    """Erreur de configuration de l'API upload-post.com."""


def _get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise UploadPostConfigError(
            f"Variable d'environnement {name} manquante. "
            f"Ajoute-la dans ton .env ou exporte-la dans ton shell."
        )
    return value


def upload_tiktok_carousel(
    image_paths: Iterable[str | Path],
    title: str,
    description: Optional[str] = None,
    *,
    user: Optional[str] = None,
    api_key: Optional[str] = None,
    privacy_level: str = "PUBLIC_TO_EVERYONE",
    post_mode: str = "DIRECT_POST",
    async_upload: bool = False,
    auto_add_music: bool = True,
    extra_params: Optional[Mapping[str, str]] = None,
) -> dict:
    """
    Upload d'un carrousel de photos sur TikTok via upload-post.com.

    - image_paths : chemins des fichiers images FINALISÉS (avec overlay)
    - title : titre/caption principal
    - description : description détaillée (utilisée comme tiktok_description)
    - auto_add_music : ajout automatique de musique de fond (défaut True)
    """
    image_paths = [Path(p) for p in image_paths]
    if not image_paths:
        raise ValueError("Aucune image à uploader.")

    user = user or _get_env("UPLOAD_POST_USER")
    api_key = api_key or _get_env("UPLOAD_POST_API_KEY")

    headers = {"Authorization": f"Apikey {api_key}"}

    # Préserver les retours à la ligne pour que la description ne s'affiche pas en un seul bloc
    raw_desc = description or title
    if raw_desc and "\n" in raw_desc:
        # Normaliser (LF -> CRLF) pour que TikTok / l'API affichent bien les sauts de ligne
        tiktok_description = raw_desc.replace("\r\n", "\n").replace("\n", "\r\n")
    else:
        tiktok_description = raw_desc

    data = {
        "user": user,
        "platform[]": "tiktok",
        "title": title,
        "tiktok_title": title,
        "tiktok_description": tiktok_description,
        "privacy_level": privacy_level,
        "post_mode": post_mode,
        "async_upload": "true" if async_upload else "false",
        "auto_add_music": "true" if auto_add_music else "false",
    }

    if extra_params:
        data.update(extra_params)

    files: List[tuple] = []
    for path in image_paths:
        if not path.is_file():
            raise FileNotFoundError(f"Image introuvable: {path}")
        mime_type, _ = mimetypes.guess_type(path.name)
        if mime_type is None:
            mime_type = "image/jpeg"
        files.append(("photos[]", (path.name, path.open("rb"), mime_type)))

    try:
        sizes = []
        for p in image_paths:
            try:
                sizes.append(int(Path(p).stat().st_size))
            except Exception:
                sizes.append(-1)
        logger.info(
            "upload-post request | user=%s | post_mode=%s | async=%s | auto_add_music=%s | photos=%s | sizes=%s",
            user,
            post_mode,
            async_upload,
            auto_add_music,
            len(image_paths),
            sizes,
        )
        response = requests.post(UPLOAD_PHOTOS_URL, headers=headers, data=data, files=files, timeout=60)
        logger.info("upload-post response | status=%s | ok=%s", response.status_code, response.ok)
    except Exception as e:
        logger.exception("upload-post request failed: %s", e)
        raise

    # Fermer les fichiers
    for _, (_, fh, _) in files:
        try:
            fh.close()
        except Exception:
            pass

    if not response.ok:
        text = (response.text or "").strip()
        snippet = text[:500] + ("…" if len(text) > 500 else "")
        logger.warning("upload-post error body (snippet): %s", snippet)
        raise RuntimeError(
            f"Erreur upload-post.com: HTTP {response.status_code} - {response.text}"
        )

    try:
        return response.json()
    except ValueError:
        return {"raw": response.text}


__all__ = ["upload_tiktok_carousel", "UploadPostConfigError", "UPLOAD_PHOTOS_URL"]

