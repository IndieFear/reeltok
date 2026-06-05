"""Bibliothèque d'images utilisateur — upload, liste, preview, suppression."""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from backend.services.user_image_library import (
    add_image,
    delete_image,
    get_image_meta,
    get_image_path,
    list_images,
)

router = APIRouter()


@router.get("/user-images")
def list_user_images():
    return {"images": list_images()}


@router.post("/user-images")
async def upload_user_image(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nom de fichier requis")
    content = await file.read()
    try:
        meta = add_image(content, file.filename, file.content_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return meta


@router.get("/user-images/{image_id}")
def get_user_image(image_id: str):
    meta = get_image_meta(image_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Image introuvable")
    path = get_image_path(image_id)
    if not path:
        raise HTTPException(status_code=404, detail="Image introuvable")
    return FileResponse(path, media_type=meta.get("mime") or "image/jpeg")


@router.delete("/user-images/{image_id}")
def remove_user_image(image_id: str):
    if not delete_image(image_id):
        raise HTTPException(status_code=404, detail="Image introuvable")
    return {"ok": True}
