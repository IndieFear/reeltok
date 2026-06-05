"""Plantes qui aiment l'humidité."""

import json

from backend.content_types.base import get_schema_example, get_common_instructions, get_image_prompts_instruction


def build_prompt(keyword: str, num_slides: int = 6) -> str:
    schema = get_schema_example(
        intro_title="Plantes qui aiment l'humidité",
        intro_body="Salle de bain, cuisine, pièce humide... Certaines plantes adorent ça. Voici les meilleures pour les environnements humides.",
        tips=[
            {"tag": "PLANTE 1", "body": "La plante star des pièces humides : entretien, pourquoi elle adore l'humidité."},
            {"tag": "PLANTE 2", "body": "Deuxième option : une plante tropicale qui se régale dans la vapeur."},
            {"tag": "PLANTE 3", "body": "Troisième idée : une plante facile pour les débutants en milieu humide."},
            {"tag": "LEAFEE", "body": "Leafee m'aide à gérer l'arrosage. Humidité + lumière = chaque plante a ses besoins."},
            {"tag": "TIPS", "body": "Brume ou pas ? Ça dépend de la plante. Pas toutes aiment les feuilles mouillées."},
        ],
        caption="Plantes pour pièces humides 🌿 Salle de bain, cuisine...",
        tiktok_desc="Plantes humidité.\nSalle de bain.\nCuisine.\n3 plantes qui adorent l'humidité.\nLeafee pour un guide perso.\n#humidite #salledebain #houseplants",
        image_prompts=[
            "Fern in bathroom, steam, toothpaste visible, slightly brown fronds, iPhone, no bokeh, humid",
            "Calathea on bathroom shelf, condensation, towel on rack, imperfect leaves, iPhone photo",
            "Pothos trailing in bathroom, shower curtain, natural clutter, iPhone, sharp focus",
            "Fern in corner, humidity droplets, bathroom shelf clutter, iPhone, realistic",
            "Bathroom plant collection, soap bottles, steam, iPhone photo, no bokeh",
            "Orchid on bathroom windowsill, condensation on glass, natural light, iPhone",
        ],
    )
    return (
        "You are a content creator for TikTok & Instagram carousels.\n"
        "Generate a carousel about plants that love humidity.\n\n"
        f"CONTEXT = '{keyword}' (e.g. Salle de bain, Cuisine, Serre). Adapt if relevant.\n\n"
        "CONTEXT: Platforms TikTok & Instagram. Audience: plant lovers. Tone: practical, casual.\n\n"
        + get_common_instructions()
        + "CAROUSEL: 6 slides. Slide 1 = intro. Slides 2-4 = 3 plants that thrive in humid environments. "
        "Slide 5 = Leafee. Slide 6 = tip (misting, etc.).\n\n"
        "Focus on plants that naturally love humidity (tropicals, ferns, etc.).\n"
        + get_image_prompts_instruction()
        + "\nExample structure:\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )
