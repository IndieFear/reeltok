import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    # Nouveau SDK officiel Gemini (2025+)
    from google import genai  # type: ignore
    from google.genai import types as genai_types  # type: ignore
except Exception:  # pragma: no cover - au cas où la lib n'est pas installée
    genai = None
    genai_types = None


class GeminiConfigError(RuntimeError):
    """Erreur de configuration Gemini (clé API manquante, SDK absent, etc.)."""


@dataclass
class TipSlide:
    tag: str
    body: str


@dataclass
class CarouselContent:
    intro_title: str
    intro_body: str
    tips: List[TipSlide]
    caption: str
    tiktok_description: str  # Description longue SEO TikTok (phrases courtes), avec mention Leafee
    image_prompts: List[str]  # Prompts Midjourney ultra-détaillés par slide (photo réaliste iPhone)


# Emplacement par défaut du cache (dernier appel réussi)
_DEFAULT_CACHE_PATH = Path(__file__).resolve().parent / "data" / "gemini_last_response.json"


def _get_client() -> "genai.Client":
    """
    Initialise le client Gemini à partir de GEMINI_API_KEY.
    Lève une GeminiConfigError si la configuration est invalide.
    """
    if genai is None:
        raise GeminiConfigError(
            "Le SDK 'google-genai' n'est pas installé. "
            "Ajoute 'google-genai' dans requirements.txt puis installe les dépendances."
        )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiConfigError(
            "Variable d'environnement GEMINI_API_KEY manquante. "
            "Crée un fichier .env avec GEMINI_API_KEY=... ou exporte-la dans ton shell."
        )

    return genai.Client(api_key=api_key)


def _build_prompt(keyword: str, num_slides: int) -> str:
    """
    Construit un prompt détaillé pour obtenir un JSON structuré.
    """
    # On fixe la structure pour 6 slides logiques :
    # - slide 1 : intro (intro_title + intro_body)
    # - slides 2 à 6 : water, light, Leafee, repotting tip, truth/mindset
    schema_example = {
        "intro_title": f"{keyword} care guide",
        "intro_body": (
            "Everyone loves this plant, but most people struggle to keep it happy. "
            "Here is what actually works in real life."
        ),
        "tips": [
            {
                "tag": "WATER",
                "body": "Stop drowning it. Let the top layer of soil dry out before you even think about watering again.",
            },
            {
                "tag": "LIGHT",
                "body": "It wants bright, indirect light. Near a window is perfect, direct harsh sun will just crisp the leaves.",
            },
            {
                "tag": "LEAFEE",
                "body": "This got way easier once I stopped guessing and started tracking my plant care rhythm with Leafee.",
            },
            {
                "tag": "REPOTTING",
                "body": "Repot only when roots are clearly circling the pot or poking out the bottom, not every few months.",
            },
            {
                "tag": "TRUTH",
                "body": "Is it easy? Honestly, yes, if you stop overthinking and follow a simple routine.",
            },
        ],
        "caption": f"{keyword} care made simple 🌿 Save this so you don't have to Google it again.",
        "tiktok_description": (
            "Monstera deliciosa.\n"
            "Big leaves. Big vibe.\n"
            "But most people mess it up.\n"
            "This guide keeps it simple.\n"
            "No overthinking. No plant rules.\n"
            "Watering first.\n"
            "Too much water kills it.\n"
            "Let the soil dry a bit.\n"
            "Then water.\n"
            "And stop.\n"
            "Light matters. A lot.\n"
            "Bright room.\n"
            "Close to a window.\n"
            "No direct sun.\n"
            "No splits on the leaves?\n"
            "It's usually light.\n"
            "Not fertilizer.\n"
            "Not magic.\n"
            "Repot when it feels tight.\n"
            "Roots coming out?\n"
            "Time to size up.\n"
            "Fresh soil. Done.\n"
            "Monsteras grow slow sometimes.\n"
            "That's normal.\n"
            "What helped me most?\n"
            "Having a care plan made for my plant.\n"
            "Not generic advice.\n"
            "That's why I use Leafee.\n"
            "It gives me a personalized care guide, based on my Monstera and my home.\n"
            "Less guessing.\n"
            "Better growth.\n"
            "#monstera #monsteradeliciosa #monsteracare #plantcare #houseplants"
        ),
    }

    return (
        "You are a content creator specialized in short-form social media (TikTok & Instagram carousels).\n"
        "Your goal is to generate complete plant care carousel guides to promote a plant care app called Leafee,\n"
        "in a very natural, non-salesy way.\n\n"
        f"PLANT_TYPE_OR_TOPIC = '{keyword}'. The carousel is a care guide for this exact plant.\n\n"
        "CONTEXT\n"
        "- Platforms: TikTok & Instagram\n"
        "- Audience: beginner to intermediate plant owners\n"
        "- Tone: ultra casual, human, scroll-stopping\n"
        "- Sounds like someone sharing real experience\n"
        "- Short sentences, contractions, sometimes imperfect phrasing\n"
        "- Almost no emojis (0 or 1 max, optional)\n"
        "- Never educational or corporate\n"
        "- Must feel 100% native to social media\n\n"
        "OUTPUT FORMAT (STRICT - CRITICAL)\n"
        "You MUST return ONLY valid JSON. Do NOT use markdown code blocks (no ```json or ```).\n"
        "Do NOT add any text before or after the JSON.\n"
        "Do NOT add explanations, comments, or any other text.\n"
        "Start your response directly with { and end with }.\n"
        "Use EXACTLY this structure and keys:\n"
        + json.dumps(schema_example, ensure_ascii=False, indent=2)
        + "\n\n"
        "MEANING OF FIELDS\n"
        "- intro_title: very short title text shown in the orange bar on slide 1.\n"
        "- intro_body: 1–2 short sentences shown in the white box on slide 1.\n"
        "- tips: array of 5 objects. Each object corresponds to one slide:\n"
        "  - tips[0] = slide 2 (watering)\n"
        "  - tips[1] = slide 3 (light)\n"
        "  - tips[2] = slide 4 (Leafee integration)\n"
        "  - tips[3] = slide 5 (repotting or quick practical tip)\n"
        "  - tips[4] = slide 6 (truth / mindset shift)\n"
        "- tag: ultra short, uppercase label shown in the small orange badge (ex: \"WATER\").\n"
        "- body: text displayed in the white box of that slide.\n"
        "- caption: post caption for the TikTok carousel. MAX 90 characters (TikTok limit).\n"
        "- tiktok_description: LONG SEO description for TikTok (video description). See format below.\n\n"
        "LONG SEO DESCRIPTION (tiktok_description) — STRICT FORMAT\n"
        "Write a long, scrollable description. One short phrase per line (2–6 words often). Use the actual plant name (PLANT_TYPE_OR_TOPIC).\n"
        "1) Open with the plant name alone on one line (e.g. \"Monstera deliciosa.\").\n"
        "2) Hook: 2–4 punchy lines (vibe + \"most people mess it up\" + \"this guide keeps it simple\" / \"no overthinking\").\n"
        "3) Watering: ultra-short tips (e.g. \"Watering first.\" \"Too much water kills it.\" \"Let the soil dry a bit.\" \"Then water.\" \"And stop.\").\n"
        "4) Light: same style (e.g. \"Light matters. A lot.\" \"Bright room.\" \"Close to a window.\" \"No direct sun.\").\n"
        "5) Repotting: short lines (e.g. \"Repot when it feels tight.\" \"Roots coming out?\" \"Time to size up.\" \"Fresh soil. Done.\").\n"
        "6) Truth: normalize (e.g. \"[Plant] grows slow sometimes.\" \"That's normal.\").\n"
        "7) Leafee pitch: \"What helped me most?\" then a care plan for MY plant, not generic advice, then \"That's why I use Leafee.\" "
        "Then one line: \"It gives me a personalized care guide, based on my [Plant] and my home.\" Then \"Less guessing.\" \"Better growth.\"\n"
        "8) End with 4–5 hashtags (e.g. #monstera #monsteradeliciosa #monsteracare #plantcare #houseplants). Use the real plant name in hashtags.\n"
        "Tone: casual, human, no corporate. Almost no emojis. Newline between each phrase (\\n).\n\n"
        "CAROUSEL STRUCTURE (6 SLIDES)\n"
        "Generate content for 6 logical slides following this flow:\n"
        "Slide 1 (intro): announce the plant guide.\n"
        "  - intro_title MUST be exactly: \"{PLANT_TYPE_OR_TOPIC} care guide\" using the real plant name.\n"
        "  - intro_body: 1–2 short sentences about common struggles and what this guide will fix.\n"
        "Slide 2 (water)  -> tips[0]\n"
        "  - tag: \"WATER\" or similar.\n"
        "  - body MUST be about watering (e.g., \"Stop drowning it.\").\n"
        "Slide 3 (light)  -> tips[1]\n"
        "  - tag: \"LIGHT\" or similar.\n"
        "  - body MUST be about light/exposure (e.g., \"It needs that bright spot.\").\n"
        "Slide 4 (Leafee) -> tips[2]\n"
        "  - tag: something like \"ROUTINE\" or \"LEAFEE\".\n"
        "  - body MUST integrate Leafee smoothly, very soft and human (e.g., \"Found my rhythm with this\").\n"
        "  - No hard CTA, no \"download now\", no feature list.\n"
        "Slide 5 (tip)    -> tips[3]\n"
        "  - tag: \"REPOTTING\" or another short practical label.\n"
        "  - body MUST be a quick practical tip (repotting or similar action).\n"
        "Slide 6 (truth)  -> tips[4]\n"
        "  - tag: something like \"TRUTH\" or \"REAL TALK\".\n"
        "  - body MUST address the difficulty/truth (e.g., \"Is it easy? Honestly...\").\n\n"
        "SLIDE TEXT RULES\n"
        "- 1–2 short sentences max per slide body.\n"
        "- Easy to read fast, conversational, no jargon.\n"
        "- Almost no emojis (0 or 1 max in the whole JSON, optional).\n\n"
        "IMPORTANT JSON RULES\n"
        "- Use the PLANT_TYPE_OR_TOPIC value to personalize the text.\n"
        "- intro_title MUST literally contain \"care guide\" with the real plant name.\n"
        "- Generate EXACTLY 5 elements in 'tips'.\n"
        "- 'tag' must be a very short UPPERCASE label (\"WATER\", \"LIGHT\", \"LEAFEE\", \"REPOTTING\", \"TRUTH\", etc.).\n"
        "- tiktok_description MUST follow the long SEO format above (plant name, hook, water, light, repot, truth, Leafee pitch with \"personalized care guide based on my [plant] and my home\", then hashtags).\n"
        "- The JSON must contain NO comments and NO extra text before or after the JSON.\n"
    )


def _repair_incomplete_json(text: str) -> str:
    """
    Essaie de réparer un JSON incomplet en fermant les structures manquantes.
    """
    text = text.strip()
    
    # Compter les accolades ouvertes/fermées
    open_braces = text.count("{")
    close_braces = text.count("}")
    open_brackets = text.count("[")
    close_brackets = text.count("]")
    
    # Vérifier si on est dans une string non fermée
    in_string = False
    escape_next = False
    for i, char in enumerate(text):
        if escape_next:
            escape_next = False
            continue
        if char == "\\":
            escape_next = True
            continue
        if char == '"':
            in_string = not in_string
    
    # Si on est dans une string à la fin, fermer la string
    if in_string:
        text += '"'
    
    # Fermer les tableaux ouverts
    while open_brackets > close_brackets:
        text += "]"
        close_brackets += 1
    
    # Fermer les objets ouverts
    while open_braces > close_braces:
        text += "}"
        close_braces += 1
    
    return text


def _parse_response_to_json(text: str) -> Dict[str, Any]:
    """
    Essaie de parser la réponse du modèle en JSON pur.
    Gère le cas où le modèle renvoie du texte avant/après, du markdown, etc.
    Gère aussi les JSON incomplets (tronqués).
    """
    import re

    original_text = text
    text = text.strip()

    # Essai 1 : JSON direct
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Essai 2 : Extraire depuis un bloc markdown ```json ... ```
    json_block_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
    match = re.search(json_block_pattern, text, re.DOTALL)
    if match:
        candidate = match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Essai 3 : Extraire depuis un bloc markdown simple ``` ... ```
    code_block_pattern = r"```[^`]*?(\{.*?\})[^`]*?```"
    match = re.search(code_block_pattern, text, re.DOTALL)
    if match:
        candidate = match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Essai 4 : Chercher le premier '{' et réparer le JSON si incomplet
    start = text.find("{")
    if start == -1:
        preview = original_text[:500] + "..." if len(original_text) > 500 else original_text
        raise ValueError(
            f"Impossible de trouver du JSON dans la réponse Gemini.\n"
            f"Extrait de la réponse reçue:\n{preview}"
        )

    # Extraire le JSON depuis le premier '{'
    candidate = text[start:]
    
    # Essayer de réparer si incomplet
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # Réparer le JSON incomplet
        repaired = _repair_incomplete_json(candidate)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError as e:
            # Si même réparé ça ne marche pas, afficher l'erreur
            preview = candidate[:500] + "..." if len(candidate) > 500 else candidate
            raise ValueError(
                f"Impossible de parser/réparer le JSON de Gemini.\n"
                f"Erreur: {e}\n"
                f"JSON original (extrait):\n{preview}"
            )


def _load_cached_content(
    keyword: str,
    num_slides: int,
    content_type: str = "care-guide",
    cache_path: Optional[Path] = None,
) -> Optional[CarouselContent]:
    """
    Tente de charger un résultat Gemini mis en cache pour éviter de ré-appeler l'API.
    """
    path = cache_path or _DEFAULT_CACHE_PATH
    if not path.is_file():
        return None

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None

    if data.get("keyword") != keyword or data.get("num_slides") != num_slides or data.get("content_type") != content_type:
        return None

    intro_title = str(data.get("intro_title") or "").strip()
    intro_body = str(data.get("intro_body") or "").strip()
    caption = str(data.get("caption") or "").strip()
    tiktok_description = str(data.get("tiktok_description") or "").strip()

    tips_data = data.get("tips") or []
    tips: List[TipSlide] = []
    for item in tips_data:
        tag = str(item.get("tag") or "").strip()
        body = str(item.get("body") or "").strip()
        if not tag or not body:
            continue
        tips.append(TipSlide(tag=tag, body=body))

    if not intro_title or not intro_body or not caption or not tips:
        return None

    caption = caption[:90] if len(caption) > 90 else caption

    if not tiktok_description:
        tiktok_description = caption + "\nUse Leafee for a personalized care guide."

    image_prompts: List[str] = data.get("image_prompts") or []
    if len(image_prompts) < num_slides:
        image_prompts = list(image_prompts) + [""] * (num_slides - len(image_prompts))

    return CarouselContent(
        intro_title=intro_title,
        intro_body=intro_body,
        tips=tips,
        caption=caption,
        tiktok_description=tiktok_description,
        image_prompts=image_prompts[:num_slides],
    )


def _save_cached_content(
    keyword: str,
    num_slides: int,
    content: CarouselContent,
    content_type: str = "care-guide",
    cache_path: Optional[Path] = None,
) -> None:
    """
    Sauvegarde le dernier résultat Gemini dans un fichier JSON pour les tests.
    """
    path = cache_path or _DEFAULT_CACHE_PATH
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "keyword": keyword,
            "num_slides": num_slides,
            "content_type": content_type,
            "intro_title": content.intro_title,
            "intro_body": content.intro_body,
            "caption": content.caption,
            "tiktok_description": content.tiktok_description,
            "tips": [{"tag": t.tag, "body": t.body} for t in content.tips],
            "image_prompts": content.image_prompts,
        }
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception:
        # En cas d'erreur d'écriture, on ne bloque pas le pipeline.
        pass


def generate_carousel_content(
    keyword: str,
    num_slides: int,
    *,
    content_type: str = "care-guide",
    use_cache: bool = False,
    cache_path: Optional[Path] = None,
    variation_index: int = 0,
    custom_prompt: str | None = None,
) -> CarouselContent:
    """
    Génère le contenu structuré pour un carrousel TikTok :
    - 1 slide d'intro (titre + texte)
    - (num_slides - 1) slides de conseils (tag + texte)
    - un caption global pour le post
    """
    if num_slides < 1:
        raise ValueError("num_slides doit être >= 1")

    # 1) Essayer de charger depuis le cache si demandé (jamais pour les variations ni prompt personnalisé)
    if use_cache and variation_index == 0 and not custom_prompt:
        cached = _load_cached_content(keyword, num_slides, content_type, cache_path=cache_path)
        if cached is not None:
            print("[Gemini] Utilisation du cache local (pas d'appel API).")
            return cached
        else:
            print("[Gemini] Aucun cache valide trouvé, appel API normal…")

    client = _get_client()
    if custom_prompt and custom_prompt.strip():
        try:
            from backend.content_types.registry import build_prompt_for_type
            base_prompt = build_prompt_for_type(content_type, keyword, num_slides, variation_index=variation_index)
        except Exception:
            base_prompt = _build_prompt(keyword=keyword, num_slides=num_slides)
        # Ajouter les indications personnalisées à la fin du prompt
        prompt = f"{base_prompt}\n\n---\n\nINSTRUCTIONS SUPPLÉMENTAIRES:\n{custom_prompt.strip()}"
    else:
        try:
            from backend.content_types.registry import build_prompt_for_type
            prompt = build_prompt_for_type(content_type, keyword, num_slides, variation_index=variation_index)
        except Exception:
            prompt = _build_prompt(keyword=keyword, num_slides=num_slides)

    # Configuration simple, on peut raffiner plus tard
    config = None
    if genai_types is not None:
        config = genai_types.GenerateContentConfig(
            temperature=0.7,  # Légèrement plus bas pour plus de cohérence
            max_output_tokens=8192,  # 7 slides + 6 tips + image_prompts = contenu long
        )

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
        config=config,
    )

    raw_text = getattr(response, "text", None) or "".join(
        part.text for part in getattr(response, "candidates", []) or []
    )
    if not raw_text:
        raise RuntimeError("Réponse vide de Gemini.")

    # Debug : afficher un extrait de la réponse pour diagnostiquer
    debug_preview = raw_text[:200] + "..." if len(raw_text) > 200 else raw_text
    print(f"[DEBUG] Extrait de la réponse Gemini (premiers 200 chars): {debug_preview}")

    try:
        data = _parse_response_to_json(raw_text)
    except ValueError as e:
        # Afficher l'erreur complète pour debug
        print(f"[DEBUG] Erreur de parsing JSON. Réponse complète:\n{raw_text}")
        raise

    intro_title = str(data.get("intro_title") or "").strip()
    intro_body = str(data.get("intro_body") or "").strip()
    caption = str(data.get("caption") or "").strip()

    tips_raw = data.get("tips") or []
    tips: List[TipSlide] = []
    for item in tips_raw:
        tag = str(item.get("tag") or "").strip()
        body = str(item.get("body") or "").strip()
        if not tag or not body:
            continue
        tips.append(TipSlide(tag=tag, body=body))

    # Sécurité : au moins 1 tip
    if not tips:
        tips.append(
            TipSlide(
                tag="TIP",
                body="Keep your plant in bright, indirect light and avoid overwatering.",
            )
        )

    # Ajuster le nombre de tips au nombre de slides demandé
    desired_tips = max(num_slides - 1, 0)
    if desired_tips == 0:
        tips = []
    elif len(tips) > desired_tips:
        tips = tips[:desired_tips]
    elif len(tips) < desired_tips:
        # Dupliquer en boucle si le modèle n'en a pas donné assez
        while len(tips) < desired_tips:
            tips.append(tips[len(tips) % len(tips)])

    if not intro_title:
        intro_title = keyword.title()
    if not intro_body:
        intro_body = f"Here are some quick tips about {keyword}."
    if not caption:
        caption = f"{keyword} made simple 🌿 Save this post for later!"
    caption = caption[:90] if len(caption) > 90 else caption

    tiktok_description = str(data.get("tiktok_description") or "").strip()
    if not tiktok_description:
        tiktok_description = (
            f"{keyword} care tips.\n"
            "Water. Light. Routine.\n"
            "Use Leafee for a personalized care guide.\n"
            "Save this carousel."
        )

    # image_prompts: prompts Midjourney ultra-détaillés par slide
    image_prompts_raw = data.get("image_prompts") or []
    image_prompts: List[str] = []
    for i in range(num_slides):
        if i < len(image_prompts_raw) and image_prompts_raw[i]:
            p = str(image_prompts_raw[i]).strip()
            if p:
                image_prompts.append(p)
                continue
        image_prompts.append("")  # fallback vide

    content = CarouselContent(
        intro_title=intro_title,
        intro_body=intro_body,
        tips=tips,
        caption=caption,
        tiktok_description=tiktok_description,
        image_prompts=image_prompts,
    )

    # Sauvegarder en cache pour les prochains tests (jamais pour les variations)
    if variation_index == 0:
        _save_cached_content(keyword, num_slides, content, content_type=content_type, cache_path=cache_path)

    return content


__all__ = ["TipSlide", "CarouselContent", "GeminiConfigError", "generate_carousel_content"]

