"""Idées cadeau pour plant lover."""

import json

from backend.content_types.base import get_schema_example, get_common_instructions, get_image_prompts_instruction


def build_prompt(keyword: str, num_slides: int = 6) -> str:
    schema = get_schema_example(
        intro_title=f"Cadeaux plant lover",
        intro_body="Tu cherches un cadeau pour un plant lover ? Voici des idées qui font toujours leur effet.",
        tips=[
            {"tag": "IDÉE 1", "body": "Première idée : plante + pourquoi c'est un bon cadeau."},
            {"tag": "IDÉE 2", "body": "Deuxième option : accessoire ou kit qui plaît aux plant lovers."},
            {"tag": "IDÉE 3", "body": "Troisième idée : expérience ou abonnement lié aux plantes."},
            {"tag": "LEAFEE", "body": "Leafee en cadeau ? Un guide personnalisé pour leur plante. Ils vont adorer."},
            {"tag": "TIPS", "body": "Pense à leur niveau : débutant ou collectionneur, ça change tout."},
        ],
        caption="Cadeaux pour plant lover 🌿 Sauve ça pour la prochaine occasion.",
        tiktok_desc="Cadeaux plant lover.\nDes idées qui font toujours leur effet.\nPlantes.\nAccessoires.\nExpériences.\nLeafee = guide perso en cadeau.\n#cadeaux #plantlover #houseplants",
        image_prompts=[
            "Monstera in gift wrap, ribbon slightly crooked, table with coffee mug, iPhone, natural light, no bokeh",
            "Pothos in decorative pot, gift card visible, lived-in room, dusty leaves, iPhone photo",
            "Succulent in small ceramic pot, gift box nearby, natural imperfections, iPhone, sharp focus",
            "Plant gift on kitchen table, morning light, clutter, iPhone, realistic",
            "Houseplant with bow, imperfect wrapping, casual interior, iPhone photo, no bokeh",
            "Orchid on desk, gift tag, papers and cables, iPhone, natural imperfections",
        ],
    )
    return (
        "You are a content creator for TikTok & Instagram carousels.\n"
        "Generate a carousel about gift ideas for plant lovers.\n\n"
        f"OCCASION = '{keyword}' (e.g. Anniversaire, Housewarming, Noël, Fête des mères). "
        "Adapt the suggestions to this occasion if relevant.\n\n"
        "CONTEXT: Platforms TikTok & Instagram. Audience: people looking for gift ideas. Tone: helpful, casual.\n\n"
        + get_common_instructions()
        + "CAROUSEL: 6 slides. Slide 1 = intro. Slides 2-4 = 3 gift ideas (plants, accessories, experiences). "
        "Slide 5 = Leafee as a gift idea. Slide 6 = tip (e.g. consider their level).\n"
        + get_image_prompts_instruction()
        + "\nExample structure:\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )
