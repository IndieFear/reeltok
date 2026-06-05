"""Before/After - Transformation d'une plante (avant soins vs après)."""

import json

from backend.content_types.base import get_schema_example, get_common_instructions, get_image_prompts_instruction


def build_prompt(keyword: str, num_slides: int = 6) -> str:
    schema = get_schema_example(
        intro_title=f"Before vs After {keyword}",
        intro_body="I almost killed this one. Here's what changed and how it bounced back.",
        tips=[
            {"tag": "BEFORE", "body": "This was it a few months ago. Yellow leaves, drooping, barely hanging on. I thought I was done for."},
            {"tag": "THE MISTAKE", "body": "I was overwatering. And had it in a dark corner. Classic beginner move."},
            {"tag": "LEAFEE", "body": "Leafee showed me exactly when to water and how much light it actually needed. Stopped guessing."},
            {"tag": "AFTER", "body": "Now it's thriving. New growth everywhere. Took about two months to see the difference."},
            {"tag": "THE FIX", "body": "Moved it to a bright spot, let the soil dry between waterings, and stuck to a routine. That's it."},
        ],
        caption=f"My {keyword} glow up — before vs after",
        tiktok_desc=f"Before vs After {keyword}.\nAlmost killed it.\nYellow leaves, drooping.\nI was overwatering.\nWrong spot too.\nLeafee helped me fix it.\nNow it's thriving.\nTwo months of consistency.\n#beforeandafter #houseplants #plantsoftiktok",
        image_prompts=[
            "selfie of a girl. behind her a Monstera in ceramic pot on kitchen counter, morning light, coffee mug nearby. iPhone photo, sharp focus, no bokeh, natural and lived-in. high skin texture detail.",
            "Monstera plant with yellow wilted leaves, drooping, sad state, terracotta pot, dim lighting, iPhone photo, no bokeh, realistic",
            "Monstera in corner of room, poor lighting, slightly wilted leaves, ceramic pot, iPhone, natural imperfections",
            "Leafee app on phone next to houseplant, soft morning light, cozy interior, iPhone photo, sharp focus",
            "Monstera plant thriving, healthy green leaves, new growth, ceramic pot, bright natural light, iPhone, no bokeh, lived-in",
            "Monstera close-up healthy leaves, vibrant, terracotta pot, windowsill, golden hour, iPhone photo, sharp focus",
        ],
    )
    return (
        "You are a content creator for TikTok & Instagram carousels.\n"
        "Generate a BEFORE/AFTER transformation carousel about a plant.\n\n"
        f"PLANT = '{keyword}' (e.g. 'Monstera', 'Pothos', 'Fiddle leaf fig', 'Calathea').\n\n"
        "CONTEXT: Platforms TikTok & Instagram. Audience: plant lovers, beginners who've struggled. "
        "This format shows a plant transformation — from struggling to thriving.\n\n"
        "TONE: Personal, honest, relatable. Use first person (I, my, me). Share the real struggle and the real fix. "
        "Natural English, conversational. No emojis. Sound like someone who almost killed their plant and figured it out.\n\n"
        + get_common_instructions()
        + "CAROUSEL STRUCTURE (6 slides):\n"
        "Slide 1: intro_title + intro_body. intro_title MUST be in English: \"Before vs After [plant]\" or \"My [plant] glow up\". "
        "intro_body: personal hook — almost killed it, here's what changed.\n"
        "Slide 2 (tips[0]): BEFORE — The plant in its sad state. Yellow leaves, wilting, what it looked like when struggling. Be specific.\n"
        "Slide 3 (tips[1]): THE MISTAKE — What you were doing wrong. Overwatering, wrong light, neglect. Honest and relatable.\n"
        "Slide 4 (tips[2]): LEAFEE — How Leafee helped you fix it. Tracking, reminders, understanding the plant's needs.\n"
        "Slide 5 (tips[3]): AFTER — The plant now, thriving. New growth, healthy leaves. The glow up.\n"
        "Slide 6 (tips[4]): THE FIX — What you actually changed. The concrete steps that made the difference. Keep it simple.\n\n"
        "Keep each tip body to 1-2 short sentences. No newlines inside body text.\n"
        "image_prompts: Slide 2 = plant in BAD state (yellow, wilted). Slide 5 = plant THRIVING. Slide 6 = healthy plant. "
        "Slide 1 = selfie. Slide 4 = Leafee. Be specific about the plant species in each prompt.\n"
        + get_image_prompts_instruction()
        + "\nExample structure:\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )
