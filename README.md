# 中山大学官方海报编辑器

Editable official poster for **Sun Yat-sen University (中山大学)**, using the school visual identity:

| Role | HEX | RGB | CMYK (print / screening) |
| --- | --- | --- | --- |
| Standard green 标准色 | `#00561F` | 0, 86, 31 | 100, 0, 100, 60 |
| Auxiliary red 辅助色 | `#740003` | 116, 0, 3 | 30, 100, 100, 50 |
| Gold 金色 | `#D29865` | 210, 152, 101 | 18, 50, 66, 0 |

Open `poster/index.html` in a browser (or serve the `poster` folder). Edit title, date, venue, and theme on the left. Click **打印 / PDF** and choose “Save as PDF”.

## How to use

1. Open `poster/index.html`.
2. Pick **绿色** for regular academic posters, **红色** for ceremonies.
3. Choose A3 (wall poster), A4, or vertical screen size.
4. Replace the placeholder copy with your event.
5. Optional: upload the official emblem SVG from [中山大学视觉形象识别系统](https://home3.sysu.edu.cn/sysuvi/).
6. Print to PDF. Give the print shop the CMYK values above.

The editor currently defaults to **海报 1 国际学生报到** from `报到海报文案.doc`. Switch to **海报 2** for required documents. Click poster text to edit, then print to PDF.

## Files

```
poster/
  index.html      editor
  styles.css
  app.js
  NOTICE.txt      logo copyright
  assets/         emblem, wordmark, motto, haitang ornaments
```

校徽版权归中山大学所有。正式印发请以学校视觉识别手册为准。
