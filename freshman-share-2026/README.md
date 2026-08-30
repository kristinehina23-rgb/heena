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

Output:

`freshman-share-2026/outputs/喜娜_中大本科新生分享_丰富经历照片终版_2026.pptx`

## Personal photos

The original WeChat / Codex paths from the local Mac are not in this environment. Campus photographs from the 2026 international-student life booklet fill those frames until originals are added. See [photos/README.md](photos/README.md).

Fallback frames show a red tag: `校园氛围图 · 待换个人照片`.

## Fonts

The original Office deck embeds **等线 (DengXian)** as an EOT/OTTO (CFF) font. Artifact-tool then reports:

- `embedded_font_decode_failed: unsupported CTF scaler type 0x4f54544f` (`OTTO`)
- `embedded_font_name_mismatch: EOT family "等线" does not match decoded SFNT name "DengXian"`

Those warnings are not overflow errors. The overflow tests still pass.

This rebuild does **not** embed 等线. Slide text uses **Microsoft YaHei** (TrueType, same Latin and East-Asian family name) and **Noto Serif CJK SC** for titles. Preview PNGs are drawn with Noto CJK TrueType collections. Do not re-embed DengXian/等线 if you later inspect the file with artifact-tool.

## Visual identity

School green `#00561F`, auxiliary red `#740003`, gold accent `#D29865`, and the official emblem. Emblem and campus photos follow the notices in `poster/NOTICE.txt` and `poster/photos/NOTICE.txt`.
