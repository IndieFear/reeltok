"""Vases, pots, arrosoirs."""

import json

from backend.content_types.base import get_schema_example, get_common_instructions, get_image_prompts_instruction


def build_prompt(keyword: str, num_slides: int = 6) -> str:
    schema = get_schema_example(
        intro_title=f"{keyword} pour tes plantes",
        intro_body="Une belle plante mérite un beau contenant. Voici des idées de vases, pots et arrosoirs qui subliment tes plantes.",
        tips=[
            {"tag": "IDÉE 1", "body": "Première idée : style, matière, pour quelle plante."},
            {"tag": "IDÉE 2", "body": "Deuxième option : un look différent, peut-être plus minimal ou plus coloré."},
            {"tag": "IDÉE 3", "body": "Troisième idée : accessoire pratique (arrosoir, vaporisateur) qui est aussi beau."},
            {"tag": "LEAFEE", "body": "Leafee m'aide à garder mes plantes en vie. Un beau pot c'est bien, une plante en bonne santé c'est mieux."},
            {"tag": "TIPS", "body": "Pense au drainage : un pot sans trou, c'est joli mais risqué."},
        ],
        caption=f"Vases, pots, arrosoirs 🌿 Des idées pour sublimer tes plantes.",
        tiktok_desc=f"{keyword} pour plantes.\nUn beau contenant = une plante sublimée.\n3 idées.\nLeafee pour les garder en vie.\n#pots #vases #arrosoir #houseplants",
        image_prompts=[
            "Terracotta pot with Monstera, water stain on pot, shelf with books, iPhone, no bokeh, natural light",
            "Ceramic pot with plant, slight chip visible, desk clutter, iPhone photo, realistic",
            "Brass watering can with plant, water droplets, lived-in room, iPhone, sharp focus",
            "Plant in decorative pot, cable visible, imperfect arrangement, iPhone, no bokeh",
            "Houseplant collection, messy pots, natural imperfections, iPhone photo",
            "Monstera in large pot, dust on leaves, casual interior, iPhone, realistic",
        ],
    )
    return (
        "You are a content creator for TikTok & Instagram carousels.\n"
        "Generate a carousel about plant accessories: vases, pots, watering cans.\n\n"
        f"TYPE = '{keyword}' (e.g. Vase, Pot céramique, Arrosoir, Pot design).\n\n"
        "CONTEXT: Platforms TikTok & Instagram. Audience: plant lovers who care about aesthetics. Tone: aesthetic, casual.\n\n"
        + get_common_instructions()
        + "CAROUSEL: 6 slides. Slide 1 = intro. Slides 2-4 = 3 accessory ideas (describe style, material, which plants). "
        "Slide 5 = Leafee (keeping plants alive matters). Slide 6 = practical tip (drainage, etc.).\n"
        + get_image_prompts_instruction()
        + "\nExample structure:\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )
