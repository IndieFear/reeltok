"""Plantes Gen Z / Boomer / Millennial."""

import json

from backend.content_types.base import get_schema_example, get_common_instructions, get_image_prompts_instruction


def build_prompt(keyword: str, num_slides: int = 6) -> str:
    schema = get_schema_example(
        intro_title=f"Plantes {keyword}",
        intro_body="Chaque génération a sa vibe. Et ses plantes. Voici les plantes qui matchent avec les {keyword}s.",
        tips=[
            {"tag": "PLANTE 1", "body": "La plante iconique de ta génération : pourquoi elle colle parfaitement."},
            {"tag": "PLANTE 2", "body": "Deuxième must-have : celle qu'on voit partout sur le feed des {keyword}s."},
            {"tag": "PLANTE 3", "body": "La plante underrated que les {keyword}s adoptent en premier."},
            {"tag": "LEAFEE", "body": "Leafee m'a aidé à trouver la mienne. Mon style, mon espace, mon niveau = une plante qui me ressemble."},
            {"tag": "TRUTH", "body": "Chaque génération a sa vibe. Et ses plantes. C'est normal."},
        ],
        caption=f"Plantes {keyword} 🌿 Sauve ça.",
        tiktok_desc=f"Plantes {keyword}.\nChaque génération a sa vibe.\nEt ses plantes.\nDécouvre les 3 must-have.\nLeafee pour un guide perso.\n#{keyword.lower().replace(' ', '')} #plantcare #houseplants",
        image_prompts=[
            "Monstera on IKEA shelf, vinyl records visible, slightly dusty leaves, student apartment vibe, iPhone, no bokeh",
            "Pothos in macrame hanger, boho room, wrinkled bedding, natural light, imperfections, iPhone photo",
            "ZZ plant in black pot, minimalist desk, cable visible, one yellow leaf, iPhone, sharp focus",
            "Monstera in corner, plants and clutter, lived-in Gen Z room, iPhone, realistic",
            "Houseplant collection, messy shelf, coffee cups, natural imperfections, iPhone",
            "Snake plant by window, dust on leaves, casual interior, iPhone photo, no bokeh",
        ],
    )
    return (
        "You are a content creator for TikTok & Instagram carousels.\n"
        "Generate a carousel about plants that match a generation (Gen Z, Millennial, Boomer).\n\n"
        f"GENERATION = '{keyword}'.\n\n"
        "CONTEXT: Platforms TikTok & Instagram. Audience: plant lovers. Tone: fun, relatable, slightly ironic.\n\n"
        + get_common_instructions()
        + "CAROUSEL: 6 slides. Slide 1 = intro. Slides 2-4 = 3 plants that match this generation's vibe. "
        "Slide 5 = Leafee. Slide 6 = truth/mindset.\n\n"
        "Be specific about why each plant matches the generation (aesthetics, trends, lifestyle).\n"
        + get_image_prompts_instruction()
        + "\nExample structure:\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )
