# How this data is updated for a **new** Q1 paper

## 中文：你要的「更新数据发新 Q1」是什么意思

不是把 38 人改成 97 人，也不是再填假问卷。

**更新 = 用问卷网原始编码文件，重新清洗、重新统计，写成一篇和 2024 年 *Arbor* 不同的新论文。**

| 2024 已发表短文 | 现在这篇新论文 |
|---|---|
| 声称 n = 97，14 题李克特 | **n = 38**，30 题问卷网原题 |
| 只报大概百分比，统计有误 | 题项频率 + Fisher + Spearman + 敏感性分析 |
| 「挑战与影响」描述文 | **新贡献：平台地理 + 家庭生态 → 压力/投入** |
| 不能再投 Q1（已发表） | 可以投 Q1，但必须声明关系、不能抄原文 |

清洗规则（已写入 `data/publication_n38.csv`）：

1. 去掉姓名、IP，只留匿名变量  
2. 巴基斯坦 37 人 + 孟加拉 1 人；主分析 n = 38，另做 n = 37 敏感性  
3. 学习评价三题平均分（α = .84）  
4. 不把人数放大，不补访谈假引语  

敏感性：去掉孟加拉、去掉中国 IP 后，**家里很影响学习 × 高压** 和 **网速 × 学习评价** 方向不变。

投 Q1 还需要：曹慧敏同意署名、伦理一句、以及投稿信里说明 2024 短文。访谈有最好，没有就按**量化问卷论文**投，不要假装混合方法。

---

## English (for the cover letter)

This manuscript is a **new original analysis** of the primary Wenjuan export (N = 38). It does not reuse the 2024 tables. New results include platform geography, the home–stress association (OR = 25.67, 95% CI [4.42, 149.00]), and speed–appraisal correlations. Sensitivity checks (Pakistani-only n = 37; offshore IP n = 29) leave the two main associations in the same direction.

Files to submit later: `manuscript.md` + `analysis/apa_tables.md` (paste as Word tables).
