from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Iterable, Tuple

from PIL import Image, ImageDraw, ImageFont

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Flags requis pour Chromium dans Docker/Railway (évite les blocages sur /dev/shm)
CHROMIUM_DOCKER_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
]
PLAYWRIGHT_TIMEOUT_MS = int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", "30000"))

ROOT = Path(__file__).resolve().parent
DEFAULT_INTRO_TEMPLATE = ROOT / "backend" / "templates" / "intro" / "leafee-v2.html"
DEFAULT_TIP_TEMPLATE = ROOT / "backend" / "templates" / "tip" / "leafee-v2.html"

# Dimensions cibles pour TikTok (9:16)
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

# Couleurs (approx) inspirées de ton exemple
ORANGE = (255, 138, 61, 255)  # bandeau
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """
    Charge TikTok Sans si disponible, sinon une police par défaut.

    L'ordre de recherche :
    - variable d'env TIKTOK_FONT_PATH
    - assets/fonts/TikTokSans-Regular.ttf (chemin projet)
    - police par défaut PIL
    """
    # Permet d'agrandir/réduire facilement la taille du texte
    # via une variable d'environnement, sans changer le code.
    try:
        scale = float(os.getenv("FONT_SCALE", "1.0"))
    except ValueError:
        scale = 1.0
    scaled_size = max(1, int(size * scale))

    font_paths = []

    env_path = os.getenv("TIKTOK_FONT_PATH")
    if env_path:
        font_paths.append(Path(env_path))

    project_root = Path(__file__).resolve().parent
    font_paths.append(project_root / "assets" / "fonts" / "TikTokSans-Regular.ttf")

    for path in font_paths:
        try:
            if path.is_file():
                return ImageFont.truetype(str(path), size=scaled_size)
        except Exception:
            continue

    # Fallback
    return ImageFont.load_default()


def _resize_to_target(image: Image.Image) -> Image.Image:
    """
    Recadre l'image d'entrée en 9:16 (1080x1920) en gardant le centre.
    """
    w, h = image.size
    target_ratio = TARGET_WIDTH / TARGET_HEIGHT
    current_ratio = w / h

    if abs(current_ratio - target_ratio) < 1e-3:
        return image.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)

    if current_ratio > target_ratio:
        # Trop large -> couper les côtés
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        box = (left, 0, left + new_w, h)
    else:
        # Trop haut -> couper en haut/bas
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        box = (0, top, w, top + new_h)

    cropped = image.crop(box)
    return cropped.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)


def _draw_rounded_rectangle(
    draw: ImageDraw.ImageDraw,
    box: Tuple[int, int, int, int],
    radius: int,
    fill: Tuple[int, int, int, int],
) -> None:
    """
    Dessine un rectangle arrondi.
    """
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def _wrap_text_to_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
) -> str:
    """
    Coupe le texte en lignes pour tenir dans max_width.
    """
    words = text.split()
    if not words:
        return ""

    lines = []
    current_line: list[str] = []

    for word in words:
        candidate = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), candidate, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width or not current_line:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)


def _draw_text_centered_in_box(
    draw: ImageDraw.ImageDraw,
    box: Tuple[int, int, int, int],
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: Tuple[int, int, int, int],
) -> None:
    x0, y0, x1, y1 = box
    w = x1 - x0
    h = y1 - y0

    wrapped = _wrap_text_to_width(draw, text, font, max_width=int(w * 0.9))
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, align="center")
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    tx = x0 + (w - tw) // 2
    ty = y0 + (h - th) // 2

    draw.multiline_text((tx, ty), wrapped, font=font, fill=fill, align="center")


def create_intro_image(
    background_path: str | Path,
    title: str,
    body: str,
    output_path: str | Path,
    template_html_path: str | Path | None = None,
    title_bg_color: str | None = None,
) -> Path:
    """
    Crée l'image d'intro du carousel en utilisant le template HTML si disponible.
    Sinon, fallback sur la méthode PIL classique.
    """
    background_path = Path(background_path)
    output_path = Path(output_path)

    print("[intro] Création slide 1…")

    # Essayer d'utiliser le template HTML si Playwright est disponible
    if PLAYWRIGHT_AVAILABLE:
        html_template = template_html_path or DEFAULT_INTRO_TEMPLATE
        print(f"[intro] Playwright disponible, tentative avec template HTML: {html_template}")
        if html_template.is_file():
            try:
                return _create_intro_image_from_html(
                    background_path=background_path,
                    title=title,
                    body=body,
                    output_path=output_path,
                    template_html_path=html_template,
                    title_bg_color=title_bg_color,
                )
            except Exception as e:
                print(f"[WARN] Erreur lors du rendu HTML, fallback sur PIL : {e}")
                # Continue avec la méthode PIL ci-dessous
        else:
            print(f"[intro] Template HTML introuvable: {html_template}, fallback PIL.")
    else:
        print("[intro] Playwright non disponible, fallback PIL.")

    # Fallback : méthode PIL classique (code existant)
    return _create_intro_image_pil(
        background_path=background_path,
        title=title,
        body=body,
        output_path=output_path,
        title_bg_color=title_bg_color,
    )


def _create_intro_image_from_html(
    background_path: Path,
    title: str,
    body: str,
    output_path: Path,
    template_html_path: Path,
    title_bg_color: str | None = None,
) -> Path:
    """
    Génère l'image depuis le template HTML en utilisant Playwright.
    """
    # Lire le template HTML
    html_content = template_html_path.read_text(encoding="utf-8")

    # Convertir les chemins absolus en file:// URLs pour Playwright
    bg_url = background_path.resolve().as_uri()

    html_content = html_content.replace(
        'src="https://images.unsplash.com/photo-1700213040197-d13ed110bfb9?q=80&w=928&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"',
        f'src="{bg_url}"',
    )

    # Remplacer le titre
    html_content = html_content.replace(
        "Monstera Deliciosa Care Guide",
        title,
    )

    # Remplacer le texte du body (apostrophe droite ' ou typographique ')
    _body_placeholder = "Everyone loves the swiss cheese look but they can be dramatic. Here's what actually works"
    html_content = html_content.replace(_body_placeholder, body).replace(
        _body_placeholder.replace("'", "\u2019"), body
    )

    print("[intro-html] title_bg_color reçu:", title_bg_color)
    # Optionnel : couleur du bandeau titre (remplace le orange par la couleur choisie)
    if title_bg_color:
        # Intro templates utilisent actuellement #FF933D
        html_content = html_content.replace(
            "background-color: #FF933D;",
            f"background-color: {title_bg_color};",
        )

    # Retirer le scale pour avoir la vraie taille 1080x1920
    html_content = html_content.replace(
        "transform: scale(0.4);",
        "transform: scale(1.0);",
    )

    return _render_html_screenshot(html_content, output_path, temp_prefix="_temp_intro")


def _parse_hex_color(value: str | None, fallback: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    """
    Convertit une couleur hexadécimale de type #RRGGBB en tuple RGBA.
    Retourne fallback si le format est invalide.
    """
    if not value or not isinstance(value, str):
        return fallback
    v = value.strip()
    if not (v.startswith("#") and len(v) == 7):
        return fallback
    try:
        r = int(v[1:3], 16)
        g = int(v[3:5], 16)
        b = int(v[5:7], 16)
        return (r, g, b, 255)
    except ValueError:
        return fallback


def _create_intro_image_pil(
    background_path: Path,
    title: str,
    body: str,
    output_path: Path,
    title_bg_color: str | None = None,
) -> Path:
    """
    Méthode PIL classique (fallback si HTML non disponible).
    """
    img = Image.open(background_path).convert("RGBA")
    img = _resize_to_target(img)

    draw = ImageDraw.Draw(img, "RGBA")

    # Marges de sécurité TikTok (éviter barres haut/bas)
    bottom_safe = int(TARGET_HEIGHT * 0.08)

    print("[intro-pil] title_bg_color reçu:", title_bg_color)
    # =========================
    # 1. Tag orange (titre)
    # =========================
    title_font = _load_font(size=80)
    tag_text = title.upper()
    tag_bbox = draw.textbbox((0, 0), tag_text, font=title_font)
    tag_text_w = tag_bbox[2] - tag_bbox[0]
    tag_text_h = tag_bbox[3] - tag_bbox[1]

    tag_pad_x = 40
    tag_pad_y = 20
    tag_w = tag_text_w + 2 * tag_pad_x
    tag_h = tag_text_h + 2 * tag_pad_y

    # Position proche du bas (comme dans le template HTML)
    overlay_center_y = int(TARGET_HEIGHT * 0.70)
    tag_x0 = (TARGET_WIDTH - tag_w) // 2
    tag_y0 = overlay_center_y - tag_h // 2
    tag_box = (tag_x0, tag_y0, tag_x0 + tag_w, tag_y0 + tag_h)

    tag_color = _parse_hex_color(title_bg_color, ORANGE)
    _draw_rounded_rectangle(draw, tag_box, radius=24, fill=tag_color)

    tag_text_x = tag_x0 + tag_pad_x
    tag_text_y = tag_y0 + tag_pad_y
    draw.text((tag_text_x, tag_text_y), tag_text, font=title_font, fill=WHITE)

    # =========================
    # 2. Lignes blanches façon "capsules"
    # =========================
    body_font = _load_font(size=56)

    # Découper le texte en lignes raisonnables
    max_body_width = int(TARGET_WIDTH * 0.74)  # proche du MAX_WIDTH=800 dans le template HTML
    wrapped = _wrap_text_to_width(draw, body, body_font, max_width=max_body_width)
    lines = [line for line in wrapped.split("\n") if line.strip()]

    line_pad_x = 28
    line_pad_y = 14

    # Calcul des largeurs de lignes
    line_boxes = []
    for line in lines:
        lb = draw.textbbox((0, 0), line, font=body_font)
        lw = lb[2] - lb[0]
        lh = lb[3] - lb[1]
        line_boxes.append((line, lw, lh))

    # Harmoniser la largeur de lignes proches (effet "gooey" visuel)
    widths = [lw + 2 * line_pad_x for (_, lw, _) in line_boxes]
    threshold = 100
    for i in range(len(widths) - 1):
        if abs(widths[i] - widths[i + 1]) < threshold:
            max_w = max(widths[i], widths[i + 1])
            widths[i] = max_w
            widths[i + 1] = max_w

    # Positionner les lignes sous le tag, légèrement au-dessus du bas
    start_y = tag_box[3] + 30
    overlap = 10  # chevauchement léger des rectangles (comme margin négatif)

    for idx, (line, lw, lh) in enumerate(line_boxes):
        rect_w = widths[idx]
        rect_h = lh + 2 * line_pad_y
        x0 = (TARGET_WIDTH - rect_w) // 2
        y0 = start_y + idx * (rect_h - overlap)

        # Ne pas descendre trop bas (respect du bottom_safe)
        if y0 + rect_h > TARGET_HEIGHT - bottom_safe:
            break

        line_box = (x0, y0, x0 + rect_w, y0 + rect_h)
        _draw_rounded_rectangle(draw, line_box, radius=30, fill=WHITE)

        text_x = x0 + line_pad_x
        text_y = y0 + line_pad_y
        draw.text((text_x, text_y), line, font=body_font, fill=BLACK)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img = img.convert("RGB")
    img.save(output_path, format="JPEG", quality=95)
    return output_path


def create_tip_image(
    background_path: str | Path,
    tag: str,
    body: str,
    output_path: str | Path,
    template_html_path: str | Path | None = None,
    title_bg_color: str | None = None,
) -> Path:
    """
    Crée une slide de conseil.
    - Si possible, utilise le template HTML leafee-v2 via Playwright.
    - Sinon, fallback sur la méthode PIL classique (label + bloc blanc).
    """
    background_path = Path(background_path)
    output_path = Path(output_path)

    print("[tip] Création slide conseil…")

    # Essayer d'utiliser le template HTML si Playwright est disponible
    if PLAYWRIGHT_AVAILABLE:
        html_template = template_html_path or DEFAULT_TIP_TEMPLATE
        print(f"[tip] Playwright disponible, tentative avec template HTML: {html_template}")
        if html_template.is_file():
            try:
                return _create_tip_image_from_html(
                    background_path=background_path,
                    tag=tag,
                    body=body,
                    output_path=output_path,
                    template_html_path=html_template,
                    title_bg_color=title_bg_color,
                )
            except Exception as e:
                print(f"[WARN] Erreur lors du rendu HTML (slideX), fallback sur PIL : {e}")
                # Continue avec la méthode PIL ci-dessous
        else:
            print(f"[tip] Template HTML slideX introuvable: {html_template}, fallback PIL.")
    else:
        print("[tip] Playwright non disponible, fallback PIL.")

    # Fallback PIL classique
    return _create_tip_image_pil(
        background_path=background_path,
        tag=tag,
        body=body,
        output_path=output_path,
        title_bg_color=title_bg_color,
    )


def _create_tip_image_from_html(
    background_path: Path,
    tag: str,
    body: str,
    output_path: Path,
    template_html_path: Path,
    title_bg_color: str | None = None,
) -> Path:
    """
    Génère une slide de conseil depuis le template HTML slideX via Playwright.
    """
    html_content = template_html_path.read_text(encoding="utf-8")

    bg_url = background_path.resolve().as_uri()

    # Remplacer l'image de fond
    html_content = html_content.replace(
        'src="https://images.unsplash.com/photo-1700213040197-d13ed110bfb9?q=80&w=928&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"',
        f'src="{bg_url}"',
    )

    # Remplacer le titre (tag)
    html_content = html_content.replace(
        "Monstera Deliciosa Care Guide",
        tag.upper(),
    )

    # Remplacer le texte du body (apostrophe droite ' ou typographique ')
    _body_placeholder = "Everyone loves the swiss cheese look but they can be dramatic. Here's what actually works"
    html_content = html_content.replace(_body_placeholder, body).replace(
        _body_placeholder.replace("'", "\u2019"), body
    )

    print("[tip-html] title_bg_color reçu:", title_bg_color)
    # Optionnel : couleur du bandeau/tag (remplace le orange par la couleur choisie)
    if title_bg_color:
        # Tip template utilise actuellement #FF8845 comme orange
        html_content = html_content.replace(
            "background-color: #FF8845;",
            f"background-color: {title_bg_color};",
        )

    # Retirer le scale pour la taille réelle
    html_content = html_content.replace(
        "transform: scale(0.4);",
        "transform: scale(1.0);",
    )

    return _render_html_screenshot(html_content, output_path, temp_prefix="_temp_tip")


def _render_html_screenshot(html_content: str, output_path: Path, temp_prefix: str) -> Path:
    """Rend un fichier HTML en JPEG via Playwright (compatible Docker)."""
    temp_html = output_path.parent / f"{temp_prefix}_{output_path.stem}.html"
    temp_html.write_text(html_content, encoding="utf-8")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=CHROMIUM_DOCKER_ARGS)
            try:
                page = browser.new_page(viewport={"width": 1080, "height": 1920})
                page.goto(
                    temp_html.resolve().as_uri(),
                    timeout=PLAYWRIGHT_TIMEOUT_MS,
                    wait_until="load",
                )
                page.wait_for_timeout(1000)
                page.locator(".phone-container").screenshot(
                    path=str(output_path),
                    type="jpeg",
                    quality=95,
                    timeout=PLAYWRIGHT_TIMEOUT_MS,
                )
            finally:
                browser.close()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"[playwright] Screenshot OK: {output_path.name}")
        return output_path
    finally:
        if temp_html.exists():
            temp_html.unlink()


def _create_tip_image_pil(
    background_path: Path,
    tag: str,
    body: str,
    output_path: Path,
    title_bg_color: str | None = None,
) -> Path:
    """
    Méthode PIL classique pour les slides de conseil.
    """
    img = Image.open(background_path).convert("RGBA")
    img = _resize_to_target(img)
    draw = ImageDraw.Draw(img, "RGBA")

    top_safe = int(TARGET_HEIGHT * 0.10)
    bottom_safe = int(TARGET_HEIGHT * 0.10)

    print("[tip-pil] title_bg_color reçu:", title_bg_color)
    # Petit label tag en haut
    label_width = int(TARGET_WIDTH * 0.30)
    label_height = int(TARGET_HEIGHT * 0.06)
    label_x0 = (TARGET_WIDTH - label_width) // 2
    label_y0 = top_safe + int(TARGET_HEIGHT * 0.04)
    label_box = (label_x0, label_y0, label_x0 + label_width, label_y0 + label_height)

    label_color = _parse_hex_color(title_bg_color, ORANGE)
    _draw_rounded_rectangle(draw, label_box, radius=25, fill=label_color)
    tag_font = _load_font(size=64)
    _draw_text_centered_in_box(draw, label_box, tag.upper(), tag_font, WHITE)

    # Bloc texte principal
    body_width = int(TARGET_WIDTH * 0.88)
    body_height = int(TARGET_HEIGHT * 0.22)
    body_x0 = (TARGET_WIDTH - body_width) // 2
    body_y0 = label_box[3] + int(TARGET_HEIGHT * 0.04)
    body_box = (body_x0, body_y0, body_x0 + body_width, body_y0 + body_height)

    _draw_rounded_rectangle(draw, body_box, radius=40, fill=WHITE)

    body_font = _load_font(size=56)
    _draw_text_centered_in_box(draw, body_box, body, body_font, BLACK)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img = img.convert("RGB")
    img.save(output_path, format="JPEG", quality=95)
    return output_path


__all__ = ["create_intro_image", "create_tip_image", "TARGET_WIDTH", "TARGET_HEIGHT"]

