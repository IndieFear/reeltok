"""Plante pour quelle pièce."""

import json

from backend.content_types.base import get_schema_example, get_common_instructions, get_image_prompts_instruction


def build_prompt(keyword: str, num_slides: int = 6) -> str:
    schema = get_schema_example(
        intro_title=f"Plantes pour {keyword}",
        intro_body="Pas toutes les plantes vont partout. Voici les plantes qui vont vraiment bien dans une {keyword}.",
        tips=[
            {"tag": "PLANTE 1", "body": "La plante parfaite pour cette pièce : lumière, humidité, entretien."},
            {"tag": "PLANTE 2", "body": "Deuxième option : une plante qui s'adapte aux conditions de la {keyword}."},
            {"tag": "PLANTE 3", "body": "Pour les débutants : la plante la plus facile pour cette pièce."},
            {"tag": "LEAFEE", "body": "Leafee m'a aidé à choisir selon ma pièce. Lumière, humidité, mon rythme = plante idéale."},
            {"tag": "TIPS", "body": "Pense à la taille : une plante trop grande dans une petite pièce, ça étouffe."},
        ],
        caption=f"Plantes pour ta {keyword} 🌿",
        tiktok_desc=f"Plantes pour {keyword}.\nPas toutes les plantes vont partout.\n3 plantes parfaites pour cette pièce.\nLeafee pour un guide perso.\n#{keyword.lower().replace(' ', '')} #houseplants #plantcare",
        image_prompts=[
            "Pothos in bathroom on shelf, steam, toothpaste visible, slightly wilted leaf, iPhone, no bokeh, natural",
            "Fern in bathroom corner, humidity, towel on rack, imperfect fronds, iPhone photo, lived-in",
            "Orchid on bathroom windowsill, condensation on glass, natural light, iPhone, realistic",
            "Pothos trailing in bathroom, shower curtain slightly open, clutter, iPhone, sharp focus",
            "Houseplant in bathroom, soap and bottles visible, natural imperfections, iPhone",
            "Spider plant on bathroom shelf, steam, casual arrangement, iPhone photo, no bokeh",
        ],
    )
    return (
        "You are a content creator for TikTok & Instagram carousels.\n"
        "Generate a carousel about plants for a specific room.\n\n"
        f"ROOM = '{keyword}' (e.g. Salle de bain, Bureau, Cuisine, Chambre, Salon).\n\n"
        "CONTEXT: Platforms TikTok & Instagram. Audience: plant lovers. Tone: practical, casual.\n\n"
        + get_common_instructions()
        + "CAROUSEL: 6 slides. Slide 1 = intro. Slides 2-4 = 3 plants suited for this room (light, humidity, size). "
        "Slide 5 = Leafee. Slide 6 = practical tip.\n\n"
        "Consider light levels, humidity, and space when recommending plants.\n"
        + get_image_prompts_instruction()
        + "\nExample structure:\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )
