"""Endpoint pour lister les templates disponibles."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = ROOT / "backend" / "templates"
LEAFEE_IMAGE = ROOT / "assets" / "leafee.jpg"
ASSETS_DIR = ROOT / "assets"

router = APIRouter()


def get_girls_images() -> list[dict]:
    """Retourne la liste des images de filles disponibles dans assets/."""
    images = []
    for i in range(1, 10):  # Support fille1.png à fille9.png
        img_path = ASSETS_DIR / f"fille{i}.png"
        if img_path.is_file():
            images.append({
                "id": f"fille{i}",
                "filename": f"fille{i}.png",
                "url": f"/api/fille-image/fille{i}",
            })
    return images


@router.get("/girls-images")
def list_girls_images():
    """Retourne la liste des images de filles disponibles."""
    return {"images": get_girls_images()}


@router.get("/fille-image/{image_id}")
def get_fille_image(image_id: str):
    """Retourne une image de fille spécifique par son ID (ex: fille1, fille2, fille3)."""
    # Valider que l'image existe
    valid_ids = [img["id"] for img in get_girls_images()]
    if image_id not in valid_ids:
        raise HTTPException(status_code=404, detail=f"Image {image_id} introuvable")

    image_path = ASSETS_DIR / f"{image_id}.png"
    if not image_path.is_file():
        raise HTTPException(status_code=404, detail=f"Image {image_id}.png introuvable")

    return FileResponse(image_path, media_type="image/png")


@router.get("/leafee-image")
def get_leafee_image():
    """Retourne l'image Leafee (slide 4) depuis assets/leafee.jpg."""
    if not LEAFEE_IMAGE.is_file():
        raise HTTPException(status_code=404, detail="Image Leafee introuvable (assets/leafee.jpg)")
    return FileResponse(LEAFEE_IMAGE, media_type="image/jpeg")


@router.get("/templates")
def list_templates():
    """Retourne la liste des templates disponibles (intro et tip)."""
    templates_json = TEMPLATES_DIR / "templates.json"
    if not templates_json.exists():
        return {"intro": [], "tip": []}

    import json
    with templates_json.open(encoding="utf-8") as f:
        return json.load(f)
