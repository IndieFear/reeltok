"""Plantes for him/her anniversaire."""

import json

from backend.content_types.base import get_schema_example, get_common_instructions, get_image_prompts_instruction


def build_prompt(keyword: str, num_slides: int = 6) -> str:
    schema = get_schema_example(
        intro_title=f"Plantes à offrir pour {keyword}",
        intro_body="Un anniversaire, un plant lover. Voici les plantes qui font toujours plaisir, pour lui ou pour elle.",
        tips=[
            {"tag": "PLANTE 1", "body": "Première idée : une plante qui plaît et qui est facile d'entretien."},
            {"tag": "PLANTE 2", "body": "Deuxième option : une plante plus originale pour les collectionneurs."},
            {"tag": "PLANTE 3", "body": "Troisième idée : plante + pot ou accessoire pour un cadeau complet."},
            {"tag": "LEAFEE", "body": "Leafee en complément : un guide perso pour leur nouvelle plante. Cadeau qui dure."},
            {"tag": "TIPS", "body": "Adapte au niveau : débutant = plante facile, passionné = plante rare."},
        ],
        caption=f"Plantes à offrir pour un anniversaire 🌿 Pour lui ou pour elle.",
        tiktok_desc="Plantes anniversaire.\nPour lui.\nPour elle.\n3 idées qui font plaisir.\nLeafee = guide perso en cadeau.\n#anniversaire #cadeaux #plantlover #houseplants",
        image_prompts=[
            "Monstera as birthday gift, unwrapped, ribbon on table, party clutter, iPhone, no bokeh, natural",
            "Pothos in gift pot, birthday card visible, lived-in room, dusty leaves, iPhone photo",
            "ZZ plant in decorative pot, gift bag, natural imperfections, iPhone, sharp focus",
            "Plant gift on kitchen counter, cake nearby, casual birthday vibe, iPhone, realistic",
            "Houseplant with birthday balloon, imperfect arrangement, iPhone photo, no bokeh",
            "Succulent gift, small pot, confetti on table, iPhone, natural clutter",
        ],
    )
    return (
        "You are a content creator for TikTok & Instagram carousels.\n"
        "Generate a carousel about plants to give for a birthday (for him or her).\n\n"
        f"TARGET = '{keyword}' (e.g. Lui, Elle, Un ami, Une amie).\n\n"
        "CONTEXT: Platforms TikTok & Instagram. Audience: people looking for birthday gifts. Tone: helpful, casual.\n\n"
        + get_common_instructions()
        + "CAROUSEL: 6 slides. Slide 1 = intro. Slides 2-4 = 3 plant gift ideas. "
        "Slide 5 = Leafee. Slide 6 = tip (adapt to their level).\n"
        + get_image_prompts_instruction()
        + "\nExample structure:\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )
