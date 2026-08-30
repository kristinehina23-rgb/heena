#!/usr/bin/env python3
"""Render 1920x1080 slide PNGs with TrueType CJK (not 等线/OTTO)."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
W, H = 1920, 1080

GREEN = (0, 86, 31)
GREEN_DEEP = (0, 34, 16)
GREEN_MID = (10, 107, 45)
CREAM = (246, 241, 228)
PAPER = (251, 250, 246)
GOLD = (210, 152, 101)
GOLD_SOFT = (228, 194, 154)
INK = (34, 31, 27)
MUTED = (92, 86, 76)
WHITE = (255, 255, 255)
RED = (116, 0, 3)

SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
SANS_MED = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"
SANS_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
SERIF_BOLD = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
SC = 2  # Noto CJK collection: JP, KR, SC, TC, HK


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size, index=SC)


def load_json(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def cover_image(path: Path, size=(W, H), darken=0.42) -> Image.Image:
    im = Image.open(path).convert("RGB")
    src_w, src_h = im.size
    scale = max(size[0] / src_w, size[1] / src_h)
    im = im.resize((int(src_w * scale), int(src_h * scale)), Image.Resampling.LANCZOS)
    left = (im.width - size[0]) // 2
    top = (im.height - size[1]) // 2
    im = im.crop((left, top, left + size[0], top + size[1]))
    im = ImageEnhance.Brightness(im).enhance(darken)
    im = ImageEnhance.Color(im).enhance(0.85)
    return im


def crop_cover(path: Path, size: tuple[int, int]) -> Image.Image:
    im = Image.open(path).convert("RGB")
    src_w, src_h = im.size
    scale = max(size[0] / src_w, size[1] / src_h)
    im = im.resize((int(src_w * scale), int(src_h * scale)), Image.Resampling.LANCZOS)
    left = (im.width - size[0]) // 2
    top = (im.height - size[1]) // 2
    return im.crop((left, top, left + size[0], top + size[1]))


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        if not para:
            lines.append("")
            continue
        current = ""
        for ch in para:
            trial = current + ch
            if draw.textlength(trial, font=fnt) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = ch
        if current:
            lines.append(current)
    return lines


def draw_text(draw, xy, text, fnt, fill, anchor="lt"):
    draw.text(xy, text, font=fnt, fill=fill, anchor=anchor)


def paste_emblem(base: Image.Image, path: Path, xy: tuple[int, int], size: int = 72) -> None:
    if not path.exists():
        return
    mark = Image.open(path).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    base.paste(mark, xy, mark)


def brand_bar(base: Image.Image, meta: dict, light: bool, right: str, page: int, total: int) -> None:
    draw = ImageDraw.Draw(base)
    title_fill = GREEN if light else CREAM
    muted = MUTED if light else (220, 214, 198)
    emblem = ROOT / ("assets/emblem-green.png" if light else "assets/emblem-white.png")
    paste_emblem(base, emblem, (56, 28), 56)
    draw_text(draw, (128, 32), meta["university"], font(SERIF_BOLD, 28), title_fill)
    draw_text(draw, (128, 68), meta["universityEn"].upper(), font(SANS, 16), muted)
    draw_text(draw, (1860, 56), right, font(SANS_MED, 22), GOLD if not light else GREEN, anchor="rm")
    draw_text(draw, (56, 1040), meta["motto"], font(SANS, 18), muted)
    draw_text(draw, (1864, 1040), f"{page:02d} / {total:02d}", font(SANS, 18), muted, anchor="rm")


def render_cover(slide, meta, photos, page, total) -> Image.Image:
    base = cover_image(ROOT / slide["background"], darken=0.55)
    veil = Image.new("RGBA", (W, H), (0, 24, 12, 0))
    vd = ImageDraw.Draw(veil)
    for x in range(W):
        t = x / W
        a = int(210 * (1 - t * 0.55))
        vd.line([(x, 0), (x, H)], fill=(0, 28, 14, a))
    base = Image.alpha_composite(base.convert("RGBA"), veil).convert("RGB")
    draw = ImageDraw.Draw(base)
    brand_bar(base, meta, False, slide["kicker"], page, total)
    draw.rectangle((88, 690, 208, 694), fill=GOLD)
    title_font = font(SERIF_BOLD, 72)
    lines = wrap(draw, slide["title"], title_font, 1400)
    y = 720
    for line in lines:
        draw_text(draw, (88, y), line, title_font, CREAM)
        y += 88
    draw_text(draw, (88, y + 8), slide["subtitle"], font(SANS_MED, 30), GOLD_SOFT)
    draw_text(draw, (88, y + 62), slide["speaker"], font(SANS, 28), CREAM)
    return base


def cream_bg() -> Image.Image:
    return Image.new("RGB", (W, H), PAPER)


def render_quote(slide, meta, photos, page, total) -> Image.Image:
    base = cream_bg()
    draw = ImageDraw.Draw(base)
    brand_bar(base, meta, True, slide["kicker"], page, total)
    draw_text(draw, (88, 150), slide["kicker"], font(SANS_MED, 22), GOLD)
    title_font = font(SERIF_BOLD, 60)
    draw_text(draw, (88, 196), slide["title"], title_font, GREEN)
    body_font = font(SANS, 30)
    y = 300
    for line in wrap(draw, slide["body"], body_font, 1700):
        draw_text(draw, (88, y), line, body_font, INK)
        y += 48
    cards = slide["points"]
    gap = 28
    card_w = (W - 176 - gap * 2) // 3
    card_h = 220
    top = 760
    for i, text in enumerate(cards):
        x = 88 + i * (card_w + gap)
        draw.rectangle((x, top, x + card_w, top + card_h), fill=WHITE)
        draw.rectangle((x, top, x + 8, top + card_h), fill=GOLD)
        draw_text(draw, (x + 32, top + 28), f"0{i + 1}", font(SANS_MED, 24), GOLD)
        pf = font(SANS_MED, 28)
        yy = top + 78
        for line in wrap(draw, text, pf, card_w - 56):
            draw_text(draw, (x + 32, yy), line, pf, INK)
            yy += 42
    return base


def render_map(slide, meta, photos, page, total) -> Image.Image:
    base = cream_bg()
    draw = ImageDraw.Draw(base)
    brand_bar(base, meta, True, slide["kicker"], page, total)
    draw_text(draw, (88, 150), slide["kicker"], font(SANS_MED, 22), GOLD)
    draw_text(draw, (88, 196), slide["title"], font(SERIF_BOLD, 56), GREEN)
    gap = 28
    card_w = (W - 176 - gap * 2) // 3
    card_h = 620
    top = 320
    for i, card in enumerate(slide["cards"]):
        x = 88 + i * (card_w + gap)
        photo = crop_cover(ROOT / card["photo"], (card_w, card_h))
        base.paste(photo, (x, top))
        overlay = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        for yy in range(card_h):
            a = int(40 + 180 * (yy / card_h) ** 1.4)
            od.line([(0, yy), (card_w, yy)], fill=(0, 22, 10, a))
        base.paste(Image.alpha_composite(photo.convert("RGBA"), overlay).convert("RGB"), (x, top))
        draw = ImageDraw.Draw(base)
        draw_text(draw, (x + 36, top + card_h - 170), card["num"], font(SANS_MED, 26), GOLD)
        draw_text(draw, (x + 36, top + card_h - 128), card["title"], font(SERIF_BOLD, 40), CREAM)
        draw_text(draw, (x + 36, top + card_h - 68), card["line"], font(SANS, 24), CREAM)
    return base


def photo_panel(path: Path, spec: dict, size: tuple[int, int]) -> Image.Image:
    panel = crop_cover(path, size)
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for yy in range(size[1] - 220, size[1]):
        a = int(220 * ((yy - (size[1] - 220)) / 220))
        od.line([(0, yy), (size[0], yy)], fill=(0, 18, 8, a))
    panel = Image.alpha_composite(panel.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(panel)
    if spec.get("usingFallback"):
        draw.rectangle((size[0] - 290, 20, size[0] - 20, 58), fill=RED)
        draw_text(draw, (size[0] - 155, 39), "校园氛围图 · 待换原照", font(SANS, 16), CREAM, anchor="mm")
    draw_text(draw, (24, size[1] - 92), spec["label"], font(SANS_MED, 18), GOLD_SOFT)
    cap_font = font(SANS_MED, 24)
    yy = size[1] - 62
    for line in wrap(draw, spec["caption"], cap_font, size[0] - 48):
        draw_text(draw, (24, yy), line, cap_font, CREAM)
        yy += 32
    return panel.convert("RGB")


def render_experience(slide, meta, photos, page, total) -> Image.Image:
    base = cream_bg()
    draw = ImageDraw.Draw(base)
    brand_bar(base, meta, True, f"{meta['series']} · {meta['year']}", page, total)
    left = 56
    col_w = 820
    title_font = font(SERIF_BOLD, 40)
    y = 130
    for line in wrap(draw, slide["title"], title_font, col_w):
        draw_text(draw, (left, y), line, title_font, GREEN)
        y += 54
    y += 10
    label = slide["greenTitle"]
    lw = int(draw.textlength(label, font=font(SANS_MED, 22))) + 36
    draw.rectangle((left, y, left + lw, y + 44), fill=(0, 86, 31, 255))
    # pillow RGB image: use a light green chip
    draw.rectangle((left, y, left + lw, y + 44), fill=(226, 236, 226))
    draw_text(draw, (left + 16, y + 8), label, font(SANS_MED, 22), GREEN)
    y += 70
    stat_w = 390
    for i, (n, lab) in enumerate(((slide["n1"], slide["l1"]), (slide["n2"], slide["l2"]))):
        x = left + i * (stat_w + 20)
        draw.rectangle((x, y, x + stat_w, y + 130), fill=WHITE)
        draw.rectangle((x, y, x + 8, y + 130), fill=GOLD)
        draw_text(draw, (x + 28, y + 16), n, font(SERIF_BOLD, 56), GREEN)
        draw_text(draw, (x + 28, y + 84), lab, font(SANS, 22), MUTED)
    y += 160
    draw.rectangle((left, y, left + col_w, 1000), fill=GREEN)
    qf = font(SERIF_BOLD, 30)
    yy = y + 36
    for line in wrap(draw, slide["whiteTitle"], qf, col_w - 64):
        draw_text(draw, (left + 32, yy), line, qf, CREAM)
        yy += 44
    bf = font(SANS, 24)
    yy += 10
    for line in wrap(draw, slide["body"], bf, col_w - 64):
        draw_text(draw, (left + 32, yy), line, bf, (236, 230, 214))
        yy += 40

    p1 = photos[slide["image1"]]
    p2 = photos[slide["image2"]]
    pw, ph = 470, 860
    panel_top = 120
    x1, x2 = 920, 1418
    base.paste(photo_panel(Path(p1["resolvedAbs"]), p1, (pw, ph)), (x1, panel_top))
    base.paste(photo_panel(Path(p2["resolvedAbs"]), p2, (pw, ph)), (x2, panel_top))
    return base


def render_advice(slide, meta, photos, page, total) -> Image.Image:
    base = cream_bg()
    draw = ImageDraw.Draw(base)
    brand_bar(base, meta, True, slide["kicker"], page, total)
    draw_text(draw, (88, 150), slide["kicker"], font(SANS_MED, 22), GOLD)
    title_font = font(SERIF_BOLD, 50)
    y = 196
    for line in wrap(draw, slide["title"], title_font, 1700):
        draw_text(draw, (88, y), line, title_font, GREEN)
        y += 64
    gap = 28
    card_w = (W - 176 - gap * 2) // 3
    top = 360
    card_h = 620
    for i, item in enumerate(slide["items"]):
        x = 88 + i * (card_w + gap)
        draw.rectangle((x, top, x + card_w, top + card_h), fill=WHITE)
        draw.rectangle((x, top, x + card_w, top + 8), fill=GOLD)
        draw_text(draw, (x + 36, top + 36), item["n"], font(SANS_MED, 26), GOLD)
        hf = font(SERIF_BOLD, 34)
        yy = top + 90
        for line in wrap(draw, item["title"], hf, card_w - 72):
            draw_text(draw, (x + 36, yy), line, hf, GREEN)
            yy += 50
        bf = font(SANS, 24)
        yy += 16
        for line in wrap(draw, item["body"], bf, card_w - 72):
            draw_text(draw, (x + 36, yy), line, bf, INK)
            yy += 40
    return base


def render_close(slide, meta, photos, page, total) -> Image.Image:
    base = cover_image(ROOT / slide["background"], darken=0.5)
    veil = Image.new("RGBA", (W, H), (0, 28, 14, 150))
    base = Image.alpha_composite(base.convert("RGBA"), veil).convert("RGB")
    draw = ImageDraw.Draw(base)
    brand_bar(base, meta, False, slide["kicker"], page, total)
    draw.rectangle((88, 690, 208, 694), fill=GOLD)
    title_font = font(SERIF_BOLD, 64)
    y = 720
    for line in wrap(draw, slide["title"], title_font, 1500):
        draw_text(draw, (88, y), line, title_font, CREAM)
        y += 80
    draw_text(draw, (88, y + 10), slide["body"], font(SANS_MED, 30), GOLD_SOFT)
    draw_text(draw, (88, y + 64), slide["speaker"], font(SANS, 28), CREAM)
    return base


RENDERERS = {
    "cover": render_cover,
    "quote": render_quote,
    "map": render_map,
    "experience": render_experience,
    "advice": render_advice,
    "close": render_close,
}


def render_all(photos: dict, out_dir: Path) -> list[Path]:
    content = load_json("content.json")
    meta = content["meta"]
    slides = content["slides"]
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, slide in enumerate(slides, start=1):
        fn = RENDERERS[slide["kind"]]
        im = fn(slide, meta, photos, i, len(slides))
        dest = out_dir / f"slide-{i:02d}.png"
        im = im.convert("RGB")
        im.save(dest, "PNG", optimize=True)
        paths.append(dest)
        print(f"rendered {dest.name}", flush=True)
    return paths
