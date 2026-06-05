"""Plantes Saint-Valentin."""

import json

from backend.content_types.base import get_schema_example, get_common_instructions, get_image_prompts_instruction


def build_prompt(keyword: str, num_slides: int = 6) -> str:
    schema = get_schema_example(
        intro_title="Plantes Saint-Valentin",
        intro_body="Fleurs coupées, c'est joli 3 jours. Une plante, c'est pour la vie. Voici les plantes à offrir pour la Saint-Valentin.",
        tips=[
            {"tag": "PLANTE 1", "body": "La plante romantique par excellence : symbole, entretien, pourquoi c'est parfait."},
            {"tag": "PLANTE 2", "body": "Deuxième option : une plante qui dit je t'aime sans cliché."},
            {"tag": "PLANTE 3", "body": "Pour les couples : une plante à entretenir ensemble."},
            {"tag": "LEAFEE", "body": "Offre Leafee en plus : un guide perso pour leur nouvelle plante. Cadeau qui dure."},
            {"tag": "TIPS", "body": "Évite les plantes trop fragiles si c'est leur première."},
        ],
        caption="Plantes à offrir pour la Saint-Valentin 🌿 Plus durable que des fleurs.",
        tiktok_desc="Plantes Saint-Valentin.\nFleurs = 3 jours.\nPlante = pour la vie.\n3 plantes parfaites pour offrir.\nLeafee = guide perso en cadeau.\n#saintvalentin #plantes #cadeaux #houseplants",
        image_prompts=[
            "Anthurium in red pot, candle nearby, slightly wilted flower, romantic table setting, iPhone, no bokeh, natural light",
            "Orchid on bedside table, wrinkled sheets, soft morning light, imperfect petals, iPhone photo",
            "Rose succulent in heart-shaped pot, desk clutter, natural imperfections, iPhone, sharp focus",
            "Anthurium with gift ribbon, coffee cup, lived-in romantic vibe, iPhone, no bokeh",
            "Romantic plant arrangement, candles, slightly messy, iPhone photo, realistic",
            "Philodendron heart leaves, bedroom corner, natural clutter, iPhone, imperfections",
        ],
    )
    return (
        "You are a content creator for TikTok & Instagram carousels.\n"
        "Generate a carousel about plants to give for Valentine's Day.\n\n"
        "TOPIC = Saint-Valentin. Keyword can add a twist (e.g. Romantique, Original, Couple).\n\n"
        "CONTEXT: Platforms TikTok & Instagram. Audience: people looking for Valentine gifts. Tone: romantic but not cheesy, casual.\n\n"
        + get_common_instructions()
        + "CAROUSEL: 6 slides. Slide 1 = intro. Slides 2-4 = 3 plants to give for Valentine's. "
        "Slide 5 = Leafee. Slide 6 = tip.\n\n"
        "Focus on plants with romantic symbolism or that last longer than cut flowers.\n"
        + get_image_prompts_instruction()
        + "\nExample structure:\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )
