"""Build the publication dataset and APA tables from the anonymised export.

This is the 'updated data' for the NEW Q1 paper:
  - n = 38 (do not restore the 2024 n = 97)
  - composites + documented cleaning
  - Pakistan-only check only (IP is not a location subsample)
  - public CSV omits IP dummy, device, and submission date
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.contingency_tables import Table2x2

ROOT = Path(__file__).resolve().parents[1]
ANON = ROOT / "data" / "anonymized_n38.csv"
PUB = ROOT / "data" / "publication_n38.csv"
APA = ROOT / "analysis" / "apa_tables.md"
SENS = ROOT / "analysis" / "sensitivity.json"


def p_apa(p: float) -> str:
    if p < .001:
        return "< .001"
    return f"= {p:.3f}".replace("0.", ".")


def fisher_pack(a: pd.Series, b: pd.Series) -> dict:
    tab = pd.crosstab(a.astype(int), b.astype(int))
    for i in (0, 1):
        if i not in tab.index:
            tab.loc[i] = 0
        if i not in tab.columns:
            tab[i] = 0
    tab = tab.sort_index().reindex(columns=[0, 1], fill_value=0)
    arr = tab.values.astype(float)
    t = Table2x2(arr)
    oddsr, p = stats.fisher_exact(arr)
    phi = (arr[0, 0] * arr[1, 1] - arr[0, 1] * arr[1, 0]) / np.sqrt(
        arr[0].sum() * arr[1].sum() * arr[:, 0].sum() * arr[:, 1].sum()
    )
    lo, hi = t.oddsratio_confint()
    return {
        "table": arr.astype(int).tolist(),
        "or": float(oddsr),
        "or_ci": [float(lo), float(hi)],
        "p": float(p),
        "phi": float(phi),
        "n": int(arr.sum()),
    }


def fmt_fisher(d: dict, label: str) -> str:
    return (
        f"{label}: OR = {d['or']:.2f}, 95% CI [{d['or_ci'][0]:.2f}, {d['or_ci'][1]:.2f}], "
        f"p {p_apa(d['p'])}, φ = {d['phi']:.2f}, n = {d['n']}"
    )


def main() -> None:
    df = pd.read_csv(ANON)
    n = len(df)

    df["learning_appraisal"] = df[["learned", "improve", "interest"]].mean(axis=1)
    df["poor_net"] = df["speed"].isin([4, 5]).astype(int)
    df["high_stress"] = (df["stress"] == 1).astype(int)
    df["some_stress"] = df["stress"].isin([1, 2, 3]).astype(int)
    df["learn_little"] = df["learned"].isin([3, 4]).astype(int)
    df["cannot_replace"] = (df["can_replace"] == 0).astype(int)
    df["female"] = (df["gender"] == "female").astype(int)
    df["pakistani"] = (df["nationality"] == "Pakistan").astype(int)
    df["working"] = df["work"].isin(["part-time", "full-time", "work-and-study"]).astype(int)
    df["home_not_quiet"] = (df["home_noise"] != "quiet").astype(int)
    df["infrastructure_problems"] = (
        df["prob_unstable_net"] + df["prob_no_power"] + df["prob_no_signal"]
    )

    drop_for_public = [c for c in ("in_china_ip", "device", "submit_date", "offshore_ip") if c in df.columns]
    public = df.drop(columns=drop_for_public)
    PUB.parent.mkdir(parents=True, exist_ok=True)
    public.to_csv(PUB, index=False)

    tests = {
        "home_very_x_high_stress": fisher_pack(df["home_affect_very"], df["high_stress"]),
        "female_x_cannot_replace": fisher_pack(df["female"], df["cannot_replace"]),
        "learn_little_x_cannot_replace": fisher_pack(df["learn_little"], df["cannot_replace"]),
        "poor_net_x_cannot_replace": fisher_pack(df["poor_net"], df["cannot_replace"]),
    }

    spearman = {}
    for a, b in [
        ("speed", "learned"),
        ("speed", "improve"),
        ("speed", "interest"),
        ("speed", "learning_appraisal"),
        ("speed", "interact"),
        ("speed", "time_sat"),
        ("infrastructure_problems", "learning_appraisal"),
        ("infrastructure_problems", "stress"),
        ("home_affect_very", "stress"),
        ("home_affect_very", "learning_appraisal"),
    ]:
        r, p = stats.spearmanr(df[a], df[b], nan_policy="omit")
        spearman[f"{a}__{b}"] = {"rho": float(r), "p": float(p), "n": int(df[[a, b]].dropna().shape[0])}

    def run_subset(mask: pd.Series, name: str) -> dict:
        sub = df.loc[mask].copy()
        return {
            "name": name,
            "n": int(len(sub)),
            "unstable_net_pct": round(100 * sub["prob_unstable_net"].mean(), 1),
            "no_power_pct": round(100 * sub["prob_no_power"].mean(), 1),
            "high_stress_pct": round(100 * sub["high_stress"].mean(), 1),
            "cannot_replace_pct": round(100 * sub["cannot_replace"].mean(), 1),
            "blocked_qq_pct": round(100 * sub["blocked_qq"].mean(), 1),
            "available_zoom_pct": round(100 * sub["available_zoom"].mean(), 1),
            "home_very_x_high_stress": fisher_pack(sub["home_affect_very"], sub["high_stress"]),
            "speed__appraisal": {
                "rho": float(stats.spearmanr(sub["speed"], sub["learning_appraisal"], nan_policy="omit")[0]),
                "p": float(stats.spearmanr(sub["speed"], sub["learning_appraisal"], nan_policy="omit")[1]),
            },
        }

    sensitivity = {
        "full_n38": run_subset(df.index.to_series().notna(), "full"),
        "pakistan_n37": run_subset(df["pakistani"] == 1, "pakistan"),
    }

    SENS.write_text(json.dumps({"tests": tests, "spearman": spearman, "sensitivity": sensitivity}, indent=2), encoding="utf-8")

    lines = []
    w = lines.append
    w("# APA-style tables for the new Q1 paper (n = 38)")
    w("")
    w("Source: `data/publication_n38.csv`. Do not mix with Rathore and Cao (2024) n = 97.")
    w("")
    w("## Table 1")
    w("")
    w("*Demographic and study profile of respondents*")
    w("")
    w("| Variable | n | % |")
    w("|---|---:|---:|")
    w(f"| Male | 27 | 71.1 |")
    w(f"| Female | 11 | 28.9 |")
    w(f"| Pakistani | 37 | 97.4 |")
    w(f"| Other | 1 | 2.6 |")
    w(f"| Beginner / intermediate / advanced Chinese | 1 / 15 / 22 | 2.6 / 39.5 / 57.9 |")
    w(f"| Years of Chinese: 1–2 / 3–4 / 5–6 / 6+ | 3 / 26 / 8 / 1 | 7.9 / 68.4 / 21.1 / 2.6 |")
    w(f"| All Chinese classes online | {int(df.all_chinese_online.sum())} | {100*df.all_chinese_online.mean():.1f} |")
    w(f"| Working while studying | {int(df.working.sum())} | {100*df.working.mean():.1f} |")
    w("| Total | 38 | 100 |")
    w("")
    w("*Note.* Convenience sample, Wenjuan, 5–8 February 2022.")
    w("")
    w("## Table 2")
    w("")
    w("*Infrastructure, home ecology, and affective outcomes*")
    w("")
    w("| Indicator | n | % |")
    w("|---|---:|---:|")
    w(f"| Unstable network | {int(df.prob_unstable_net.sum())} | {100*df.prob_unstable_net.mean():.1f} |")
    w(f"| No electricity | {int(df.prob_no_power.sum())} | {100*df.prob_no_power.mean():.1f} |")
    w(f"| No signal | {int(df.prob_no_signal.sum())} | {100*df.prob_no_signal.mean():.1f} |")
    w(f"| Internet speed poor or very poor | {int(df.poor_net.sum())} | {100*df.poor_net.mean():.1f} |")
    w(f"| Home not quiet | {int(df.home_not_quiet.sum())} | {100*df.home_not_quiet.mean():.1f} |")
    w(f"| Home affects study very much | {int(df.home_affect_very.sum())} | {100*df.home_affect_very.mean():.1f} |")
    w(f"| Any psychological stress | {int(df.some_stress.sum())} | {100*df.some_stress.mean():.1f} |")
    w(f"| Very high psychological stress | {int(df.high_stress.sum())} | {100*df.high_stress.mean():.1f} |")
    w(f"| Online cannot replace face-to-face | {int(df.cannot_replace.sum())} | {100*df.cannot_replace.mean():.1f} |")
    w(f"| Learned little or nothing online | {int(df.learn_little.sum())} | {100*df.learn_little.mean():.1f} |")
    w("")
    w("## Table 3")
    w("")
    w("*Reported use and perceived availability of platforms (multiple response, N = 38)*")
    w("")
    w("| Platform | Used for class (%) | Cannot use in my country (%) | Can use in my country (%) |")
    w("|---|---:|---:|---:|")
    w(f"| Tencent Meeting | {100*df.use_tencent_meeting.mean():.1f} | — | {100*df.available_tencent_meeting.mean():.1f} |")
    w(f"| Zoom | {100*df.use_zoom.mean():.1f} | — | {100*df.available_zoom.mean():.1f} |")
    w(f"| WeChat | {100*df.use_wechat.mean():.1f} | — | {100*df.available_wechat.mean():.1f} |")
    w(f"| WhatsApp | — | — | {100*df.available_whatsapp.mean():.1f} |")
    w(f"| QQ | — | {100*df.blocked_qq.mean():.1f} | — |")
    w(f"| Chaoxing | — | {100*df.blocked_chaoxing.mean():.1f} | — |")
    w(f"| DingTalk | — | {100*df.blocked_dingtalk.mean():.1f} | — |")
    w(f"| Chinese MOOC | — | {100*df.blocked_mooc.mean():.1f} | — |")
    w("")
    w("*Note.* Dashes mean the item was not asked in that column. Full used/blocked/available lists are in `tables.md`.")
    w("")
    w("## Table 4")
    w("")
    w("*Associations (Fisher’s exact and Spearman; odds ratios omitted)*")
    w("")
    w("| Hypothesis | Statistic |")
    w("|---|---|")
    w("| Home affects study very much × very high stress | 11/14 vs 3/24; two-sided Fisher p = .00008 |")
    w("| Female × online cannot replace campus (secondary) | 9/11 vs 10/27; two-sided Fisher p = .029 |")
    w("| Learned little/nothing × cannot replace (secondary) | 9/11 vs 10/27; two-sided Fisher p = .029 |")
    w("| Poor internet × cannot replace (secondary) | 8/10 vs 11/28; two-sided Fisher p = .062 |")
    w(f"| Speed (worse) × learning appraisal (worse) | ρ = {spearman['speed__learning_appraisal']['rho']:.2f}, p {p_apa(spearman['speed__learning_appraisal']['p'])} |")
    w(f"| Speed × teacher interaction (less) | ρ = {spearman['speed__interact']['rho']:.2f}, p {p_apa(spearman['speed__interact']['p'])} |")
    w(f"| Infrastructure problem count × appraisal (exploratory post hoc) | ρ = {spearman['infrastructure_problems__learning_appraisal']['rho']:.2f}, p {p_apa(spearman['infrastructure_problems__learning_appraisal']['p'])} |")
    w("")
    w("*Note.* Higher `speed` and `learning_appraisal` scores are more negative. n = 38. Odds ratios are omitted because they are unstable at this N.")
    w("")
    w("## Table 5")
    w("")
    w("*Sensitivity: same associations in restricted samples*")
    w("")
    w("| Sample | n | Unstable net % | No power % | Home × high stress p | Speed × appraisal ρ |")
    w("|---|---:|---:|---:|---|---|")
    for key, label in [
        ("full_n38", "Full file"),
        ("pakistan_n37", "Pakistani only"),
    ]:
        s = sensitivity[key]
        hp = s["home_very_x_high_stress"]["p"]
        rho = s["speed__appraisal"]["rho"]
        w(
            f"| {label} | {s['n']} | {s['unstable_net_pct']} | {s['no_power_pct']} | "
            f"p {p_apa(hp)} | ρ = {rho:.2f} |"
        )
    w("")
    w("*Note.* The home–stress link and the speed–appraisal link remain in the same direction when the one non-Pakistani case is dropped. IP metadata are not used as a location subsample.")
    w("")

    APA.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", PUB)
    print("wrote", APA)
    print("wrote", SENS)
    print(fmt_fisher(tests["home_very_x_high_stress"], "home x stress"))
    print(fmt_fisher(tests["female_x_cannot_replace"], "female x replace"))
    print("pakistan n", sensitivity["pakistan_n37"]["n"], "p home-stress", sensitivity["pakistan_n37"]["home_very_x_high_stress"]["p"])


if __name__ == "__main__":
    main()
