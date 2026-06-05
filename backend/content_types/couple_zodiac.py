"""Combo mois de naissance couple = une plante."""

import json

from backend.content_types.base import get_schema_example, get_common_instructions, get_image_prompts_instruction


def build_prompt(keyword: str, num_slides: int = 6) -> str:
    # keyword format: "novembre janvier" or "lui novembre elle janvier"
    schema = get_schema_example(
        intro_title="Votre plante de couple",
        intro_body="Lui né en novembre, elle en janvier. Votre combo = une plante qui vous représente. Découvre la vôtre.",
        tips=[
            {"tag": "PLANTE", "body": "La plante parfaite pour ce combo : Monstera ou autre. Pourquoi elle vous correspond."},
            {"tag": "ENTRETIEN", "body": "Comment s'en occuper à deux : arrosage, lumière, qui fait quoi."},
            {"tag": "SYMBOLE", "body": "Ce que cette plante représente pour un couple : croissance, patience, complémentarité."},
            {"tag": "LEAFEE", "body": "Leafee pour un guide à deux : chacun peut suivre les besoins de votre plante commune."},
            {"tag": "BONUS", "body": "Idée : offrez-vous cette plante pour un anniversaire de couple."},
        ],
        caption="Votre plante de couple 🌿 Lui + elle = une plante qui vous ressemble.",
        tiktok_desc="Plante de couple.\nLui novembre.\nElle janvier.\n= Monstera.\nVotre combo = votre plante.\nLeafee pour un guide à deux.\n#couple #plantes #zodiaque #houseplants",
        image_prompts=[
            "Monstera on couple's nightstand, two coffee mugs, morning light, dusty leaves, iPhone, no bokeh",
            "Monstera in shared living room, books and blanket, lived-in couple vibe, iPhone photo",
            "Monstera in corner, two chairs visible, natural imperfections, iPhone, sharp focus",
            "Monstera on kitchen table, breakfast clutter, couple's home, iPhone, realistic",
            "Couple's plant in bedroom, wrinkled bedding, natural light, iPhone photo, no bokeh",
            "Monstera by window, couple's apartment, casual interior, iPhone, imperfections",
        ],
    )
    return (
        "You are a content creator for TikTok & Instagram carousels.\n"
        "Generate a carousel about the 'couple plant' based on birth months.\n\n"
        f"KEYWORD = '{keyword}' (e.g. 'novembre janvier' = his month + her month, or 'lui novembre elle janvier').\n"
        "Parse the months. Example: novembre + janvier = Monstera (or another plant that 'combines' both energies).\n\n"
        "CONTEXT: Platforms TikTok & Instagram. Audience: couples, plant lovers. Tone: romantic, fun, casual.\n\n"
        + get_common_instructions()
        + "CAROUSEL: 6 slides. Slide 1 = intro (announce the couple's plant). "
        "Slide 2 = the plant and why it matches. Slide 3 = care (as a couple). Slide 4 = symbolism. "
        "Slide 5 = Leafee. Slide 6 = bonus idea.\n\n"
        "The plant should feel like a 'combination' of both birth months/personalities. Be creative.\n"
        + get_image_prompts_instruction()
        + "\nExample structure:\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )
