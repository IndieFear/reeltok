"""Base pour les prompts de types de contenu."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parent.parent
PROMPT_OVERRIDES_PATH = ROOT.parent / "data" / "prompt_overrides.json"


def get_schema_example(
    intro_title: str,
    intro_body: str,
    tips: list[dict],
    caption: str,
    tiktok_desc: str,
    image_prompts: list[str] | None = None,
) -> dict:
    """Exemple de schéma JSON pour Gemini."""
    d = {
        "intro_title": intro_title,
        "intro_body": intro_body,
        "tips": tips,
        "caption": caption,
        "tiktok_description": tiktok_desc,
    }
    if image_prompts is not None:
        d["image_prompts"] = image_prompts
    return d


def get_common_instructions() -> str:
    """Instructions communes à tous les types de contenu."""
    return (
        "OUTPUT FORMAT (STRICT - CRITICAL)\n"
        "You MUST return ONLY valid JSON. Do NOT use markdown code blocks (no ```json or ```).\n"
        "Do NOT add any text before or after the JSON.\n"
        "Start your response directly with { and end with }.\n"
        "Use EXACTLY the structure with keys: intro_title, intro_body, tips, caption, tiktok_description, image_prompts.\n\n"
        "MEANING OF FIELDS\n"
        "- intro_title: very short title for slide 1 (orange bar). Must be in English.\n"
        "- intro_body: 1–2 short sentences for slide 1 (white box).\n"
        "- tips: array of 5 objects. Each has 'tag' (short UPPERCASE label) and 'body' (text for the slide, 1-2 short sentences max, no newlines).\n"
        "- caption: post caption for TikTok. MAX 90 characters (TikTok limit). Short, punchy.\n"
        "- tiktok_description: long SEO description, one short phrase per line (\\n). End with 4-5 hashtags.\n"
        "- image_prompts: array of 6 strings. One ULTRA-DETAILED image generation prompt per slide for Midjourney/DALL-E. "
        "Each prompt must describe a REALISTIC photo: taken with iPhone, no bokeh (sharp focus), natural lighting, "
        "very natural and authentic feel (lived-in but tidy, everyday objects, soft textures, casual arrangement). "
        "Describe the plant, the setting, the mood. 2-4 sentences per prompt. In English.\n\n"
        "TONE\n"
        "- Natural English, like a real person wrote it. Not robotic or templated.\n"
        "- Ultra casual, human, scroll-stopping\n"
        "- Short sentences, contractions\n"
        "- No emojis\n"
        "- Never educational or corporate\n"
        "- Must feel 100% native to social media\n"
    )


def get_image_prompts_instruction() -> str:
    """Instruction détaillée pour les prompts d'image Midjourney."""
    return (
        "IMAGE_PROMPTS (image_prompts) — CRITICAL FOR MIDJOURNEY\n"
        "Generate 6 ultra-detailed image prompts, one per slide. Each prompt describes a photo to generate via Midjourney.\n\n"
        "SLIDE 1 (image_prompts[0]) — MANDATORY SELFIE FORMAT:\n"
        "Use this structure: \"selfie of a girl. behind her a [PLANT] [SCENE]. "
        "iPhone photo, sharp focus, no bokeh, natural and lived-in. high skin texture detail.\"\n"
        "- [PLANT]: the specific plant (e.g. 'Large Zamioculcas zamiifolia (ZZ plant) in a terracotta pot', "
        "'Monstera deliciosa in a white ceramic pot', 'Pothos golden in a macrame hanger'). Must be visible behind the girl.\n"
        "- [SCENE]: VARY the setting every time. Do NOT repeat the same scene. Examples of different scenes:\n"
        "  • Living room: hardwood floor, cognac leather chair, morning light, glasses on side table\n"
        "  • Bedroom: plant on nightstand, rumpled linen, soft golden hour through curtains\n"
        "  • Kitchen: plant on counter near coffee machine, tile backsplash, breakfast vibe\n"
        "  • Bathroom: plant on shelf above sink, soft steam, towel on rack, natural light\n"
        "  • Balcony/terrace: plant on small table, city view or plants in background, afternoon light\n"
        "  • Desk/office: plant next to laptop, books, mug, desk lamp, cozy work-from-home\n"
        "  • Reading nook: armchair, plant on floor or shelf, blanket, book stack\n"
        "  • Entryway: plant on console table, keys, mail, coat hook visible\n"
        "Vary the room, furniture, lighting (morning/golden hour/overcast), and small details (mug, book, glasses, etc.).\n"
        "HANDS — CRITICAL: If hands are visible, show ONLY ONE hand, as if the person took the photo themselves.\n\n"
        "REQUIREMENTS for slides 2-6 (and any prompt with hands):\n"
        "- HANDS: if hands appear (e.g. holding plant, watering), show ONLY ONE hand, as if the person took the photo themselves\n"
        "- REALISTIC: looks like a real photograph, not a render or illustration\n"
        "- IPHONE QUALITY: shot with smartphone, natural grain, no professional studio look\n"
        "- NO BOKEH: sharp focus, no shallow depth of field, everything in focus\n"
        "- NATURAL: natural lighting (window light, overcast, golden hour), no flash\n"
        "- VERY NATURAL & AUTHENTIC: lived-in but tidy, casual arrangement, soft textures, everyday objects (coffee mug, "
        "book, plant slightly off-center). Not messy or dirty — just genuine, warm, real-life feel\n"
        "- Describe: the plant (species, size, pot color), the setting (windowsill, desk, bathroom), "
        "the mood (cozy, casual, morning light)\n"
        "- 2-4 sentences per prompt. In English. Be specific.\n"
        "Example for slides 2-6: \"Monstera deliciosa in terracotta pot on wooden windowsill, morning light, "
        "coffee mug nearby, lived-in but tidy room, iPhone photo, sharp focus, no bokeh\"\n"
    )


@lru_cache(maxsize=1)
def _load_prompt_overrides() -> Dict[str, Dict[str, Any]]:
    """
    Charge le fichier JSON des overrides de prompts (éditables depuis le dashboard).
    Structure attendue :
    {
      "care-guide": {"extra_instructions": "..."},
      "decor": {"extra_instructions": "..."},
      ...
    }
    """
    if not PROMPT_OVERRIDES_PATH.is_file():
        return {}
    try:
        with PROMPT_OVERRIDES_PATH.open(encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            # on force les clés en str -> dict
            return {str(k): (v if isinstance(v, dict) else {}) for k, v in data.items()}
    except Exception:
        # En cas de JSON corrompu, on ignore les overrides
        return {}
    return {}


def get_extra_instructions(content_type_id: str) -> str:
    """
    Retourne les instructions additionnelles (texte libre) pour un type de contenu.
    Ce texte est éditable depuis le dashboard et sera concaténé au prompt Gemini.
    """
    overrides = _load_prompt_overrides()
    entry = overrides.get(content_type_id) or {}
    extra = entry.get("extra_instructions") or ""
    return str(extra) if isinstance(extra, str) else ""


def get_full_prompt_template(content_type_id: str) -> str | None:
    """
    Retourne un template complet de prompt (si défini) pour un type de contenu.
    Si présent, ce template remplace entièrement le prompt par défaut.

    Le template peut utiliser des placeholders Python .format comme :
      {keyword}  -> le mot-clé saisi dans le dashboard
      {num_slides} -> le nombre de slides demandé
    """
    overrides = _load_prompt_overrides()
    entry = overrides.get(content_type_id) or {}
    value = entry.get("full_prompt")
    if not value:
        return None
    return str(value)
