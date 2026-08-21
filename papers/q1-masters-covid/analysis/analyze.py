"""Analyse the anonymised Wenjuan export for the Q1 reanalysis paper.

If data/raw/wenjuan_coded.sav is present, rebuild the anonymised CSV
(names and IP addresses are dropped). Otherwise read the committed CSV.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "wenjuan_coded.sav"
ANON = ROOT / "data" / "anonymized_n38.csv"
OUT = ROOT / "analysis" / "results.json"

CHINA_PROV = {"天津市", "广西壮族自治区", "河北省", "安徽省", "海南省"}


def recode_q6(row: pd.Series) -> float:
    picks = [i for i, c in enumerate(["Q6_1", "Q6_2", "Q6_3", "Q6_4"], start=1) if row[c] == 1]
    if len(picks) != 1:
        return np.nan
    return float(picks[0])


def recode_q21(row: pd.Series) -> float:
    picks = [i for i, c in enumerate(["Q21_1", "Q21_2", "Q21_3", "Q21_4"], start=1) if row[c] == 1]
    if len(picks) != 1:
        return np.nan
    return float(picks[0])


def cronbach(items: pd.DataFrame) -> float:
    items = items.dropna()
    k = items.shape[1]
    return float((k / (k - 1)) * (1 - items.var(axis=0, ddof=1).sum() / items.sum(axis=1).var(ddof=1)))


def fisher(a, b) -> dict:
    tab = pd.crosstab(a, b)
    if tab.shape != (2, 2):
        chi2, p, dof, _ = stats.chi2_contingency(tab)
        return {"table": tab.values.tolist(), "index": tab.index.tolist(), "cols": tab.columns.tolist(), "p": float(p), "test": "chi2"}
    oddsr, p = stats.fisher_exact(tab)
    return {"table": tab.values.tolist(), "index": [str(x) for x in tab.index], "cols": [str(x) for x in tab.columns], "or": float(oddsr), "p": float(p), "test": "fisher"}


def pct(n: int, d: int) -> float:
    return round(100 * n / d, 1)


def anonymize(raw: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    out["id"] = raw["答题序号"].astype(int)
    out["gender"] = raw["Q2"].map({1: "male", 2: "female"})
    out["nationality"] = np.where(raw["Q3"] == 1, "Pakistan", "other")
    out["level"] = raw["Q4"].map({1: "beginner", 2: "intermediate", 3: "advanced"})
    out["years"] = raw["Q5"].map({1: "1-2", 2: "3-4", 3: "5-6", 4: "6+"})
    out["like_online"] = raw.apply(recode_q6, axis=1)  # 1 very ... 4 not at all
    out["hours"] = raw["Q7"]
    out["learned"] = raw["Q8"]  # 1 a lot ... 4 nothing
    out["improve"] = raw["Q9"]
    out["interest"] = raw["Q10"]
    out["all_chinese_online"] = raw["Q11"].map({1: 1, 2: 0})
    out["online_required"] = raw["Q12_1"].astype(int)
    out["online_elective"] = raw["Q12_2"].astype(int)
    out["has_internet"] = raw["Q13"].map({1: 1, 2: 0})
    out["speed"] = raw["Q14"]  # 1 very good ... 5 very bad
    out["can_replace"] = raw["Q15"].map({1: 1, 2: 0})
    for src, dst in [
        ("Q16_1", "easy_tencent_meeting"),
        ("Q16_9", "easy_wechat"),
        ("Q17_1", "use_tencent_meeting"),
        ("Q17_5", "use_zoom"),
        ("Q17_4", "use_wechat"),
        ("Q18_8", "blocked_qq"),
        ("Q18_5", "blocked_chaoxing"),
        ("Q18_4", "blocked_dingtalk"),
        ("Q18_6", "blocked_mooc"),
        ("Q19_2", "available_zoom"),
        ("Q19_3", "available_whatsapp"),
        ("Q19_1", "available_tencent_meeting"),
        ("Q19_4", "available_wechat"),
        ("Q23_1", "prob_unstable_net"),
        ("Q23_2", "prob_no_power"),
        ("Q23_3", "prob_no_signal"),
        ("Q23_5", "prob_no_time"),
        ("Q21_1", "home_affect_very"),
        ("Q30_1", "interact_qa"),
        ("Q30_2", "interact_dialogue"),
        ("Q30_3", "interact_game"),
        ("Q30_4", "interact_scenario"),
        ("Q30_5", "interact_roleplay"),
    ]:
        out[dst] = raw[src].fillna(0).astype(int)
    out["home_noise"] = raw["Q20"].map({1: "noisy", 2: "quiet", 3: "lively", 5: "other"})
    out["home_affect"] = raw.apply(recode_q21, axis=1)
    out["work"] = raw["Q22"].map({1: "part-time", 2: "full-time", 3: "study-only", 4: "work-and-study", 5: "other"})
    out["stress"] = raw["Q24"]  # 1 very high ... 4 none
    out["interact"] = raw["Q25"]
    out["content_volume"] = raw["Q27"]
    out["time_sat"] = raw["Q28"]
    out["prefer_minutes"] = raw["Q29"].map({1: 30, 2: 45, 3: 60, 4: np.nan})
    out["in_china_ip"] = raw["IP省份"].isin(CHINA_PROV).astype(int)
    out["device"] = np.where(raw["操作系统"].astype(str).str.contains("iPhone"), "iphone", "android")
    out["submit_date"] = pd.to_datetime(raw["提交时间"]).dt.date.astype(str)
    return out


def main() -> None:
    if RAW.exists():
        import pyreadstat

        raw, _ = pyreadstat.read_sav(RAW)
        anon = anonymize(raw)
        ANON.parent.mkdir(parents=True, exist_ok=True)
        anon.to_csv(ANON, index=False)
        print(f"wrote {ANON} from {RAW}")
    else:
        anon = pd.read_csv(ANON)
        print(f"read {ANON}")

    n = len(anon)
    results: dict = {"n": n}

    def count_map(col: str) -> dict:
        vc = anon[col].value_counts(dropna=False)
        return {str(k): {"n": int(v), "pct": pct(int(v), n)} for k, v in vc.items()}

    results["gender"] = count_map("gender")
    results["nationality"] = count_map("nationality")
    results["level"] = count_map("level")
    results["years"] = count_map("years")
    results["like_online"] = count_map("like_online")
    results["learned"] = count_map("learned")
    results["improve"] = count_map("improve")
    results["interest"] = count_map("interest")
    results["can_replace"] = count_map("can_replace")
    results["has_internet"] = count_map("has_internet")
    results["speed"] = count_map("speed")
    results["home_noise"] = count_map("home_noise")
    results["stress"] = count_map("stress")
    results["interact"] = count_map("interact")
    results["work"] = count_map("work")
    results["time_sat"] = count_map("time_sat")
    results["prefer_minutes"] = count_map("prefer_minutes")
    results["device"] = count_map("device")
    results["in_china_ip"] = count_map("in_china_ip")
    results["all_chinese_online"] = count_map("all_chinese_online")
    results["hours"] = count_map("hours")

    binaries = [
        "online_required",
        "online_elective",
        "prob_unstable_net",
        "prob_no_power",
        "prob_no_signal",
        "prob_no_time",
        "home_affect_very",
        "use_tencent_meeting",
        "use_zoom",
        "use_wechat",
        "blocked_qq",
        "blocked_chaoxing",
        "blocked_dingtalk",
        "blocked_mooc",
        "available_zoom",
        "available_whatsapp",
        "available_tencent_meeting",
        "available_wechat",
        "easy_tencent_meeting",
        "easy_wechat",
        "interact_qa",
        "interact_dialogue",
        "interact_game",
        "interact_scenario",
        "interact_roleplay",
    ]
    results["binaries"] = {c: {"n": int(anon[c].sum()), "pct": pct(int(anon[c].sum()), n)} for c in binaries}

    scale = anon[["learned", "improve", "interest"]]
    results["cronbach_learning"] = round(cronbach(scale), 3)

    female = anon["gender"] == "female"
    poor_net = anon["speed"].isin([4, 5])
    high_stress = anon["stress"] == 1
    some_stress = anon["stress"].isin([1, 2, 3])
    learn_little = anon["learned"].isin([3, 4])
    cannot_replace = anon["can_replace"] == 0

    results["fisher"] = {
        "female_x_cannot_replace": fisher(female, cannot_replace),
        "poor_net_x_cannot_replace": fisher(poor_net, cannot_replace),
        "learn_little_x_cannot_replace": fisher(learn_little, cannot_replace),
        "home_very_x_high_stress": fisher(anon["home_affect_very"] == 1, high_stress),
        "no_power_x_high_stress": fisher(anon["prob_no_power"] == 1, high_stress),
    }

    results["derived"] = {
        "poor_net": {"n": int(poor_net.sum()), "pct": pct(int(poor_net.sum()), n)},
        "high_stress": {"n": int(high_stress.sum()), "pct": pct(int(high_stress.sum()), n)},
        "some_stress": {"n": int(some_stress.sum()), "pct": pct(int(some_stress.sum()), n)},
        "learn_little": {"n": int(learn_little.sum()), "pct": pct(int(learn_little.sum()), n)},
        "cannot_replace": {"n": int(cannot_replace.sum()), "pct": pct(int(cannot_replace.sum()), n)},
        "home_not_quiet": {
            "n": int((anon["home_noise"] != "quiet").sum()),
            "pct": pct(int((anon["home_noise"] != "quiet").sum()), n),
        },
        "working": {
            "n": int(anon["work"].isin(["part-time", "full-time", "work-and-study"]).sum()),
            "pct": pct(int(anon["work"].isin(["part-time", "full-time", "work-and-study"]).sum()), n),
        },
    }

    spearman_pairs = [
        ("speed", "learned"),
        ("speed", "improve"),
        ("speed", "interest"),
        ("speed", "interact"),
        ("speed", "time_sat"),
        ("learned", "improve"),
        ("improve", "interest"),
        ("home_affect_very", "stress"),
    ]
    results["spearman"] = {}
    for a, b in spearman_pairs:
        r, p = stats.spearmanr(anon[a], anon[b], nan_policy="omit")
        results["spearman"][f"{a}__{b}"] = {"rho": round(float(r), 3), "p": float(p)}

    mw = {}
    for col in ["learned", "improve", "interest", "speed", "stress", "interact", "time_sat"]:
        u, p = stats.mannwhitneyu(
            anon.loc[anon["gender"] == "male", col].dropna(),
            anon.loc[anon["gender"] == "female", col].dropna(),
            alternative="two-sided",
        )
        mw[col] = {"U": float(u), "p": float(p)}
    results["mannwhitney_gender"] = mw

    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT}")
    print("n", n, "cronbach", results["cronbach_learning"])
    print("fisher home x stress p", results["fisher"]["home_very_x_high_stress"]["p"])
    print("fisher female x replace p", results["fisher"]["female_x_cannot_replace"]["p"])


if __name__ == "__main__":
    main()
