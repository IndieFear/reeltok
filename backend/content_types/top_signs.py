"""Top 5 signes / symptômes — ex: 5 Signs You’re Overwatering Your Plant."""

import json

from backend.content_types.base import (
    get_schema_example,
    get_common_instructions,
    get_image_prompts_instruction,
)


def build_prompt(keyword: str, num_slides: int = 7) -> str:
    """
    Génère un prompt pour un carousel "Top 5 signs" en ordre décroissant.

    Exemple de keyword :
      - "you’re overwatering your plant"
      - "your plant needs more light"
      - "your Monstera is unhappy"
    """
    schema = get_schema_example(
        intro_title=f"5 Signs {keyword}",
        intro_body="If you’ve been guessing, these are the 5 signs that actually matter — ranked from #5 to #1.",
        tips=[
            {
                "tag": "5. Sign",
                "body": "Sign number five — the one most people ignore but that quietly shows up first.",
            },
            {
                "tag": "4. Sign",
                "body": "Fourth place — the moment where you start realizing something is off but still think it’s normal.",
            },
            {
                "tag": "LEAFEE",
                "body": "Leafee literally tracks what your plant goes through so you stop guessing and see the signs before they get dramatic.",
            },
            {
                "tag": "3. Sign",
                "body": "Third place — the point where the plant is clearly telling you something, but most people still wait.",
            },
            {
                "tag": "2. Sign",
                "body": "Second place — the sign that makes you finally open Google and search “what’s wrong with my plant”.",
            },
            {
                "tag": "1. Sign",
                "body": "Number one — the moment where your plant is screaming for help and you can’t ignore it anymore.",
            },
        ],
        caption=f"5 signs {keyword} — ranked from #5 to #1.",
        tiktok_desc=(
            f"5 signs {keyword}.\n"
            "Not the usual vague advice.\n"
            "Real signs ranked from #5 to #1.\n"
            "Leafee helps you catch them earlier.\n"
            "#houseplants #plantsoftiktok #plantcare"
        ),
        image_prompts=[
            "selfie of a girl. behind her a medium-sized houseplant on a windowsill, leaves just starting to look slightly dull and less perky, cozy living room with sofa and books, soft morning light. iPhone photo, sharp focus, no bokeh, natural and lived-in. high skin texture detail.",
            "Living room scene: overwatered plant in a ceramic pot on a low table, soil looking very dark and wet, a small puddle on the saucer, couch and throw blanket in the background, warm afternoon light through curtains. iPhone photo, sharp focus, no bokeh, realistic and relatable.",
            "Desk scene: Leafee app open on a phone next to a slightly sad plant in a pot, laptop, notebook and pen on the desk, mug with coffee, neutral daylight from a nearby window. iPhone photo, sharp focus, lived-in but tidy workspace.",
            "Bedroom scene: plant on a nightstand with several yellowing leaves drooping over the edge, bed with rumpled linen sheets, book and glasses nearby, soft golden hour light through curtains. iPhone photo, sharp focus, no bokeh, natural home vibe.",
            "Kitchen corner: plant on a counter with multiple brown leaf tips and soggy soil, cutting board, kettle and spice jars behind, overhead warm light mixed with cool daylight from a window. iPhone photo, realistic, sharp focus, everyday mess level.",
            "Bathroom shelf: plant on a high shelf with many limp, yellow leaves, some fallen on the floor, towel rack and mirror visible, slightly steamy atmosphere, soft diffused light. iPhone photo, sharp focus, lived-in and realistic.",
            "Entryway: plant on a small bench near the door, leaves almost entirely yellow or brown and curling, a few crispy leaves on the ground, coat hooks and shoes nearby, dramatic evening light from the open door. iPhone photo, sharp focus, no bokeh, urgent mood.",
        ],
    )
    return (
        "You are a content creator for TikTok & Instagram carousels.\n"
        "Generate a TOP 5 SIGNS carousel about plant problems.\n\n"
        f"TOPIC = '5 signs {keyword}'.\n"
        "Examples of topics you might receive:\n"
        "- \"you’re overwatering your plant\"\n"
        "- \"your plant needs more light\"\n"
        "- \"your Monstera is unhappy\"\n"
        "- \"your plant is rootbound\"\n"
        "- \"your plant is in the wrong room\"\n\n"
        "CONTEXT: Platforms TikTok & Instagram. Audience: people who feel lost with plants, beginners, busy people.\n"
        "TONE: Direct, simple, slightly dramatic but never mean. Talk to the viewer (you), not to “plant owners”.\n"
        "Make it feel like a friend pointing out what’s really happening.\n\n"
        + get_common_instructions()
        + "CAROUSEL STRUCTURE (7 slides) — DESCENDING ORDER (#5 to #1):\n"
        "Slide 1: intro_title + intro_body.\n"
        "- intro_title MUST be in English and follow this pattern: \"5 Signs [short version of keyword]\" "
        "(e.g. \"5 Signs You’re Overwatering Your Plant\", \"5 Signs Your Plant Needs More Light\").\n"
        "- intro_body: 1–2 short sentences that set up why these signs matter and why most people miss them.\n"
        "Slide 2 (tips[0]): tag = \"5. [VERY SHORT SIGN]\" — The earliest or most subtle sign.\n"
        "Slide 3 (tips[1]): tag = \"4. [VERY SHORT SIGN]\" — Still early, but a bit more obvious.\n"
        "Slide 4 (tips[2]): tag = \"LEAFEE\" — Fixed. How Leafee helps you see and track these signs before it’s too late.\n"
        "Slide 5 (tips[3]): tag = \"3. [VERY SHORT SIGN]\" — Middle of the list, clearly visible.\n"
        "Slide 6 (tips[4]): tag = \"2. [VERY SHORT SIGN]\" — Strong sign that something is wrong.\n"
        "Slide 7 (tips[5]): tag = \"1. [VERY SHORT SIGN]\" — The worst / most dramatic sign.\n\n"
        "TAG FORMAT:\n"
        "- For sign slides, tag MUST be \"{rank}. [2–4 word label]\" (e.g. \"5. Always soggy soil\", \"3. Leaves drooping hard\").\n"
        "- tags are UPPERCASE or Title Case, max 4 words, no emojis.\n"
        "- LEAFEE slide keeps tag exactly \"LEAFEE\".\n\n"
        "BODY TEXT RULES:\n"
        "- Each tip body = 1–2 short sentences, no newlines.\n"
        "- Explain what the viewer actually sees (what the plant looks like) and what it really means.\n"
        "- Make it practical and visual, not generic theory.\n\n"
        "IMAGE FIELDS:\n"
        "- image_prompts: 7 ultra-detailed prompts following the same logic as the schema example.\n"
        + get_image_prompts_instruction()
        + "\nIMPORTANT:\n"
        "- You MUST respect the descending order 5 → 1 in both tags and explanations.\n"
        "- Make the signs visually different from each other.\n"
        "- Make sure the LEAFEE slide clearly connects the app to spotting or preventing these signs.\n\n"
        "Example structure:\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )

