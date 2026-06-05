"""Hooks viraux sur les problèmes de plantes (why your plant is dying, etc.)."""

import json

from backend.content_types.base import get_schema_example, get_common_instructions, get_image_prompts_instruction


def build_prompt(keyword: str, num_slides: int = 6) -> str:
    """
    Template plus général basé sur des hooks viraux.

    Le mot-clé `keyword` représente le contexte principal (ex: "overwatering", "yellow leaves", "dying plant").
    """
    schema = get_schema_example(
        intro_title="Why your plant keeps dying",
        intro_body="You water it. You care. It still looks sad. Here’s what’s actually going wrong.",
        tips=[
            {
                "tag": "Why it dies",
                "body": "You think you’re helping it… but every time you water, you’re slowly drowning the roots.",
            },
            {
                "tag": "Hidden mistake",
                "body": "You bought a “low light” plant and hid it in the darkest corner of your home. It can’t photosynthesize there.",
            },
            {
                "tag": "LEAFEE",
                "body": "I stopped guessing once I used Leafee to track watering and light — it literally tells me when to stop touching the plant.",
            },
            {
                "tag": "Simple fix",
                "body": "Move it closer to a window, let the soil dry almost fully between waterings, and repot it in well‑draining mix.",
            },
            {
                "tag": "The truth",
                "body": "You’re not “bad with plants”. You were just never given a simple system that matches your home and your plants.",
            },
        ],
        caption="Stop killing your plants with kindness.",
        tiktok_desc=(
            "If your plant is sad even when you water it, you’re not alone.\n"
            "Most people kill plants by loving them too much.\n"
            "Overwatering, zero light, random “care tips” from the internet.\n"
            "Your plant doesn’t need more attention.\n"
            "It needs the right kind of attention.\n"
            "Leafee builds a care rhythm around your home and your plants.\n"
            "So you water less, stress less, and your plants stop dying for no reason.\n"
            "#plantcare #houseplants #leafee"
        ),
        image_prompts=[
            "selfie of a girl looking frustrated at a drooping houseplant behind her in a small apartment living room, "
            "soft evening light through curtains, cozy but slightly cluttered space, iPhone photo, sharp focus, no bokeh, "
            "natural and lived‑in, high skin texture detail.",
            "Overwatered plant on a windowsill, yellowing leaves and soggy soil in a cheap plastic pot, glass of water and spray bottle nearby, "
            "overcast daylight from the window, iPhone photo, sharp focus, no bokeh, very realistic and relatable scene.",
            "Leafee app open on a phone next to a healthy green plant on a wooden table, notebook and pen nearby, morning light, "
            "airpods case on the table, iPhone photo, sharp focus, no bokeh, warm and inviting.",
            "Same plant in recovery: fresh soil in a terracotta pot on a bright windowsill, simple decor, glass of water, "
            "soft golden hour light coming in, iPhone photo, realistic, lived‑in.",
            "Multiple happy houseplants grouped in a corner of a living room, different pots on a bench and the floor, "
            "cozy rug, throw blanket on a chair, afternoon light, iPhone photo, sharp focus, no bokeh.",
            "Close view of a simple plant care setup: watering can, moisture meter, Leafee app on phone, and a healthy plant on a table, "
            "natural daylight, iPhone photo, realistic and calm mood.",
        ],
    )
    return (
        "You are a content creator for TikTok & Instagram carousels.\n"
        "Generate a hook‑driven carousel about common plant problems and how to fix them, tied to the app Leafee.\n\n"
        "CONTEXT:\n"
        f"- Main problem / angle = '{keyword}' (ex: overwatering, yellow leaves, plants always dying, confusing care advice).\n"
        "- Audience: people who feel bad with plants, beginners, busy people.\n"
        "- Platforms: TikTok & Instagram.\n\n"
        "TONE:\n"
        "- Short, viral hooks.\n"
        "- Talk directly to the viewer (you).\n"
        "- Ultra casual, natural English, no emojis.\n"
        "- Make it feel like a friend exposing the real reason their plants keep dying.\n\n"
        + get_common_instructions()
        + "CAROUSEL STRUCTURE (6 slides):\n"
        "Slide 1: intro_title + intro_body. Use a strong hook like \"Why your plant keeps dying\" or \"This is why your plant looks sad\".\n"
        "Slide 2 (tips[0]): tag = short label (1–3 words) — explain WHAT is really happening to the plant (root cause), not another hook line.\n"
        "Slide 3 (tips[1]): tag = short label (1–3 words) — describe WHAT the viewer usually does wrong that makes it worse.\n"
        "Slide 4 (tips[2]): tag MUST be exactly \"LEAFEE\" — body MUST be about how Leafee fixes this (tracking watering, light, routine, reminders).\n"
        "Slide 5 (tips[3]): tag = short label (1–3 words) — give a clear, simple fix the viewer can try.\n"
        "Slide 6 (tips[4]): tag = short label (1–3 words) — give the mindset shift so the viewer stops thinking they are “bad with plants”.\n\n"
        "TAG RULES:\n"
        "- For slides 2, 3, 5, 6: you are FREE to choose the tags, but they MUST be very short (max 3 words) and feel like punchy labels, not full sentences.\n"
        "- No emojis in tags.\n"
        "- Slide 4 keeps tag \"LEAFEE\" for technical reasons and brand clarity.\n\n"
        "IMPORTANT:\n"
        "- Always keep slide 4 explicitly about Leafee.\n"
        "- Mention Leafee by name in tips[2].\n"
        "- Keep each body to 1–2 short sentences, no newlines.\n\n"
        "IMAGE LOGIC:\n"
        "- Show very realistic, everyday apartments/homes.\n"
        "- Mix sad plants, recovery shots, and at least one clear shot with the Leafee app open next to a plant.\n"
        + get_image_prompts_instruction()
        + "\nExample structure:\n"
        + json.dumps(schema, ensure_ascii=False, indent=2)
    )

