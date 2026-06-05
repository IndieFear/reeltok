"""Plantes selon signe astrologique."""

import json

from backend.content_types.base import get_schema_example, get_common_instructions, get_image_prompts_instruction


def build_prompt(keyword: str, num_slides: int = 7) -> str:
    schema = get_schema_example(
        intro_title=f"Plants for {keyword}",
        intro_body=f"Your sign says a lot about you. What if your perfect plant matched too? Here are the five that vibe with {keyword}s.",
        tips=[
            {"tag": "5. Monstera", "body": "Solid pick. Low maintenance, fits anywhere. Mine's been with me for over a year and still going strong."},
            {"tag": "4. Pothos", "body": "This one just gets me. Easy to care for, trails nicely. Perfect for when you want something that doesn't need constant attention."},
            {"tag": "LEAFEE", "body": "Leafee helped me find mine. My sign, my space, my vibe = a plant that actually fits. No more guessing."},
            {"tag": "3. Calathea", "body": "For when you like a challenge. A bit more picky but so worth it when it thrives. My secret flex."},
            {"tag": "2. ZZ plant", "body": "The one I recommend to friends. Lives on my desk, barely needs water. Where it sits, why it's special."},
            {"tag": "1. Philodendron", "body": "My ride or die. The one I'd replace first if anything happened. Lives on my windowsill and I swear by it."},
        ],
        caption=f"Plants for {keyword} 🌿 Save this to find your match.",
        tiktok_desc=f"Plants for {keyword}.\nYour sign = your plant.\n5 picks that actually vibe with you.\nLeafee helped me find mine.\n#astrology #plants #{keyword.lower().replace(' ', '')} #houseplants",
        image_prompts=[
            "selfie of a girl, behind her Monstera in white pot, cozy room, morning light. iPhone photo, sharp focus, no bokeh, lived-in. high skin texture detail.",
            "Monstera in corner, wrinkled curtain, plant slightly tilted, casual interior, iPhone photo, realistic, no bokeh",
            "Pothos trailing from shelf, coffee mug visible, imperfect arrangement, natural light, iPhone",
            "Leafee app on phone next to houseplant, soft morning light, cozy interior, iPhone photo, sharp focus",
            "Calathea with patterned leaves, ceramic pot, desk with laptop, natural imperfections, iPhone",
            "ZZ plant in terracotta pot, windowsill, natural light, iPhone photo, sharp focus",
            "Philodendron in white pot, shelf with books, lived-in room, iPhone, no bokeh",
        ],
    )
    return (
        "You are a content creator for TikTok & Instagram carousels.\n"
        "Generate a carousel about plants that match an astrological sign.\n\n"
        f"SIGN = '{keyword}' (e.g. Aries, Scorpio, Leo). If the keyword is in French, use the English sign name in the output.\n\n"
        "CONTEXT: Platforms TikTok & Instagram. Audience: plant lovers interested in astrology. "
        "TONE: Casual, personal, first person (I, my, me). Sound like a real person sharing their picks. Fun but not cheesy. Natural English.\n\n"
        + get_common_instructions()
        + "CAROUSEL STRUCTURE (7 slides) — DESCENDING ORDER (people scroll, so start from the bottom of the list):\n"
        "Slide 1: intro_title + intro_body. intro_title in English: \"Plants for [sign]\" (e.g. \"Plants for Aries\"). intro_body: personal hook, casual.\n"
        "Slide 2 (tips[0]): tag = \"5. [plant name]\". body: personal reasons why you kept it, why it fits the sign. NO \"fifth place\" or ranking mentions.\n"
        "Slide 3 (tips[1]): tag = \"4. [plant name]\". body: personal context, where it lives, why you love it. NO ranking mentions.\n"
        "Slide 4 (tips[2]): tag = \"LEAFEE\". body: How Leafee helped you find your plant based on your sign. Personal.\n"
        "Slide 5 (tips[3]): tag = \"3. [plant name]\". body: personal take, underrated pick. NO ranking mentions.\n"
        "Slide 6 (tips[4]): tag = \"2. [plant name]\". body: the one you recommend, where it lives. NO ranking mentions.\n"
        "Slide 7 (tips[5]): tag = \"1. [plant name]\". body: your ride or die, the one you'd replace first. NO ranking mentions.\n\n"
        "TAG FORMAT: tag = \"{rank}. {plant name}\" (e.g. \"5. Monstera\", \"4. Pothos\"). The body text must NOT repeat \"fifth place\", \"fourth place\", etc. "
        "Keep it personal and casual. LEAFEE slide keeps tag \"LEAFEE\".\n\n"
        "CRITICAL: This template has 7 slides. Return exactly 6 tips (one per slide 2-7). Exactly 7 image_prompts. "
        "Ignore any instruction about '5 tips' — for astrology use 6 tips and 7 image_prompts.\n\n"
        "Be specific about why each plant matches the sign's personality. Use first person, natural English.\n"
        + get_image_prompts_instruction()
        + "\nExample structure:\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )
