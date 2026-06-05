"""Top X - Liste de plantes par catégorie (ex: top 5 plantes roses, top 5 pour la chambre)."""

import json

from backend.content_types.base import get_schema_example, get_common_instructions, get_image_prompts_instruction

_TOP_X_IMAGE_INSTRUCTION = """
IMAGE_PROMPTS FOR TOP 5 — PLANT-FOCUSED, NATURAL SCALE (VERY IMPORTANT)

The plant is the hero, but it must look REAL — normal houseplant size, not macro, not giant.
Slides 2, 3, 5, 6, 7 show the FULL plant in its pot at natural proportions (medium shot),
like a real iPhone photo someone would post of their plant at home.

For each ranked plant slide, describe:
- The exact species in the tag (e.g. Anthurium, Caladium, Philodendron pink princess)
- The whole plant visible: pot + stems + leaves at believable indoor size (30–80 cm tall typical)
- A simple cozy setting (windowsill, shelf, desk corner, side table) — tight crop, NOT a wide room,
  but enough context to feel natural. Plant occupies roughly 40–60% of the frame, centered or slightly off-center.
- Natural light, iPhone photo, sharp focus, no bokeh, lived-in and realistic.

SLIDE 1 — SELFIE (intro, plant #5 visible behind or next to her):
"selfie of a girl. behind or next to her [simple setting: shelf / windowsill / desk corner]: [plant #5] in [pot]
 at normal size on [surface], a few everyday objects nearby, [lighting]. The plant looks like a real
 houseplant behind or next to her. iPhone photo, sharp focus, no bokeh,
 natural and lived-in. high skin texture detail."

SLIDES 2, 3, 5, 6, 7 — Plant portraits at natural scale (species matches the tag rank):
"[Simple setting], [plant name] in [pot] on [surface]. Full plant visible at normal indoor size,
 healthy and realistic. [1–2 small props: mug, book, candle]. [lighting]. iPhone photo, sharp focus,
 no bokeh, plant is clearly the subject but at real-world scale, cozy home vibe."

Vary across slides: different species, surfaces (windowsill, wooden shelf, desk, plant stand),
pots (terracotta, ceramic white, woven basket), lighting (morning, golden hour, overcast).

SLIDE 4 — LEAFEE:
"Leafee app on phone next to a houseplant on a windowsill, soft light, cozy interior, iPhone photo, sharp focus".
Replaced by Leafee asset in the final carousel.

CRITICAL:
- NO macro close-ups, NO leaves filling 80–90% of the frame, NO unrealistic giant plants behind a selfie.
- NO wide full-room shots either — keep a tight, plant-forward medium shot.
- Each plant slide must match the species named in the corresponding tip tag.
- Slides 2, 3, 5, 6, 7 must all look different (different plants, settings, lighting).
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
            "selfie of a girl. behind her a wooden shelf: Anthurium pink princess in a white ceramic pot,  a small mug and book nearby, soft morning window light. The plant looks natural behind her, not zoomed in. iPhone photo, sharp focus, no bokeh, natural and lived-in. high skin texture detail.",
            "Windowsill scene: Caladium bicolor in a terracotta pot at normal indoor size, full plant visible with heart-shaped pink-veined leaves. small candle on the sill, natural side window light. iPhone photo, sharp focus, no bokeh, plant is the clear subject at real-world scale, cozy home vibe.",
            "Wooden shelf: Begonia rex in a ceramic pot at normal size, full plant with patterned leaves visible. framed print and perfume bottle nearby, soft overcast light. iPhone photo, sharp focus, lived-in, realistic plant portrait.",
            "Leafee app open on a phone resting next to a houseplant on a windowsill, soft light, cozy interior, iPhone photo, sharp focus, realistic.",
            "Desk corner: Philodendron pink princess in a white pot at normal size, full trailing plant visible. laptop edge and mug nearby, golden hour light. iPhone photo, sharp focus, no bokeh, natural indoor plant photo.",
            "Plant stand by a window: Calathea medallion in a simple pot at normal height, whole plant visible with round patterned leaves. folded throw on a chair in soft background, cool natural light. iPhone photo, sharp focus, realistic.",
            "Side table: Anthurium andraeanum in terracotta pot at normal size, full plant with glossy red bloom and green leaves. reading glasses and coaster nearby, warm afternoon window light. iPhone photo, sharp focus, no bokeh, cozy and natural.",
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
        "IMAGE_PROMPTS — Each plant slide = medium shot of the FULL plant at normal indoor size in a cozy setting. "
        "Plant-forward but realistic (NOT macro, NOT wide room). Vary species, settings, and lighting.\n"
        + _TOP_X_IMAGE_INSTRUCTION
        + "\nExample structure:\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )
