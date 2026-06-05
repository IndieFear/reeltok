"""Plante selon style de déco."""

import json

from backend.content_types.base import get_schema_example, get_common_instructions, get_image_prompts_instruction

_DECOR_IMAGE_INSTRUCTION = """
IMAGE_PROMPTS FOR DECOR — CRITICAL: Every image MUST show a FULL ROOM SCENE. NO close-ups of isolated plants.

VARIATION — MANDATORY: Each slide MUST use a DIFFERENT room/corner. NEVER repeat the same room twice in one carousel.
Assign ONE unique room per slide from this list (use different ones for slides 1, 2, 3, 5, 6, 7):
• Living room (sofa, armchair, coffee table, TV stand, fireplace)
• Bedroom (bed, nightstand, dresser, mirror, wardrobe)
• Kitchen (counter, island, backsplash, stove, fridge)
• Bathroom (shelf above sink, vanity, bathtub corner, towel rack)
• Home office / desk area (desk, chair, bookshelf, monitor, filing)
• Reading nook (armchair, floor lamp, book stack, blanket, ottoman)
• Entryway / hallway (console table, coat rack, mirror, keys bowl)
• Balcony / terrace (small table, chair, city view, potted plants)
• Dining area (table, chairs, sideboard, pendant light)
• Kids room corner (shelf, toy storage, soft rug, playful colors)
• Laundry room / utility (shelf, washing machine, drying rack)
• Staircase landing (small table, runner rug, wall art)

FURNITURE & OBJECTS — Vary heavily. Mix from different categories:
- Surfaces: sideboard, console, shelf, nightstand, windowsill, counter, desk, coffee table, ottoman
- Seating: armchair, sofa, stool, bench, pouf, dining chair
- Lighting: pendant light, floor lamp, table lamp, Edison bulb, natural window light
- Objects: coffee mug, wine glass, books, magazine, vase, ceramic, candle, plant pot, frame, clock, basket, tray, fruit bowl, cutting board, towel, blanket, cushion, rug
- Materials: teak, oak, rattan, marble, concrete, brass, ceramic, linen, wool

LIGHTING — Vary per slide: morning light, golden hour, overcast soft light, afternoon sun, evening lamp glow, natural window, warm Edison bulb

SLIDE 1 (image_prompts[0]) — SELFIE. Pick ONE room from the list above. "selfie of a girl, one hand visible holding phone. behind her [ROOM]: [PLANT] on [surface], [2-3 furniture pieces], [2-3 objects], [lighting]. [keyword] style. Wide shot. iPhone, sharp focus, no bokeh, lived-in. high skin texture detail."

SLIDES 2, 3, 5, 6, 7 — Each a DIFFERENT room. Format: "[Room type], [plant] in [pot] on [surface]. [3-4 furniture pieces]. [Objects: x, y, z]. [keyword] style. [Lighting]. Wide shot. iPhone, sharp focus, no bokeh, lived-in."

SLIDE 4 (image_prompts[3]) — LEAFEE: "Leafee app on phone next to houseplant, soft light, cozy interior, iPhone photo". Replaced by Leafee asset.

CRITICAL: Slide 1 ≠ Slide 2 ≠ Slide 3 ≠ Slide 5 ≠ Slide 6 ≠ Slide 7 in terms of ROOM. Each prompt = different room type.

Style references for {keyword}:
- Mid century: teak, cognac leather, geometric pendant, vintage lamp, warm wood, orange accents
- Scandinave: light wood, white walls, hygge textiles, minimal, soft gray, natural fibers
- Bohème: macramé, rattan, woven baskets, layered textiles, earth tones, plants everywhere
- Industriel: exposed brick, metal shelf, Edison bulb, concrete, raw materials, urban loft
- Moderne: clean lines, statement piece, sleek pots, neutral palette, architectural plants
- Japandi: low furniture, natural materials, zen, muted colors, bamboo
"""


def build_prompt(keyword: str, num_slides: int = 7) -> str:
    schema = get_schema_example(
        intro_title=f"Plantes {keyword}",
        intro_body="Ta déco dit qui tu es. Et ta plante aussi. Voici les 5 plantes qui subliment un intérieur {keyword}.",
        tips=[
            {"tag": "5. Monstera", "body": "Une valeur sûre pour un intérieur {keyword}. Lignes, forme, pourquoi ça marche."},
            {"tag": "4. Pothos", "body": "Celle qui complète parfaitement une déco {keyword}. Easy to care for, fits anywhere."},
            {"tag": "LEAFEE", "body": "Leafee m'a aidé à choisir selon ma déco. Mon style, ma lumière, mon espace = plante parfaite."},
            {"tag": "3. Ficus lyrata", "body": "La plante underrated qui fait toute la différence. Mon secret."},
            {"tag": "2. Rubber plant", "body": "Celle que je recommande à mes amis. Où elle vit, ce qui la rend spéciale."},
            {"tag": "1. ZZ plant", "body": " Celle que je remplacerais en premier si quelque chose arrivait. Mon ride or die."},
        ],
        caption=f"Plantes pour une déco {keyword} 🌿",
        tiktok_desc=f"Plantes {keyword}.\nTa déco = ta plante.\n5 plantes qui subliment ton intérieur.\n5, 4, Leafee, puis 3, 2, 1.\nLeafee pour un guide perso.\n#{keyword.lower().replace(' ', '')} #deco #houseplants",
        image_prompts=[
            "selfie of a girl, one hand visible holding phone. behind her bathroom: Monstera in white pot on shelf above sink, vanity mirror, towel on rack, soft steam, morning light. Mid-century modern. Wide shot. iPhone, sharp focus, no bokeh, lived-in. high skin texture detail.",
            "Home office, Monstera deliciosa in terracotta pot on desk next to laptop, bookshelf, brass lamp, mug and papers, overcast light through window. Mid-century. Full scene. iPhone, sharp focus",
            "Bedroom, Pothos golden in ceramic pot on nightstand, rumpled linen, reading lamp, glasses and book, golden hour through curtains. Mid-century touches. Wide shot. iPhone, lived-in",
            "Leafee app on phone next to houseplant, soft morning light, cozy interior, iPhone photo, sharp focus",
            "Kitchen counter, Ficus lyrata in corner, coffee machine, tile backsplash, cutting board, fruit bowl. Mid-century. Full scene. iPhone, sharp focus",
            "Entryway, Rubber plant on console table, coat rack, keys bowl, mirror, afternoon light. Mid-century. Wide shot. iPhone, natural light",
            "Reading nook, ZZ plant in terracotta pot on floor next to armchair, blanket, book stack, floor lamp, evening glow. Mid-century. Full shot. iPhone, lived-in",
        ],
    )
    decor_instruction = _DECOR_IMAGE_INSTRUCTION.format(keyword=keyword)
    return (
        "You are a content creator for TikTok & Instagram carousels.\n"
        "Generate a carousel about plants that match a decor style.\n\n"
        f"STYLE = '{keyword}' (e.g. Mid century, Moderne, Scandinave, Bohème, Industriel).\n\n"
        "CONTEXT: Platforms TikTok & Instagram. Audience: decor and plant lovers. Tone: aesthetic, casual.\n\n"
        + get_common_instructions()
        + "CAROUSEL STRUCTURE (7 slides) — DESCENDING ORDER (people scroll, so start from the bottom of the list):\n"
        "Slide 1: intro_title + intro_body. Selfie vibe. intro_title in English: \"Plants for [keyword] decor\" (e.g. \"Plants for Mid century decor\").\n"
        "Slide 2 (tips[0]): tag = \"5. [plant name]\" — Fifth place. Format \"5. PlantName\" (e.g. \"5. Monstera\", \"5. Pothos\").\n"
        "Slide 3 (tips[1]): tag = \"4. [plant name]\" — Fourth place. Format \"4. PlantName\".\n"
        "Slide 4 (tips[2]): tag = \"LEAFEE\" — Fixed. How Leafee helped you choose according to your decor.\n"
        "Slide 5 (tips[3]): tag = \"3. [plant name]\" — Third place. Format \"3. PlantName\".\n"
        "Slide 6 (tips[4]): tag = \"2. [plant name]\" — Second place. Format \"2. PlantName\".\n"
        "Slide 7 (tips[5]): tag = \"1. [plant name]\" — Your number one. Format \"1. PlantName\".\n\n"
        "TAG FORMAT: For plant slides, tag MUST be \"{rank}. {plant name}\" (e.g. \"5. Monstera\", \"4. Pothos\", \"3. Ficus lyrata\"). "
        "The plant name in each tag should match the plant described in the corresponding image_prompt. LEAFEE slide keeps tag \"LEAFEE\".\n\n"
        "CRITICAL: Return exactly 6 tips (one per slide 2-7). Exactly 7 image_prompts (one per slide).\n\n"
        "Be specific about why each plant matches the style (shape, color, vibe).\n\n"
        "IMAGE_PROMPTS — MANDATORY: Describe FULL ROOM SCENES. Each slide = a DIFFERENT room (living room, bedroom, kitchen, bathroom, office, entryway, balcony, reading nook, etc.). "
        "NEVER use the same room twice. Vary furniture, objects, lighting (morning/golden hour/overcast). Wide shot, lived-in.\n"
        + decor_instruction
        + "\nExample structure:\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )
