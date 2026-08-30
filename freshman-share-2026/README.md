# 喜娜 · 中大本科新生分享 · 2026

Widescreen talk for Sun Yat-sen University undergraduate new students. The three experience slides keep the copy from the original expansion script: academic practice, volunteer work, and cultural exchange.

## Open the deck

```bash
python3 -m http.server 8765
```

Then open [http://127.0.0.1:8765/freshman-share-2026/](http://127.0.0.1:8765/freshman-share-2026/).

- Arrow keys / space: next and previous
- `N`: speaker notes
- `?slide=4&shot=1`: screenshot a single slide without chrome

## Build the PowerPoint

```bash
python3 freshman-share-2026/build_pptx.py
```

Presentable PowerPoint (open this one):

`freshman-share-2026/喜娜_中大本科新生分享_丰富经历照片终版_2026.pptx`

Same file also at:

- `freshman-share-2026/Heena-SYSU-Freshman-Share-2026.pptx`
- `freshman-share-2026/outputs/喜娜_中大本科新生分享_丰富经历照片终版_2026.pptx`

Rebuild with `python3 freshman-share-2026/make_ppt.py` after the slide PNGs exist, or `python3 freshman-share-2026/build_pptx.py` for a full rebuild.

## Personal photos

The original WeChat / Codex paths from the local Mac are not in this environment. Campus photographs from the 2026 international-student life booklet fill those frames until originals are added. See [photos/README.md](photos/README.md).

Fallback frames show a red tag: `校园氛围图 · 待换个人照片`.

## Fonts

The original Office deck embeds **等线 (DengXian)** as an EOT/OTTO (CFF) font. Artifact-tool then reports:

- `embedded_font_decode_failed: unsupported CTF scaler type 0x4f54544f` (`OTTO`)
- `embedded_font_name_mismatch: EOT family "等线" does not match decoded SFNT name "DengXian"`

Those warnings are not overflow errors. The overflow tests still pass.

This rebuild does **not** embed 等线. Slide text uses **Microsoft YaHei** (TrueType, same Latin and East-Asian family name) and **Noto Serif CJK SC** for titles. Preview PNGs are drawn with Noto CJK TrueType collections. Do not re-embed DengXian/等线 if you later inspect the file with artifact-tool.

## Compose / inspect

`artifact/build-deck.ts` is the artifact-tool compose script: named nodes, speaker notes, PNG + `format: "layout"` export, and a final `inspect`. Run it only where `@oai/artifact-tool` is available. Do not import the original 等线-embedded Office file.

This repo’s local builder writes the same inspect artifacts:

- `outputs/slides/slide-0N.layout.json` — frames, names, text
- `outputs/喜娜_中大本科新生分享_丰富经历照片终版_2026.pptx.inspect.ndjson`

Experience-slide anchors stay stable: `标题 1`, `文本框 25`, `文本框 7/10/12/13`, `文本框 22/21`, `图片 29`, `图片 23`.

## Visual identity

School green `#00561F`, auxiliary red `#740003`, gold accent `#D29865`, and the official emblem. Emblem and campus photos follow the notices in `poster/NOTICE.txt` and `poster/photos/NOTICE.txt`.
