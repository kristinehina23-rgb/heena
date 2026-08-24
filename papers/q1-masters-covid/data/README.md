# Codebook and de-identification

The public analysis file is `data/publication_n38.csv`. `data/anonymized_n38.csv` is the same respondent-level file without derived composites. Direct identifiers (name, IP address, IP city/province strings, browser, timestamps, device OS) are not included.

## De-identification

In this N = 38 convenience sample, unusual combinations can raise re-identification risk. The public files therefore:

- recode nationality as Pakistan / other (the single non-Pakistani case is not named);
- omit IP-province dummies, submission dates, and device identifiers;
- omit free-text comments;
- omit names, raw IP addresses, and spreadsheet metadata.

Aggregates that cannot be attached to a row (for example, 24 iPhone / 14 Android submissions) may still be reported in the article.

Rebuild from the gitignored `.sav` only on a private machine: place it in `data/raw/wenjuan_coded.sav` and run `python3 analysis/analyze.py`, then `python3 analysis/publish_prep.py`. Do not commit the `.sav` or any file that restores IP, date, or device columns.

| Column | Meaning |
|---|---|
| id | Sequential response number (not the original platform ID) |
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
| use_*, blocked_*, available_* | Multiple-response 0/1 (`blocked_*` = marked unusable “in my country”) |
| prob_* | Problems ticked 0/1 |
| home_noise | noisy / quiet / lively |
| home_affect | 1 very much … 4 not at all (NA if multiple ticks) |
| home_affect_very | Q21 “非常多” dummy |
| work | part-time / full-time / study-only / work-and-study |
| stress | Q24 1 very high … 4 none |
| interact | Q25 1 very much … 4 not at all |
