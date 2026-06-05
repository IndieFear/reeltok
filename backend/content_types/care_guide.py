"""Guide d'entretien de plantes."""

import json

from backend.content_types.base import get_schema_example, get_image_prompts_instruction


def build_prompt(keyword: str, num_slides: int = 6) -> str:
    schema = get_schema_example(
        intro_title=f"{keyword} care guide",
        intro_body="Everyone loves this plant, but most people struggle to keep it happy. Here is what actually works in real life.",
        tips=[
            {"tag": "WATER", "body": "Stop drowning it. Let the top layer of soil dry out before you even think about watering again."},
            {"tag": "LIGHT", "body": "It wants bright, indirect light. Near a window is perfect, direct harsh sun will just crisp the leaves."},
            {"tag": "LEAFEE", "body": "This got way easier once I stopped guessing and started tracking my plant care rhythm with Leafee."},
            {"tag": "REPOTTING", "body": "Repot only when roots are clearly circling the pot or poking out the bottom, not every few months."},
            {"tag": "TRUTH", "body": "Is it easy? Honestly, yes, if you stop overthinking and follow a simple routine."},
        ],
        caption=f"{keyword} care made simple 🌿 Save this so you don't have to Google it again.",
        tiktok_desc=f"{keyword}.\nBig leaves. Big vibe.\nBut most people mess it up.\nThis guide keeps it simple.\nWatering first.\nToo much water kills it.\nLet the soil dry a bit.\nThen water.\nAnd stop.\nLight matters. A lot.\nBright room.\nClose to a window.\nNo direct sun.\nRepot when it feels tight.\nRoots coming out?\nTime to size up.\nFresh soil. Done.\nWhat helped me most?\nHaving a care plan made for my plant.\nThat's why I use Leafee.\nIt gives me a personalized care guide, based on my {keyword} and my home.\nLess guessing.\nBetter growth.\n#plantcare #houseplants",
        image_prompts=[
            f"selfie of a girl standing slightly to the left of frame, shoulders relaxed, head gently tilted toward the camera, one hand holding the phone at chest height. behind her a {keyword} in a terracotta pot on a wooden nightstand, rumpled linen, a paperback book, and soft golden hour through sheer curtains. iPhone photo, sharp focus, no bokeh, natural skin texture, casual lived-in bedroom, warm but realistic.",
            f"A natural iPhone photo of a {keyword} in a terracotta pot on the same wooden nightstand, shot from standing height like the girl just stepped closer after taking the selfie. The leaves are crisp and detailed, the rumpled linen and paperback book are still visible in the background, soft window light, sharp focus, no bokeh, everyday cozy bedroom mood.",
            f"A realistic iPhone photo of the {keyword} moved near a bright window, slightly off-center, with sheer curtains, the same warm linen tones, and a half-full glass of water on the sill. The photo feels like the same person documenting her plant care routine at home, natural overcast light, sharp focus, no studio styling, lived-in but tidy.",
            f"A close natural photo of the {keyword} soil and pot, taken from above at a casual angle, with one hand lightly touching the edge of the terracotta pot to check moisture. Only one hand is visible, smartphone snapshot style, same bedroom window light, tiny soil texture details, no bokeh, honest real-life plant care moment.",
            f"A realistic iPhone photo of the {keyword} in a cozy room corner beside a soft curtain and a small stack of books, matching the same warm home aesthetic as the earlier slides. The plant is slightly imperfect and natural, leaves facing the window, soft morning light, sharp focus, no bokeh, casual composition like a real plant owner took it.",
            f"A final natural iPhone photo of the {keyword} on a kitchen counter next to a coffee mug, keys, and a folded dish towel, still matching the same person’s warm everyday home style. The plant is the clear subject but the scene feels unposed, morning light, sharp focus, no bokeh, realistic texture, calm routine feeling.",
        ],
    )
    return (
        "You are a content creator for TikTok & Instagram carousels.\n"
        "Generate a plant care guide for the app Leafee.\n\n"
        f"PLANT = '{keyword}'. The carousel is a care guide for this exact plant.\n\n"
        "CONTEXT: Platforms TikTok & Instagram. Audience: plant owners. Tone: ultra casual, human.\n\n"
        "OUTPUT: Return ONLY valid JSON. No markdown code blocks. Start with { and end with }.\n"
        "Structure: intro_title, intro_body, tips (array of 5 objects with tag and body), caption (MAX 90 chars), tiktok_description.\n\n"
        "CAROUSEL STRUCTURE:\n"
        f"Slide 1: intro_title + intro_body (announce the guide). intro_title MUST be exactly: \"{keyword} care guide\"\n"
        "Slide 2 (tips[0]): WATER - watering tips\n"
        "Slide 3 (tips[1]): LIGHT - light/exposure\n"
        "Slide 4 (tips[2]): LEAFEE - soft Leafee integration (e.g. \"Found my rhythm with this\")\n"
        "Slide 5 (tips[3]): REPOTTING or practical tip\n"
        "Slide 6 (tips[4]): TRUTH - difficulty/mindset\n\n"
        "tiktok_description: long SEO description, one short phrase per line. End with 4-5 hashtags.\n\n"
        "CARE GUIDE IMAGE PROMPTS — EXTRA IMPORTANT:\n"
        "- image_prompts must be much more detailed than normal search keywords. Each one should feel like a real photo brief.\n"
        "- All 6 images must feel like they were taken by the same girl/person in the same real home over the same morning or afternoon.\n"
        "- Keep a consistent visual language across all image_prompts: same smartphone/iPhone feel, similar warm natural light, similar home objects, similar casual composition, same plant species and pot when possible.\n"
        "- Avoid generic AI-photo language. Make each prompt specific: camera angle, room, objects, plant placement, lighting, textures, what is in the foreground/background.\n"
        "- The photos should feel natural, slightly imperfect, documentary, and lived-in, not staged, luxury, influencer, stock photo, studio, render, or over-polished.\n"
        "- For image_prompts[0], the girl must be visible and you MUST describe her position clearly: where she stands in the frame, how she holds the phone, her posture, head angle, and where the plant is behind/next to her.\n"
        "- If a hand appears in any prompt, only one hand can be visible, as if the person took the photo themselves. And it should be a girl hand.\n\n"
        + get_image_prompts_instruction()
        + "\nExample structure:\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )
