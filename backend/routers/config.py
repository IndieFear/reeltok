"""Endpoints de configuration éditables depuis le dashboard (prompts, etc.)."""

from pathlib import Path
from typing import Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.content_types.base import PROMPT_OVERRIDES_PATH, _load_prompt_overrides  # type: ignore[attr-defined]


router = APIRouter()


class PromptOverrideModel(BaseModel):
  extra_instructions: str = ""
  full_prompt: str | None = None


class PromptOverridesPayload(BaseModel):
  overrides: Dict[str, PromptOverrideModel]


@router.get("/prompt-config", response_model=PromptOverridesPayload)
def get_prompt_config() -> PromptOverridesPayload:
  """Retourne les overrides de prompts actuels pour chaque type de contenu."""
  data = _load_prompt_overrides()
  # Normaliser les données vers le modèle Pydantic
  overrides: Dict[str, PromptOverrideModel] = {}
  for key, raw in data.items():
      if not isinstance(raw, dict):
          continue
      overrides[key] = PromptOverrideModel(
          extra_instructions=str(raw.get("extra_instructions") or ""),
          full_prompt=str(raw.get("full_prompt")) if raw.get("full_prompt") is not None else None,
      )
  return PromptOverridesPayload(overrides=overrides)


@router.post("/prompt-config", response_model=PromptOverridesPayload)
def save_prompt_config(payload: PromptOverridesPayload) -> PromptOverridesPayload:
  """
  Sauvegarde les overrides de prompts.
  Le fichier JSON est stocké dans data/prompt_overrides.json à la racine du projet.
  """
  # S'assurer que le dossier existe
  path: Path = PROMPT_OVERRIDES_PATH
  path.parent.mkdir(parents=True, exist_ok=True)

  data = {
      key: {
          "extra_instructions": value.extra_instructions,
          **({"full_prompt": value.full_prompt} if value.full_prompt is not None else {}),
      }
      for key, value in payload.overrides.items()
  }

  try:
      path.write_text(
          __import__("json").dumps(data, ensure_ascii=False, indent=2),
          encoding="utf-8",
      )
  except Exception as exc:  # pragma: no cover - protection runtime
      raise HTTPException(status_code=500, detail=f"Impossible de sauvegarder la config: {exc}")

  # Invalider le cache pour prendre en compte la nouvelle config
  try:
      _load_prompt_overrides.cache_clear()  # type: ignore[attr-defined]
  except Exception:
      # Si jamais le cache n'existe pas, on ignore silencieusement
      pass

  return payload

