"""Génération d'images via Runware ou Replicate - API REST."""

import asyncio
import base64
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)

# Modèle Runware : Flux 2 Klein 9B (runware:400@2)
# Format TikTok portrait : 1088x1920 (divisible par 64)
RUNWARE_MODEL = "runware:400@2"
IMAGE_WIDTH = 1088
IMAGE_HEIGHT = 1920
REPLICATE_ASPECT_RATIO = "2:3"

RUNWARE_API_URL = "https://api.runware.ai/v1"
REPLICATE_GPT_IMAGE_2_MODEL = "openai/gpt-image-2"
REPLICATE_GROK_IMAGE_MODEL = "xai/grok-imagine-image"
REPLICATE_API_URL = f"https://api.replicate.com/v1/models/{REPLICATE_GPT_IMAGE_2_MODEL}/predictions"
REPLICATE_GROK_API_URL = f"https://api.replicate.com/v1/models/{REPLICATE_GROK_IMAGE_MODEL}/predictions"
# Timeout long : Flux 2 Klein peut prendre 1-2 min par image
HTTP_TIMEOUT = 180
MAX_RETRIES = 3
REPLICATE_POLL_SECONDS = 180
MAX_CONCURRENT_IMAGE_GENERATIONS = 6
IMAGE_MODEL_RUNWARE = "runware"
IMAGE_MODEL_REPLICATE_GPT_IMAGE_2 = "replicate-gpt-image-2"
IMAGE_MODEL_REPLICATE_GROK = "replicate-grok-imagine-image"
IMAGE_MODEL_ALIASES = {
    IMAGE_MODEL_RUNWARE: IMAGE_MODEL_RUNWARE,
    "flux-2-klein": IMAGE_MODEL_RUNWARE,
    IMAGE_MODEL_REPLICATE_GPT_IMAGE_2: IMAGE_MODEL_REPLICATE_GPT_IMAGE_2,
    IMAGE_MODEL_REPLICATE_GROK: IMAGE_MODEL_REPLICATE_GROK,
    "replicate": IMAGE_MODEL_REPLICATE_GPT_IMAGE_2,
    "gpt-image-2": IMAGE_MODEL_REPLICATE_GPT_IMAGE_2,
    "openai/gpt-image-2": IMAGE_MODEL_REPLICATE_GPT_IMAGE_2,
    "grok": IMAGE_MODEL_REPLICATE_GROK,
    "grok-imagine": IMAGE_MODEL_REPLICATE_GROK,
    "xai/grok-imagine-image": IMAGE_MODEL_REPLICATE_GROK,
}

ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = ROOT / "assets"
FILLE1_IMAGE = ASSETS_DIR / "fille1.png"


class GenerateImagesRequest(BaseModel):
    prompts: list[str]  # Un prompt par slide (image_prompts de Gemini)
    reference_images: list[str] | None = None  # URLs ou base64 pour la 1ère image (selfie)
    image_model: str = IMAGE_MODEL_RUNWARE
    history_id: str | None = None
    slide_indices: list[int] | None = None


def _normalize_reference_b64(value: str) -> str:
    """Retire le préfixe data:image/...;base64, si présent."""
    s = value.strip()
    if s.startswith("data:") and "," in s:
        return s.split(",", 1)[1].strip()
    return s


def _get_reference_for_first_image(reference_images: list[str] | None) -> list[str] | None:
    """Retourne la liste des images de référence pour la 1ère image (selfie)."""
    if reference_images and len(reference_images) > 0:
        first = reference_images[0]
        # Cas spécial : identifiant interne type "fille1", "fille2", ...
        # On charge alors directement le fichier local correspondant et on renvoie du base64,
        # ce qui évite d'envoyer une URL localhost non accessible à l'API Runware.
        if first.startswith("fille") and "." not in first:
            img_path = ASSETS_DIR / f"{first}.png"
            if img_path.is_file():
                b64 = base64.b64encode(img_path.read_bytes()).decode()
                return [b64]
        # Sinon : URL ou base64 (éventuellement data URL)
        out: list[str] = []
        for r in reference_images:
            s = r.strip()
            if s.startswith("http://") or s.startswith("https://"):
                out.append(s)
            else:
                out.append(_normalize_reference_b64(s))
        return out
    # Fallback : utiliser fille1.png local en base64
    if FILLE1_IMAGE.is_file():
        b64 = base64.b64encode(FILLE1_IMAGE.read_bytes()).decode()
        return [b64]
    return None


def _normalize_image_model(image_model: str | None) -> str:
    value = (image_model or IMAGE_MODEL_RUNWARE).strip()
    normalized = IMAGE_MODEL_ALIASES.get(value)
    if not normalized:
        allowed = ", ".join(sorted({IMAGE_MODEL_RUNWARE, IMAGE_MODEL_REPLICATE_GPT_IMAGE_2, IMAGE_MODEL_REPLICATE_GROK}))
        raise ValueError(f"Modèle image inconnu: {value}. Valeurs possibles: {allowed}")
    return normalized


def _get_replicate_api_key() -> str | None:
    return os.getenv("REPLICATE_API_TOKEN") or os.getenv("REPLICATE_API_KEY")


def _replicate_input_image(value: str) -> str:
    """Replicate attend des URLs ou data URLs pour les fichiers en entrée."""
    s = value.strip()
    if s.startswith("http://") or s.startswith("https://") or s.startswith("data:"):
        return s
    return f"data:image/png;base64,{_normalize_reference_b64(s)}"


def _download_image_as_result(url: str, filename: str) -> dict:
    img_resp = requests.get(url, timeout=60)
    img_resp.raise_for_status()
    b64 = base64.b64encode(img_resp.content).decode()
    content_type = img_resp.headers.get("content-type", "").split(";")[0].strip()
    mime = content_type if content_type.startswith("image/") else "image/jpeg"
    return {
        "base64": b64,
        "filename": filename,
        "mime": mime,
        "source_url": url,
    }


def _read_history() -> list[dict]:
    history_file = ROOT / "data" / "content_history.json"
    if not history_file.is_file():
        return []
    try:
        data = json.loads(history_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def _write_history(items: list[dict]) -> None:
    data_dir = ROOT / "data"
    history_file = data_dir / "content_history.json"
    data_dir.mkdir(parents=True, exist_ok=True)
    tmp = history_file.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(history_file)


def _store_generated_image_urls(history_id: str | None, image_items: list[dict]) -> None:
    if not history_id or not image_items:
        return
    history = _read_history()
    now = datetime.now(timezone.utc).isoformat()
    changed = False
    for entry in history:
        if entry.get("id") != history_id:
            continue
        generated_images = entry.setdefault("generated_images", [])
        for item in image_items:
            source_url = item.get("source_url")
            slide_index = item.get("slide_index")
            if not source_url or slide_index is None:
                continue
            generated_images[:] = [
                existing
                for existing in generated_images
                if existing.get("slide_index") != slide_index
            ]
            generated_images.append(
                {
                    "slide_index": slide_index,
                    "image_model": item.get("image_model") or IMAGE_MODEL_RUNWARE,
                    "source_url": source_url,
                    "filename": item.get("filename"),
                    "mime": item.get("mime"),
                    "generated_at": now,
                }
            )
            changed = True
        break
    if changed:
        _write_history(history)


def _generate_one_runware_image_sync(
    api_key: str,
    prompt: str,
    image_index: int = 0,
    reference_images: list[str] | None = None,
) -> dict | None:
    """Génère une image via l'API REST Runware (sans WebSocket)."""
    task_uuid = str(uuid.uuid4())
    task_payload: dict = {
        "taskType": "imageInference",
        "taskUUID": task_uuid,
        "positivePrompt": prompt.strip(),
        "model": RUNWARE_MODEL,
        "width": IMAGE_WIDTH,
        "height": IMAGE_HEIGHT,
        "outputType": "base64Data",
        "outputFormat": "JPG",
        "numberResults": 1,
    }
    # Pour la 1ère image (selfie), ajouter les images de référence (identité)
    if image_index == 0 and reference_images:
        task_payload["referenceImages"] = reference_images
    payload = [task_payload]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    resp = requests.post(
        RUNWARE_API_URL,
        json=payload,
        headers=headers,
        timeout=HTTP_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()

    if "errors" in data:
        return None

    items = data.get("data", [])
    if not items:
        return None

    item = items[0]
    b64 = item.get("imageBase64Data")
    if b64:
        return {
            "base64": b64,
            "filename": "runware_slide.jpg",
            "mime": "image/jpeg",
            "source_url": item.get("imageURL"),
        }
    # Fallback : télécharger depuis l'URL
    url = item.get("imageURL")
    if url:
        return _download_image_as_result(url, "runware_slide.jpg")
    return None


def _generate_one_replicate_image_sync(
    api_key: str,
    prompt: str,
    image_index: int = 0,
    reference_images: list[str] | None = None,
) -> dict | None:
    """Génère une image via Replicate openai/gpt-image-2."""
    input_payload: dict = {
        "prompt": prompt.strip(),
        "aspect_ratio": REPLICATE_ASPECT_RATIO,
        "quality": "low",
        "background": "auto",
        "moderation": "low",
        "output_format": "jpeg",
        "number_of_images": 1,
        "output_compression": 90,
    }
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        input_payload["openai_api_key"] = openai_api_key
    if image_index == 0 and reference_images:
        input_payload["input_images"] = [_replicate_input_image(r) for r in reference_images]

    output = _create_replicate_prediction(api_key, REPLICATE_API_URL, input_payload)
    if isinstance(output, list) and output:
        result = _download_image_as_result(output[0], "replicate_gpt_image_2_slide.jpeg")
        result["image_model"] = IMAGE_MODEL_REPLICATE_GPT_IMAGE_2
        return result
    if isinstance(output, str):
        result = _download_image_as_result(output, "replicate_gpt_image_2_slide.jpeg")
        result["image_model"] = IMAGE_MODEL_REPLICATE_GPT_IMAGE_2
        return result
    return None


def _create_replicate_prediction(api_key: str, api_url: str, input_payload: dict):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Prefer": "wait=60",
    }
    resp = requests.post(
        api_url,
        json={"input": input_payload},
        headers=headers,
        timeout=HTTP_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()

    start = time.monotonic()
    while data.get("status") not in {"succeeded", "failed", "canceled"}:
        if time.monotonic() - start >= REPLICATE_POLL_SECONDS:
            logger.warning("Replicate timeout | api_url=%s", api_url)
            return None
        get_url = data.get("urls", {}).get("get")
        if not get_url:
            logger.warning("Replicate polling URL absente | api_url=%s | data=%s", api_url, data)
            return None
        time.sleep(2)
        poll_resp = requests.get(get_url, headers=headers, timeout=HTTP_TIMEOUT)
        poll_resp.raise_for_status()
        data = poll_resp.json()

    if data.get("status") != "succeeded":
        logger.warning(
            "Replicate prediction non réussie | api_url=%s | status=%s | error=%s",
            api_url,
            data.get("status"),
            data.get("error"),
        )
        return None

    return data.get("output")


def _generate_one_grok_image_sync(
    api_key: str,
    prompt: str,
    image_index: int = 0,
    reference_images: list[str] | None = None,
) -> dict | None:
    """Fallback via Replicate xai/grok-imagine-image."""
    input_payload: dict = {
        "prompt": prompt.strip(),
        "aspect_ratio": REPLICATE_ASPECT_RATIO,
    }
    if image_index == 0 and reference_images:
        input_payload["image"] = _replicate_input_image(reference_images[0])

    output = _create_replicate_prediction(api_key, REPLICATE_GROK_API_URL, input_payload)
    if isinstance(output, list) and output:
        result = _download_image_as_result(output[0], "replicate_grok_imagine_slide.jpg")
        result["image_model"] = "replicate-grok-imagine-image"
        result["fallback_model"] = REPLICATE_GROK_IMAGE_MODEL
        return result
    if isinstance(output, str):
        result = _download_image_as_result(output, "replicate_grok_imagine_slide.jpg")
        result["image_model"] = "replicate-grok-imagine-image"
        result["fallback_model"] = REPLICATE_GROK_IMAGE_MODEL
        return result
    return None


def _try_grok_fallback_sync(
    prompt: str,
    image_index: int = 0,
    reference_images: list[str] | None = None,
    reason: str | None = None,
) -> dict | None:
    fallback_api_key = _get_replicate_api_key()
    if not fallback_api_key:
        logger.warning("Fallback Grok impossible: REPLICATE_API_TOKEN manquant")
        return None

    logger.warning(
        "Fallback Grok lancé pour image_index=%s | raison=%s",
        image_index,
        reason or "Génération primaire échouée",
    )
    result = _generate_one_grok_image_sync(
        fallback_api_key,
        prompt,
        image_index=image_index,
        reference_images=reference_images,
    )
    if result:
        result["fallback_reason"] = reason or "Génération primaire échouée"
        logger.info("Fallback Grok réussi pour image_index=%s", image_index)
        return result

    logger.warning("Fallback Grok sans résultat pour image_index=%s", image_index)
    return None


def _generate_one_image_sync(
    api_key: str,
    prompt: str,
    image_model: str,
    image_index: int = 0,
    reference_images: list[str] | None = None,
) -> dict | None:
    if image_model == IMAGE_MODEL_REPLICATE_GPT_IMAGE_2:
        return _generate_one_replicate_image_sync(api_key, prompt, image_index, reference_images)
    if image_model == IMAGE_MODEL_REPLICATE_GROK:
        return _generate_one_grok_image_sync(api_key, prompt, image_index, reference_images)
    return _generate_one_runware_image_sync(api_key, prompt, image_index, reference_images)


@router.post("/generate-images-from-prompts")
async def generate_images_from_prompts(request: GenerateImagesRequest):
    """
    Génère des images via le modèle choisi à partir des prompts (API REST).
    Un prompt = une image. Retourne les images en base64.
    Pour la 1ère image (selfie), utilise reference_images si fourni, sinon assets/fille1.png.
    """
    if not request.prompts:
        raise HTTPException(status_code=400, detail="Liste de prompts requise")

    try:
        image_model = _normalize_image_model(request.image_model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    uses_replicate = image_model in {IMAGE_MODEL_REPLICATE_GPT_IMAGE_2, IMAGE_MODEL_REPLICATE_GROK}
    api_key_name = "REPLICATE_API_TOKEN" if uses_replicate else "RUNWARE_API_KEY"
    api_key = _get_replicate_api_key() if uses_replicate else os.getenv(api_key_name)
    if not api_key and uses_replicate:
        api_key_name = "REPLICATE_API_TOKEN"
    fallback_api_key = _get_replicate_api_key()
    if not api_key and not fallback_api_key:
        raise HTTPException(
            status_code=503,
            detail=f"Variable d'environnement {api_key_name} manquante, et fallback Grok impossible sans REPLICATE_API_TOKEN.",
        )

    # Images de référence pour la 1ère image (selfie) : URLs ou base64
    ref_images = _get_reference_for_first_image(request.reference_images)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_IMAGE_GENERATIONS)

    async def generate_one(i: int, prompt: str):
        if not prompt.strip():
            return {"base64": "", "filename": "", "mime": "", "error": "Prompt vide"}

        async with semaphore:
            last_error = None
            if api_key:
                for attempt in range(MAX_RETRIES):
                    try:
                        result = await asyncio.to_thread(
                            _generate_one_image_sync,
                            api_key,
                            prompt,
                            image_model,
                            image_index=i,
                            reference_images=ref_images if i == 0 else None,
                        )
                        if result:
                            return result
                        last_error = "Génération échouée (aucune image retournée)"
                    except requests.RequestException as e:
                        last_error = str(e)
                        if attempt < MAX_RETRIES - 1:
                            await asyncio.sleep(2 * (attempt + 1))
                    except Exception as e:
                        last_error = str(e)
                        break
            else:
                last_error = f"{api_key_name} manquante"

            try:
                result = await asyncio.to_thread(
                    _try_grok_fallback_sync,
                    prompt,
                    image_index=i,
                    reference_images=ref_images if i == 0 else None,
                    reason=last_error,
                )
                if result:
                    return result
            except requests.RequestException as e:
                last_error = f"{last_error or 'Génération primaire échouée'}; fallback Grok échoué: {e}"
            except Exception as e:
                last_error = f"{last_error or 'Génération primaire échouée'}; fallback Grok échoué: {e}"

        return {"base64": "", "filename": "", "mime": "", "error": last_error or "Génération échouée"}

    results = await asyncio.gather(
        *(generate_one(i, prompt) for i, prompt in enumerate(request.prompts))
    )

    _store_generated_image_urls(
        request.history_id,
        [
            {
                **result,
                "slide_index": request.slide_indices[i] if request.slide_indices and i < len(request.slide_indices) else i,
                "image_model": result.get("image_model") or image_model,
            }
            for i, result in enumerate(results)
            if result.get("source_url")
        ],
    )

    return {"images": results}


class GenerateSingleImageRequest(BaseModel):
    prompt: str
    index: int  # 0-5, pour savoir si on utilise reference_images (index 0)
    reference_images: list[str] | None = None
    image_model: str = IMAGE_MODEL_RUNWARE
    history_id: str | None = None


@router.post("/generate-single-image")
async def generate_single_image(request: GenerateSingleImageRequest):
    """
    Génère une seule image via le modèle choisi.
    Pour index 0 (selfie), utilise reference_images si fourni, sinon assets/fille1.png.
    """
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt requis")

    try:
        image_model = _normalize_image_model(request.image_model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    uses_replicate = image_model in {IMAGE_MODEL_REPLICATE_GPT_IMAGE_2, IMAGE_MODEL_REPLICATE_GROK}
    api_key_name = "REPLICATE_API_TOKEN" if uses_replicate else "RUNWARE_API_KEY"
    api_key = _get_replicate_api_key() if uses_replicate else os.getenv(api_key_name)
    if not api_key and uses_replicate:
        api_key_name = "REPLICATE_API_TOKEN"
    fallback_api_key = _get_replicate_api_key()
    if not api_key and not fallback_api_key:
        raise HTTPException(
            status_code=503,
            detail=f"Variable d'environnement {api_key_name} manquante, et fallback Grok impossible sans REPLICATE_API_TOKEN.",
        )

    ref_images = _get_reference_for_first_image(request.reference_images) if request.index == 0 else None

    last_error = None
    if api_key:
        for attempt in range(MAX_RETRIES):
            try:
                result = await asyncio.to_thread(
                    _generate_one_image_sync,
                    api_key,
                    request.prompt,
                    image_model,
                    image_index=request.index,
                    reference_images=ref_images,
                )
                if result:
                    _store_generated_image_urls(
                        request.history_id,
                        [
                            {
                                **result,
                                "slide_index": request.index,
                                "image_model": result.get("image_model") or image_model,
                            }
                        ],
                    )
                    return result
                last_error = "Génération échouée"
            except requests.RequestException as e:
                last_error = str(e)
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(2 * (attempt + 1))
            except Exception as e:
                last_error = str(e)
                break
    else:
        last_error = f"{api_key_name} manquante"

    try:
        result = await asyncio.to_thread(
            _try_grok_fallback_sync,
            request.prompt,
            image_index=request.index,
            reference_images=ref_images,
            reason=last_error,
        )
        if result:
            _store_generated_image_urls(
                request.history_id,
                [
                    {
                        **result,
                        "slide_index": request.index,
                        "image_model": result.get("image_model") or "replicate-grok-imagine-image",
                    }
                ],
            )
            return result
    except requests.RequestException as e:
        last_error = f"{last_error or 'Génération primaire échouée'}; fallback Grok échoué: {e}"
    except Exception as e:
        last_error = f"{last_error or 'Génération primaire échouée'}; fallback Grok échoué: {e}"

    raise HTTPException(status_code=500, detail=last_error or "Génération échouée")
