# Stop: this SPSS file is n = 38, not n = 97

## 中文（请先看）

你发来的问卷网编码文件里是 **38 份完整答卷**（2022年2月5–8日），不是 2024 年 *Arbor* 文章里的 **97 人**。

| | 文章 (2024) | 这个 .sav 文件 |
|---|---|---|
| 人数 | 97（男 69，女 28） | **38（男 27，女 11）** |
| 男性比例 | 71.1% | **71.1%**（完全一样） |
| 工具 | 自称 14 题李克特 + SPSS + Cronbach | **30 题问卷网问卷**（单选 + 多选），不是 14 题量表 |
| 能否代替线下 | 文章写 77% 不能 | 文件里是 **19 能 / 19 不能（50%）** |

Q1 投稿**必须用 38 人**。如果还有另一批 59 人（纸质问卷、另一份链接、访谈对象另计），请再发文件。如果 97 是笔误或重复计算，现在改过来，比被审稿人查出来好。

**不要**把姓名、IP 放进公开仓库。原始 .sav 已放在本地 `data/raw/` 并写入 `.gitignore`。论文只用匿名 CSV。

---

## What we can now defend in a Q1 methods section

The export is a real instrument with real associations:

1. **Home “affects study very much” × very high stress:** Fisher *p* < .001, OR ≈ 26.  
2. **Worse internet speed** correlates with learning less, improving less, less interest, less interaction (Spearman ρ .46–.64).  
3. **Platform geography:** QQ / Chaoxing often unusable; Zoom / WhatsApp usable. This is new relative to the 2024 note.  
4. **Women** in this file more often say online Chinese cannot replace campus (9/11 vs 10/27 men, *p* = .029).  
5. Learning-appraisal 3-item α = .84 (learned / improve / interest).

n = 38 is small. *System* / *CALL* are still a stretch. *Language, Culture and Curriculum* or *RELC Journal* remain the realistic Q1/SSCI targets if interviews are added.

If you have the **interview recordings/transcripts**, send those next. The .sav file has almost no open text (one sentence: 我觉得中国现在让学生回来上课。在线上上课一分钟也不合适).
