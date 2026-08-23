# Supplementary statistical notes (N = 38)

Source: `data/anonymized_n38.csv`. Software: Python 3, SciPy `fisher_exact` (two-sided) and `spearmanr`. Bootstrap Spearman 95% CIs: 5,000 resamples, seed 42.

Odds ratios are **not** used in the manuscript. They are unstable at this N. A Wald interval for poor-internet × cannot-replace can exclude 1 while Fisher’s exact *p* = .062; that mismatch is why the article reports counts and Fisher *p* only.

## Focal associations

| Association | Counts | Fisher exact *p* |
|---|---|---|
| Home affects study very much × very high stress | 11/14 vs 3/24 | .000079 |
| Speed (higher = worse) × appraisal index (higher = worse) | ρ = .65, bootstrap 95% CI [.36, .84] | *p* = .000009 |

Pakistani-nationality only (n = 37): home × stress Fisher *p* = .00011; speed × appraisal ρ = .67, bootstrap 95% CI [.39, .85].

## Secondary (not used as confirmatory tests)

| Association | Counts | Fisher exact *p* |
|---|---|---|
| Female × cannot replace | 9/11 vs 10/27 | .029 |
| Learned little/nothing × cannot replace | 9/11 vs 10/27 | .029 |
| Poor internet × cannot replace | 8/10 vs 11/28 | .062 |
| Female × working while studying | 3/11 vs 19/27 | .028 |

The female × cannot-replace table and the learned-little × cannot-replace table have **identical cell counts** (17/10 vs 2/9) and therefore the same *p*. They are different predictors.

## Appraisal index inter-item Spearman ρ

| | learned | improve | interest |
|---|---:|---:|---:|
| learned | 1 | .66 | .55 |
| improve | .66 | 1 | .75 |
| interest | .55 | .75 | 1 |

Cronbach’s α = .84 (descriptive only).

## Other Spearman (exploratory)

| Pair | ρ | *p* | bootstrap 95% CI |
|---|---:|---:|---|
| Speed × learned | .46 | .004 | [.12, .72] |
| Speed × improve | .64 | .000016 | [.36, .84] |
| Speed × teacher interaction (higher = thinner) | .55 | .00031 | [.28, .76] |
| Speed × time satisfaction (higher = less satisfied) | .60 | .000068 | [.32, .80] |
| Problem-count × appraisal | .02 | .91 | [−.32, .37] |
| Home-very × stress ordinal (1 = very high) | −.66 | .000008 | [−.83, −.45] |

## Mann–Whitney U by gender (two-sided)

| Variable | U | *p* |
|---|---:|---:|
| learned | 156.0 | .81 |
| improve | 130.5 | .55 |
| interest | 121.0 | .36 |
| speed | 149.5 | .99 |
| stress | 134.0 | .63 |
| interact | 160.5 | .68 |
| time_sat | 151.0 | .95 |
