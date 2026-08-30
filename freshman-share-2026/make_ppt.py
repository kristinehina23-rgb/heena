#!/usr/bin/env python3
"""Assemble a presentable 16:9 PPTX from the rendered slides."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.util import Inches

ROOT = Path(__file__).resolve().parent
CONTENT = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
SLIDE_DIR = ROOT / "outputs" / "slides"
OUTPUTS = ROOT / "outputs"
PPTX_NAME = "喜娜_中大本科新生分享_丰富经历照片终版_2026.pptx"
ALIAS = "Heena-SYSU-Freshman-Share-2026.pptx"

WIDE = Inches(13.333333)
HIGH = Inches(7.5)


def jpeg_bytes(png_path: Path) -> bytes:
    im = Image.open(png_path).convert("RGB")
    buf = BytesIO()
    im.save(buf, "JPEG", quality=90, optimize=True)
    return buf.getvalue()


def build() -> Path:
    pngs = sorted(SLIDE_DIR.glob("slide-0*.png"))
    if len(pngs) != 9:
        raise SystemExit(f"expected 8 slide PNGs, found {len(pngs)}")

    prs = Presentation()
    prs.slide_width = WIDE
    prs.slide_height = HIGH
    blank = prs.slide_layouts[6]

    for i, (png, data) in enumerate(zip(pngs, CONTENT["slides"]), start=1):
        slide = prs.slides.add_slide(blank)
        pic = slide.shapes.add_picture(BytesIO(jpeg_bytes(png)), 0, 0, WIDE, HIGH)
        pic.name = f"slide-{i:02d}"
        slide.notes_slide.notes_text_frame.text = data.get("notes", "")

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    dest = OUTPUTS / PPTX_NAME
    prs.save(dest)
    payload = dest.read_bytes()
    for copy in (ROOT / PPTX_NAME, ROOT / ALIAS, OUTPUTS / ALIAS):
        copy.write_bytes(payload)
        print(copy)
    print(dest)
    return dest


if __name__ == "__main__":
    build()
