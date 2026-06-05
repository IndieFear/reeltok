"""Top X - Liste de plantes par catégorie (ex: top 5 plantes roses, top 5 pour la chambre)."""

import json

from backend.content_types.base import get_schema_example, get_common_instructions, get_image_prompts_instruction

_TOP_X_IMAGE_INSTRUCTION = """
IMAGE_PROMPTS FOR TOP 5 — ROOM LOGIC (VERY IMPORTANT)

1) If the CATEGORY clearly targets a specific room or location (in ANY language),
   ALL slides (except the Leafee slide) MUST be in that same room.
   Examples of room-focused keywords (non‑exhaustive):
   - French: "salle de bain", "salle de bains", "salle de bain plantes", "plantes pour la chambre",
     "plantes pour le salon", "plantes pour la cuisine", "plantes pour le bureau"
   - English: "bathroom plants", "plants for bedroom", "plants for the kitchen", "office plants"
   - Others: any wording that clearly implies a room or area in the home.

   In that case:
   - Detect the room (bathroom, bedroom, living room, kitchen, office, balcony, etc.).
   - Slide 1 selfie AND slides 2, 3, 5, 6, 7 are ALL set in that same room.
   - Only the composition / angle / furniture / objects vary between slides.

2) If the CATEGORY is more generic (eg. "pink plants", "air‑purifying plants", "easy plants"),
   then you MUST vary the rooms across slides:
   - Assign one different room per slide (slides 1, 2, 3, 5, 6, 7)
   - Use rooms from this list:
     • Living room (sofa, armchair, coffee table, TV stand)
     • Bedroom (bed, nightstand, dresser, mirror)
     • Kitchen (counter, island, backsplash, stove)
     • Bathroom (shelf above sink, vanity, towel rack)
     • Home office / desk (desk, chair, bookshelf, monitor)
     • Reading nook (armchair, floor lamp, book stack, blanket)
     • Entryway (console table, coat rack, mirror)
     • Balcony / terrace (small table, city view, potted plants)
     • Dining area (table, sideboard, pendant light)
     • Windowsill corner (shelf, curtain, natural light)

In ALL cases:
- Vary: furniture (sideboard, shelf, desk, nightstand, counter, windowsill),
  objects (mug, books, vase, lamp, blanket), lighting (morning, golden hour, overcast, afternoon).

SLIDE 1 — SELFIE:
"selfie of a girl. behind her [ROOM]: [plant] on [surface], [furniture], [objects], [lighting].
 iPhone photo, sharp focus, no bokeh, natural and lived‑in. high skin texture detail."

SLIDES 2, 3, 5, 6, 7 — Full room scenes:
"[ROOM], [plant] in [pot] on [surface]. [furniture]. [objects]. [lighting].
 iPhone photo, sharp focus, no bokeh, lived‑in, realistic."

SLIDE 4 — LEAFEE:
"Leafee app on phone next to houseplant, soft light, cozy interior, iPhone photo, sharp focus".
Replaced by Leafee asset in the final carousel.

CRITICAL:
- For room‑focused categories: SAME room across slides 1, 2, 3, 5, 6, 7.
- For generic categories: Slide 1 ≠ 2 ≠ 3 ≠ 5 ≠ 6 ≠ 7 (different rooms).
- Always show full room context, not plant close‑ups.
"""


def build_prompt(keyword: str, num_slides: int = 7) -> str:
    schema = get_schema_example(
        intro_title=f"Top 5 {keyword}",
        intro_body="I went through a lot of trial and error with this one. These are the five I actually kept and still love.",
        tips=[
            {"tag": "5. Anthurium", "body": "Starting with number five. Solid pick that's been with me for over a year. Can't go wrong."},
            {"tag": "4. Caladium", "body": "Fourth place. Another one that's held up. Easy to care for, fits anywhere."},
            {"tag": "LEAFEE", "body": "Leafee told me which of these would actually survive in my apartment. Saved me from killing a few more."},
            {"tag": "3. Philodendron pink", "body": "Nobody talks about this one but mine's been thriving for months with almost no attention. My secret pick."},
            {"tag": "2. Calathea", "body": "I put this next to my desk and it just fits. The one I recommend to friends when they ask."},
            {"tag": "1. Anthurium", "body": "This one lives on my windowsill and I swear by it. The one I'd replace first if anything happened. My ride or die."},
        ],
        caption=f"My top 5 {keyword} — the ones I actually kept",
        tiktok_desc=f"Top 5 {keyword}.\nMy personal picks.\nScroll to see the full ranking.\n5, 4, then Leafee.\nThen 3, 2, and number one at the end.\n#houseplants #plantsoftiktok",
        image_prompts=[
            "selfie of a girl. behind her bathroom: Anthurium pink in a white pot on a shelf above the sink, vanity with mirror, towel on rack, soft morning light. iPhone photo, sharp focus, no bokeh, natural and lived-in. high skin texture detail.",
            "Bathroom scene: Caladium in a ceramic pot on a wooden stool next to the bathtub, tiled walls, towel hanging, candle and skincare bottles on the edge of the tub, warm evening light. iPhone photo, sharp focus, no bokeh, realistic.",
            "Bathroom shelf: Begonia rex in terracotta pot on open shelving above the toilet, folded towels, framed print, small perfume bottles, diffused overcast light from a frosted window. iPhone, sharp focus, lived-in.",
            "Leafee app open on a phone resting next to a houseplant on a bathroom vanity, toothbrush holder, soap dispenser, mirror catching soft morning light. iPhone photo, sharp focus, realistic.",
            "Bathroom corner: Philodendron pink princess in a white pot on a narrow ladder shelf, hanging towel, woven laundry basket, bath mat on the floor, golden hour light streaming through a small window. iPhone, sharp focus, no bokeh.",
            "Bathroom windowsill: Calathea medallion in a simple pot on the sill, frosted glass window, small bottle of essential oils, neatly folded washcloths, cool overcast light. iPhone photo, realistic, lived-in.",
            "Bathroom entry area: Anthurium andraeanum on a low bench near the shower, towel hooks on the wall, bathrobe hanging, patterned floor tiles, soft afternoon light. iPhone photo, sharp focus, no bokeh, natural.",
        ],
    )
    return (
        "You are a content creator for TikTok & Instagram carousels.\n"
        "Generate a TOP 5 list carousel about plants.\n\n"
        f"CATEGORY = '{keyword}' (e.g. 'pink plants', 'bedroom plants', 'plants that love humidity', "
        "'easy plants', 'office plants', 'air-purifying plants', 'low-maintenance plants').\n\n"
        "CONTEXT: Platforms TikTok & Instagram. Audience: plant lovers, beginners.\n"
        "TONE: Personal and subjective. Use first person (I, my, me). Share real experiences: where you keep it, "
        "how long you've had it, why you love it. Sound like someone who actually owns these plants and has opinions. "
        "Natural English, conversational. No emojis. Avoid generic or robotic phrasing.\n\n"
        + get_common_instructions()
        + "CAROUSEL STRUCTURE (7 slides) — DESCENDING ORDER (people scroll, so start from the bottom of the list):\n"
        "Slide 1: intro_title + intro_body. intro_title MUST be in English: \"Top 5 [keyword]\" (e.g. \"Top 5 pink plants\", \"Top 5 bedroom plants\"). "
        "If the keyword is in another language, translate it to English for the title. intro_body: personal hook, in English.\n"
        "Slide 2 (tips[0]): tag = \"5. [plant name]\" — Fifth place. Use format \"5. PlantName\" (e.g. \"5. Anthurium\", \"5. Pothos\").\n"
        "Slide 3 (tips[1]): tag = \"4. [plant name]\" — Fourth place. Format \"4. PlantName\".\n"
        "Slide 4 (tips[2]): tag = \"LEAFEE\" — Fixed. How Leafee helped you personally.\n"
        "Slide 5 (tips[3]): tag = \"3. [plant name]\" — Third place. Format \"3. PlantName\".\n"
        "Slide 6 (tips[4]): tag = \"2. [plant name]\" — Second place. Format \"2. PlantName\".\n"
        "Slide 7 (tips[5]): tag = \"1. [plant name]\" — Your number one. Format \"1. PlantName\".\n\n"
        "TAG FORMAT: For plant slides, tag MUST be \"{rank}. {plant name}\" (e.g. \"5. Anthurium\", \"4. Caladium\", \"3. Philodendron pink princess\"). "
        "The plant name in each tag should match the plant described in the corresponding image_prompt. LEAFEE slide keeps tag \"LEAFEE\".\n\n"
        "CRITICAL: Return exactly 6 tips (one per slide 2-7). Exactly 7 image_prompts (one per slide).\n\n"
        "Be specific: name actual plant species (e.g. Anthurium, Caladium, Philodendron pink princess, Pothos).\n"
        "Keep each tip body to 1-2 short sentences. No newlines inside body text. This ensures the JSON is not truncated.\n\n"
        "IMAGE_PROMPTS — Each slide = DIFFERENT room (living room, bedroom, kitchen, bathroom, office, entryway, etc.). NEVER repeat. Full room scenes.\n"
        + _TOP_X_IMAGE_INSTRUCTION
        + "\nExample structure:\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )
