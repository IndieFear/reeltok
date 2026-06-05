"""Registre des types de contenu et construction des prompts."""

import importlib

from backend.content_types.base import get_extra_instructions, get_full_prompt_template


_CONTENT_TYPES: list[dict] = [
    {"id": "care-guide", "name": "Guide d'entretien", "keyword_placeholder": "Plante (ex: Monstera)", "description": "Guide de soins pour une plante", "module_name": "backend.content_types.care_guide"},
    {"id": "hooks", "name": "Hooks viraux (problèmes de plantes)", "keyword_placeholder": "Problème (ex: plante qui meurt, feuilles jaunes)", "description": "Carousels basés sur des hooks viraux autour des plantes qui meurent, erreurs fréquentes, etc.", "module_name": "backend.content_types.hooks"},
    {"id": "astrology", "name": "Plantes selon signe astrologique", "keyword_placeholder": "Signe (ex: Bélier, Scorpion)", "description": "Plantes qui correspondent à chaque signe du zodiaque", "module_name": "backend.content_types.astrology"},
    {"id": "demographic", "name": "Plantes Gen Z / Boomer / Millennial", "keyword_placeholder": "Génération (ex: Gen Z, Millennial)", "description": "Plantes qui matchent avec chaque génération", "module_name": "backend.content_types.demographic"},
    {"id": "decor", "name": "Plante selon ta déco", "keyword_placeholder": "Style (ex: Mid century, Moderne)", "description": "Quelle plante pour quel style de déco", "module_name": "backend.content_types.decor"},
    {"id": "room", "name": "Plante pour quelle pièce", "keyword_placeholder": "Pièce (ex: Salle de bain, Bureau)", "description": "Plantes adaptées à chaque pièce de la maison", "module_name": "backend.content_types.room"},
    {"id": "gift", "name": "Idées cadeau plant lover", "keyword_placeholder": "Occasion (ex: Anniversaire, Housewarming)", "description": "Cadeaux pour les amoureux des plantes", "module_name": "backend.content_types.gift"},
    {"id": "valentine", "name": "Plantes Saint-Valentin", "keyword_placeholder": "Thème (ex: Romantique)", "description": "Plantes à offrir pour la Saint-Valentin", "module_name": "backend.content_types.valentine"},
    {"id": "birthday", "name": "Plantes for him/her anniversaire", "keyword_placeholder": "Pour qui (ex: Lui, Elle)", "description": "Plantes à offrir pour un anniversaire", "module_name": "backend.content_types.birthday"},
    {"id": "accessories", "name": "Vases, pots, arrosoirs", "keyword_placeholder": "Type (ex: Vase, Pot céramique)", "description": "Idées de vases, pots et arrosoirs", "module_name": "backend.content_types.accessories"},
    {"id": "humidity", "name": "Plantes qui aiment l'humidité", "keyword_placeholder": "Pièce (ex: Salle de bain)", "description": "Plantes pour les environnements humides", "module_name": "backend.content_types.humidity"},
    {"id": "couple-zodiac", "name": "Combo couple = une plante", "keyword_placeholder": "Mois (ex: novembre janvier)", "description": "Mois de naissance du couple = plante idéale (ex: lui nov, elle jan = Monstera)", "module_name": "backend.content_types.couple_zodiac"},
    {"id": "top-x", "name": "Top 5 par catégorie", "keyword_placeholder": "Catégorie (ex: plantes roses, plantes pour la chambre)", "description": "Top 5 plantes selon une catégorie (roses, humidité, chambre, faciles, bureau...)", "module_name": "backend.content_types.top_x"},
    {"id": "top-signs", "name": "Top 5 signes / symptômes", "keyword_placeholder": "Problème (ex: you’re overwatering your plant)", "description": "Top 5 signes classés du #5 au #1, avec une slide Leafee au milieu", "module_name": "backend.content_types.top_signs"},
    {"id": "before-after", "name": "Avant / Après", "keyword_placeholder": "Plante (ex: Monstera, Pothos)", "description": "Transformation avant/après — plante en difficulté vs plante qui reprend", "module_name": "backend.content_types.before_after"},
]


def list_content_types() -> list[dict]:
    """Retourne la liste des types de contenu disponibles."""
    return [
        {
            "id": ct["id"],
            "name": ct["name"],
            "keyword_placeholder": ct["keyword_placeholder"],
            "description": ct["description"],
        }
        for ct in _CONTENT_TYPES
    ]


def get_content_type(content_type_id: str) -> dict | None:
    """Retourne les infos d'un type de contenu par son id."""
    for ct in _CONTENT_TYPES:
        if ct["id"] == content_type_id:
            return {
                "id": ct["id"],
                "name": ct["name"],
                "keyword_placeholder": ct["keyword_placeholder"],
                "description": ct["description"],
            }
    return None


def build_prompt_for_type(
    content_type_id: str, keyword: str, num_slides: int = 6, variation_index: int = 0
) -> str:
    """Construit le prompt Gemini pour un type de contenu donné."""

    # 1. Si un template complet est défini pour ce type, on l'utilise en priorité.
    full_template = get_full_prompt_template(content_type_id)
    if full_template and full_template.strip():
        try:
            prompt = full_template.format(keyword=keyword, num_slides=num_slides)
        except Exception:
            # En cas d'erreur de format (placeholder manquant), on tombe sur le prompt par défaut
            prompt = ""
    else:
        prompt = ""

    # 2. Sinon, on retombe sur le prompt par défaut du content_type.
    if not prompt:
        for ct in _CONTENT_TYPES:
            if ct["id"] == content_type_id:
                mod = importlib.import_module(ct["module_name"])
                prompt = mod.build_prompt(keyword=keyword, num_slides=num_slides)
                break
        else:
            # Fallback : care-guide
            mod = importlib.import_module("backend.content_types.care_guide")
            prompt = mod.build_prompt(keyword=keyword, num_slides=num_slides)

    # Appliquer les overrides de prompts (texte libre éditable depuis le dashboard)
    extra = get_extra_instructions(content_type_id)
    if extra.strip():
        prompt += (
            "\n\nADDITIONAL CUSTOM INSTRUCTIONS (HIGH PRIORITY)\n"
            f"{extra.strip()}\n"
        )

    if variation_index > 0:
        prompt += (
            f"\n\nVARIATION #{variation_index} — CRITICAL\n"
            "Create a DISTINCTLY DIFFERENT version of this content.\n"
            "- Use different wording, different phrasing, different sentence structures.\n"
            "- The tips can have different emphasis or order of ideas.\n"
            "- The caption and tiktok_description MUST be different (not copy-paste).\n"
            "- The image_prompts must describe different compositions, angles, or settings.\n"
            "- Same plant/topic, same structure (6 slides), but unique content.\n"
        )
    return prompt
