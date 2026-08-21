# Codebook (anonymised file)

`data/anonymized_n38.csv` is built from the Wenjuan SPSS export. Direct identifiers (name, IP address, IP city/province strings, browser) are not included.

| Column | Meaning |
|---|---|
| id | Sequential response number |
| gender | male / female (Q2) |
| nationality | Pakistan / other (Q3) |
| level | beginner / intermediate / advanced (Q4) |
| years | 1-2 / 3-4 / 5-6 / 6+ (Q5) |
| like_online | 1 very … 4 not at all (Q6 exclusive; 1 row NA) |
| hours | Q7 weekly online Chinese load (1 = >8h … 4 = once or twice) |
| learned, improve, interest | Q8–Q10; 1 = most positive, 4 = most negative |
| all_chinese_online | Q11 1 = yes |
| speed | Q14 1 very good … 5 very bad |
| can_replace | Q15 1 = online can replace F2F |
| use_*, blocked_*, available_* | Multiple-response 0/1 |
| prob_* | Problems ticked 0/1 |
| home_noise | noisy / quiet / lively |
| home_affect | 1 very much … 4 not at all (NA if multiple ticks) |
| home_affect_very | Q21 “非常多” dummy |
| work | part-time / full-time / study-only / work-and-study |
| stress | Q24 1 very high … 4 none |
| interact | Q25 1 very much … 4 not at all |
| in_china_ip | 1 if IP province was a mainland China label |
| device | iphone / android |
| submit_date | Date only |

Rebuild: place the `.sav` in `data/raw/wenjuan_coded.sav` (gitignored) and run `python3 analysis/analyze.py`.
