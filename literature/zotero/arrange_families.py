#!/usr/bin/env python3
"""Arrange the thesis library into the eight corpus families. Does not write Chapter 2."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RIS = ROOT / "literature/zotero/papers-1-240.ris"
OUT_MD = ROOT / "dissertation/LITERATURE-ARRANGEMENT.md"
OUT_CSV = ROOT / "literature/zotero/literature-families.csv"
OUT_JSON = ROOT / "literature/zotero/literature-families.json"

NAMES = {
    "F1": "Materials use and recontextualization",
    "F2": "Ecological teacher agency",
    "F3": "Translanguaging and multilingual mediation",
    "F4": "Curriculum policy and institutional conditions",
    "F5": "Localization, culture, and learner fit",
    "F6": "Teacher identity and professional learning",
    "F7": "Pakistan and South Asian contexts",
    "F8": "Chinese language pedagogy and contexts",
}
TARGETS = {
    "F1": 131,
    "F2": 59,
    "F3": 58,
    "F4": 56,
    "F5": 45,
    "F6": 40,
    "F7": 25,
    "F8": 17,
}
CHAPTER_MAP = {
    "F1": "2.1 (mechanism: materials-in-use and recontextualization)",
    "F2": "2.2 (achievement: ecological teacher agency)",
    "F3": "2.3.2 / 2.3.4 (neighbouring practice, not automatically localizing)",
    "F4": "2.2.3 conditions; 2.4.1 institutional setting",
    "F5": "2.3 (field’s name: localization, culture, fit)",
    "F6": "2.2 iterational resources / identity; not a separate heading",
    "F7": "2.4 (Pakistan / South Asia as context, not enactment)",
    "F8": "2.3 / 2.4 as CFL object — small set, not every paper that mentions China",
}

# Tight CFL pedagogy/context set (combined target 17). Translanguaging-in-Chinese
# immersion stays in F3 unless also on this list.
F8_IDS = {
    "Bao20c",
    "Han26b",
    "Wan24h",
    "Lin23d",
    "Zha20b",
    "Zha24g",
    "Fac24",
    "Das23",
    "Dua24",
    "Gen26",
    "Yan19b",
    "Yan22d",
    "Hsi22",
    "Guo18b",
    "Gue22b",
    "Tsa20",
    "Ji22",
}


def parse_ris(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r"\nER  -\s*\n", text)
    recs = []
    for b in blocks:
        rec = defaultdict(list)
        key, val = None, []
        for line in b.splitlines():
            m = re.match(r"^([A-Z][A-Z0-9]{1,2})  - (.*)$", line)
            if m:
                if key:
                    rec[key].append(" ".join(val).strip())
                key, val = m.group(1), [m.group(2)]
            elif key:
                val.append(line.strip())
        if key:
            rec[key].append(" ".join(val).strip())
        if not rec.get("TI"):
            continue
        authors = rec.get("AU", [])
        year = (rec.get("PY") or rec.get("DA") or [""])[0][:4]
        if not authors:
            cite = f"Anon ({year})"
        elif len(authors) == 1:
            cite = f"{authors[0].split(',')[0]} ({year})"
        elif len(authors) == 2:
            cite = f"{authors[0].split(',')[0]} and {authors[1].split(',')[0]} ({year})"
        else:
            cite = f"{authors[0].split(',')[0]} et al. ({year})"
        n1 = " ".join(rec.get("N1", []))
        ctx = ""
        m = re.search(r"Context:\s*(.*?)(?:\s*\|\s*Main finding:|$)", n1)
        if m:
            ctx = m.group(1)
        kws = [k.lower() for k in rec.get("KW", [])]
        recs.append(
            {
                "id": (rec.get("ID") or [""])[0],
                "cite": cite,
                "year": year or "",
                "title": re.sub(r"\s+", " ", rec["TI"][0]).strip(),
                "doi": (rec.get("DO") or [""])[0],
                "journal": (rec.get("JO") or rec.get("T2") or [""])[0],
                "kws": kws,
                "n1": n1,
                "ctx": ctx,
                "ab": " ".join(rec.get("AB", [])),
                "source": "undermind-220",
                "tier": "core" if "priority-core" in kws else "archive",
                "hold": "METADATA INCOMPLETE" in n1
                or "abstract unavailable" in n1.lower()
                or "metadata only" in n1.lower(),
            }
        )
    return recs


EXTRAS = [
    dict(
        id="Lu24",
        cite="Lu et al. (2024)",
        year="2024",
        title="Scenario analysis of localization and adaptation of Chinese language teaching",
        doi="10.52131/pjhss.2024.v12i4.2553",
        journal="Pakistan Journal of Humanities and Social Sciences",
        kws=[],
        n1="Related programme with Lu and Hanif (2025); count once",
        ctx="Pakistan; HSK Standard Course",
        ab="localization urdu hsk pakistan chinese teachers",
        source="pakistan-extra",
        tier="core",
        hold=False,
    ),
    dict(
        id="Lu25",
        cite="Lu and Hanif (2025)",
        year="2025",
        title="Pedagogical challenges faced by Pakistani teachers of the Chinese language, the role of Urdu language, and additional recommendations",
        doi="10.52015/daryaft.v17i02.436",
        journal="DARYAFT",
        kws=[],
        n1="Related to Lu et al. (2024); not independent evidence",
        ctx="Pakistan; HSK Standard Course",
        ab="pakistan urdu hsk chinese teachers",
        source="pakistan-extra",
        tier="core",
        hold=False,
    ),
    dict(
        id="Naheed26",
        cite="Naheed (2026)",
        year="2026",
        title="Professional development for local Chinese language teachers in Pakistan",
        doi="10.5281/zenodo.19115312",
        journal="International Journal of Politics & Social Sciences Review",
        kws=[],
        n1="",
        ctx="Pakistan; 55 local teachers; HSK Standard Course",
        ab="professional development pakistan chinese teachers hsk urdu",
        source="pakistan-extra",
        tier="core",
        hold=False,
    ),
    dict(
        id="CWang22",
        cite="C. Wang (2022)",
        year="2022",
        title="国际传播视角下的巴基斯坦汉语教学研究",
        doi="",
        journal="Doctoral dissertation, Central China Normal University",
        kws=[],
        n1="PDF outstanding",
        ctx="Pakistan Chinese teaching programmes",
        ab="pakistan chinese teaching",
        source="pakistan-extra",
        tier="core",
        hold=True,
    ),
    dict(
        id="Hanif23",
        cite="Hanif (2023)",
        year="2023",
        title="Current scenario and perspective of teaching Chinese at Confucius Institutes in Pakistan",
        doi="10.52131/pjhss.2023.1102.0530",
        journal="Pakistan Journal of Humanities and Social Sciences",
        kws=[],
        n1="Same programme background as Lu",
        ctx="Pakistan Confucius Institutes",
        ab="pakistan confucius institute teachers materials",
        source="pakistan-extra",
        tier="core",
        hold=False,
    ),
    dict(
        id="Azeem22",
        cite="Azeem et al. (2022)",
        year="2022",
        title="Chinese language teaching in Pakistan problems and solutions",
        doi="10.56220/uwjss2022/0501/04",
        journal="University of Wah Journal of Social Sciences",
        kws=[],
        n1="",
        ctx="Pakistan universities",
        ab="pakistan curriculum teachers english annotated textbooks",
        source="pakistan-extra",
        tier="core",
        hold=False,
    ),
    dict(
        id="Khan22",
        cite="Khan et al. (2022)",
        year="2022",
        title="Chinese as a mandatory foreign language at a higher education institution in Pakistan",
        doi="10.1177/02627280221120328",
        journal="South Asia Research",
        kws=[],
        n1="",
        ctx="Pakistan higher education institution",
        ab="pakistan policy class size medium of instruction",
        source="pakistan-extra",
        tier="core",
        hold=False,
    ),
    dict(
        id="Ali22",
        cite="Ali and David (2022)",
        year="2022",
        title="Challenges of teaching Chinese as a subject in an English-dominated region: Focus on Sindh, Pakistan",
        doi="10.51611/iars.irj.v12i01.2022.182",
        journal="IARS International Research Journal",
        kws=[],
        n1="",
        ctx="Sindh, Pakistan",
        ab="pakistan sindh english urdu chinese",
        source="pakistan-extra",
        tier="core",
        hold=False,
    ),
    dict(
        id="Jabbar25",
        cite="Jabbar (2025)",
        year="2025",
        title="Chinese language education in Pakistan: Historical developments, current landscape, and future prospects",
        doi="10.63878/qrjs196",
        journal="Qualitative Research Journal for Social Studies",
        kws=[],
        n1="",
        ctx="Pakistan",
        ab="pakistan chinese language education landscape",
        source="pakistan-extra",
        tier="core",
        hold=False,
    ),
    dict(
        id="Aftab24",
        cite="Aftab and Abbasi (2024)",
        year="2024",
        title="Beliefs about difficulties in learning Chinese as a foreign language in a public sector university",
        doi="10.58921/sjl.v3i1.61",
        journal="Sindh Journal of Linguistics",
        kws=[],
        n1="",
        ctx="Pakistan public-sector university",
        ab="pakistan learner difficulties chinese",
        source="pakistan-extra",
        tier="grouped",
        hold=False,
    ),
    dict(
        id="Iftikhar24",
        cite="Iftikhar et al. (2024)",
        year="2024",
        title="Perceptions, challenges, and opportunities of Chinese language learning in Punjab and Sindh, Pakistan",
        doi="10.1155/2024/6662409",
        journal="New Directions for Child and Adolescent Development",
        kws=[],
        n1="Landscape only until PDF is read",
        ctx="Punjab and Sindh, Pakistan",
        ab="pakistan cpec chinese learning",
        source="pakistan-extra",
        tier="grouped",
        hold=True,
    ),
    dict(
        id="Bernstein00",
        cite="Bernstein (2000)",
        year="2000",
        title="Pedagogy, symbolic control and identity: Theory, research, critique (Rev. ed.)",
        doi="",
        journal="Rowman & Littlefield",
        kws=["recontextualization"],
        n1="Foundational for 2.1.1",
        ctx="Curriculum sociology",
        ab="recontextualization pedagogic device",
        source="foundational",
        tier="core",
        hold=False,
    ),
    dict(
        id="Emirbayer98",
        cite="Emirbayer and Mische (1998)",
        year="1998",
        title="What is agency?",
        doi="10.1086/231294",
        journal="American Journal of Sociology",
        kws=["ecological-agency"],
        n1="Foundational for 2.2.2",
        ctx="Social theory",
        ab="agency chordal triad",
        source="foundational",
        tier="core",
        hold=False,
    ),
    dict(
        id="Bandura01",
        cite="Bandura (2001)",
        year="2001",
        title="Social cognitive theory: An agentic perspective",
        doi="10.1146/annurev.psych.52.1.1",
        journal="Annual Review of Psychology",
        kws=[],
        n1="Competing capacity model for 2.2.1",
        ctx="Social cognitive theory",
        ab="agency capacity self-efficacy",
        source="foundational",
        tier="core",
        hold=False,
    ),
]


def rx(pat: str, s: str) -> bool:
    return bool(re.search(pat, s or "", re.I))


def families_for(r: dict) -> list[str]:
    title = r["title"]
    site = f"{title} {r['ctx']}"
    kws = set(r["kws"])
    fams: set[str] = set()

    if r["source"] == "pakistan-extra" or rx(
        r"pakistan|pakistani|sindh|sri lanka|nepal|nepalese|bangladesh",
        site,
    ):
        fams.add("F7")

    if r["id"] in F8_IDS:
        fams.add("F8")

    if (
        "materials-use" in kws
        or "recontextualization" in kws
        or rx(
            r"recontextual|materials[- ]use|textbook|coursebook|teaching materials|instructional materials|materials adaptation|curriculum materials|coursebook utilization|prescribed (?:teaching )?materials|materials development|using new language materials|material-mediated|materials-in-action|materials in the classroom|elt materials",
            title + " " + " ".join(kws),
        )
    ):
        fams.add("F1")

    if "ecological-agency" in kws or rx(
        r"teacher agency|ecological (?:teacher )?agency|agentic use|agentic engagement|agency-as-achievement|what is agency\?|an agentic perspective|restricted agency|professional agency|language teacher agency",
        title + " " + " ".join(kws),
    ):
        fams.add("F2")

    if "translanguaging" in kws or rx(
        r"translanguag|multilingual (?:mediation|writing|english classroom)|medium of instruction|codeswitch|code-switch|bilingual repertoire|learning chinese through english|\bl1\b|first language|mother tongue|english-only",
        title + " " + " ".join(kws),
    ):
        fams.add("F3")
    if "F3" not in fams and rx(
        r"translanguag|\bl1\b|first language|mother tongue|multilingual|medium of instruction|urdu as",
        r["ab"],
    ):
        fams.add("F3")

    if rx(
        r"curriculum (?:reform|policy|change|standard|design|making)|textbooks policy|education(?:al)? policy|national (?:curriculum|standards|teaching quality)|confucius institute|mandatory (?:foreign )?language|policy implementation|core competencies|cefr-like policies|qualifications frameworks",
        title,
    ) or rx(
        r"curriculum reform|new textbooks policy|national teaching quality|confucius institute|mandatory chinese|institutional (?:constraint|culture)|high-stakes|accountability",
        r["ctx"] + " " + r["n1"] + " " + r["ab"],
    ):
        fams.add("F4")

    if rx(
        r"locali[sz]e|locali[sz]ation|local culture|localising|localizing|cultural (?:content|representation|adaptation|mismatch|awareness|threads)|culturally local|funds of knowledge|\bthe local\b|imported (?:cefr )?textbook|global chinese|confronting culture",
        title,
    ) or (
        rx(r"locali[sz]|local culture|cultural (?:mismatch|representation)|global textbook", r["ab"])
        and rx(r"local|cultur|imported|global", title + " " + r["ctx"])
    ):
        fams.add("F5")

    if rx(
        r"teacher identity|professional (?:identity|development|learning|practice)|identity reconstruction|identity-agency|teacher learning|materials developers|kit bag|teacher professional identity",
        title,
    ) or rx(
        r"teacher identity|professional development|professional learning|materials developer",
        r["ab"] + " " + title,
    ):
        fams.add("F6")

    if r["id"] == "Bernstein00":
        fams.add("F1")
    if r["id"] in ("Emirbayer98", "Bandura01", "Har25"):
        fams.add("F2")

    return sorted(fams)


PRIMARY_ORDER = ["F7", "F2", "F3", "F8", "F5", "F6", "F4", "F1"]


def primary_of(fams: list[str], r: dict) -> str:
    if r["id"] == "Bernstein00":
        return "F1"
    if r["id"] in ("Emirbayer98", "Bandura01"):
        return "F2"
    if r["source"] == "pakistan-extra":
        return "F7"
    if not fams:
        return "F1"
    for p in PRIMARY_ORDER:
        if p in fams:
            return p
    return fams[0]


def load() -> list[dict]:
    recs = parse_ris(RIS)
    have = {r["title"].lower()[:55] for r in recs}
    for e in EXTRAS:
        if e["title"].lower()[:55] not in have:
            recs.append(e)
    for r in recs:
        fams = families_for(r)
        r["fams"] = fams
        r["primary"] = primary_of(fams, r)
        r["also"] = [f for f in fams if f != r["primary"]]
    recs.sort(key=lambda r: (r["year"], r["cite"].lower()))
    return recs


def md_escape(s: str) -> str:
    return s.replace("|", "/")


def write_outputs(recs: list[dict]) -> None:
    comb = Counter()
    prim = Counter()
    by_fam = defaultdict(list)
    for r in recs:
        prim[r["primary"]] += 1
        for f in r["fams"]:
            comb[f] += 1
            by_fam[f].append(r)

    unique = len(recs)
    combined = sum(comb.values())

    lines = []
    a = lines.append
    a("# Chapter 2 literature arrangement")
    a("")
    a("**Status: arrange first. Do not write more Chapter 2 prose until this table is stable.**")
    a("")
    a("**Study.** Recontextualization of Chinese-Language Teaching Materials and Teacher Agency among Pakistani Teachers of Chinese: A Qualitative Study from an Ecological Perspective / 巴基斯坦本土中文教师的中文教材再语境化与教师能动性研究——一项生态视角下的质性研究.")
    a("")
    a("This file sorts the library into the eight **corpus families** below. A paper may sit in more than one family (combined count). For later writing, each paper still has **one primary family** so the chapter does not dump the same study eight times.")
    a("")
    a("## Counts")
    a("")
    a("| Family | Target (combined) | This corpus (combined) | Primary (unique) | Chapter 2 home |")
    a("|---|---:|---:|---:|---|")
    for fid, name in NAMES.items():
        a(
            f"| {name} | {TARGETS[fid]} | {comb[fid]} | {prim[fid]} | {CHAPTER_MAP[fid]} |"
        )
    a(f"| **Total** | **431** | **{combined}** | **{unique} unique papers** | |")
    a("")
    a("### How to read the 431")
    a("")
    a(f"- **Unique papers in hand:** {unique} (220 Undermind rows + Pakistan extras + three foundational texts).")
    a(f"- **Combined memberships in this arrangement:** {combined} (papers tagged to more than one family).")
    a("- **Your 431** is a combined figure. It is not 431 different studies. This corpus cannot invent rows that are not in the RIS, the Pakistan extras, or the foundational texts.")
    a("- **F1 is 128 against 131.** Three rows may sit in a larger Zotero library; they are not invented here. F8 is held to a 17-paper CFL pedagogy/context set so Chinese-immersion translanguaging stays in F3. F7 is **study site** (Pakistan, Sri Lanka, Nepal, Bangladesh), not every paper whose Undermind note mentions Pakistani teachers.")
    a("- **F7 target 25 / this corpus 16.** Eleven Pakistan studies plus five other South Asian sites. The remaining nine are not in this library as South Asian *sites* (they may live in a larger Zotero library, or they may be Southeast Asian analogues). Do not fill the nine with Indonesia/Malaysia/Vietnam.")
    a("- **F3, F4, F5, F6** run under the 431 targets because many Undermind rows are EFL textbook-agency studies that only weakly mention policy, culture, identity, or L1. They are listed where the title, context field, or abstract actually supports the tag.")
    a("")
    a("## Writing rule (when writing resumes)")
    a("")
    a("| Rule | Meaning |")
    a("|---|---|")
    a("| One primary family | The paper is *discussed* under that family’s Chapter 2 home. |")
    a("| Secondary families | Named in a list, not given a second close discussion. |")
    a("| Related publications | Lu et al. (2024) + Lu and Hanif (2025) = one programme. Zhao (2020, 2024) + Zhao et al. (2024b) = one Australian programme. |")
    a("| Hold | Metadata-only / PDF outstanding. Do not cite as if read. |")
    a("| Not yet | CNKI; papers 221–240 if they exist. |")
    a("")
    a("Machine-readable copy: `literature/zotero/literature-families.csv`.")
    a("")

    for fid, name in NAMES.items():
        rows = sorted(by_fam[fid], key=lambda r: (r["primary"] != fid, r["cite"].lower()))
        a(f"## {fid}  {name}")
        a("")
        a(f"Target combined **{TARGETS[fid]}**. This corpus combined **{comb[fid]}** ({prim[fid]} as primary). Home: {CHAPTER_MAP[fid]}.")
        a("")
        a("| Cite | Title | Role | Also in | Hold |")
        a("|---|---|---|---|---|")
        for r in rows:
            role = "primary" if r["primary"] == fid else "secondary"
            also = ", ".join(r["also"]) if r["primary"] == fid else r["primary"]
            hold = "yes" if r["hold"] else ""
            a(
                f"| {md_escape(r['cite'])} | {md_escape(r['title'])} | {role} | {also} | {hold} |"
            )
        a("")

    a("## Related-publication groups (do not count twice)")
    a("")
    a("- Lu et al. (2024) and Lu and Hanif (2025); Hanif (2023) is programme background.")
    a("- Zhao (2020), Zhao (2024), and Zhao et al. (2024b / Fac24).")
    a("")
    a("## Still required before writing resumes")
    a("")
    a("- Confirm or supply the nine F7 papers that would bring Pakistan/South Asia from 16 to 25.")
    a("- CNKI (教材再语境化, 教师能动性, 本土化, 教材使用, 国际中文教育).")
    a("- C. Wang (2022) PDF; Iftikhar et al. (2024) PDF.")
    a("- Papers 221–240 if they exist in the original 240-paper search.")
    a("- Do not restore Shawer, Tibebu, or other hold items without a full text.")
    a("")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "cite",
                "year",
                "title",
                "primary",
                "families",
                "doi",
                "source",
                "tier",
                "hold",
                "journal",
            ],
        )
        w.writeheader()
        for r in recs:
            w.writerow(
                {
                    "id": r["id"],
                    "cite": r["cite"],
                    "year": r["year"],
                    "title": r["title"],
                    "primary": r["primary"],
                    "families": ";".join(r["fams"]),
                    "doi": r["doi"],
                    "source": r["source"],
                    "tier": r["tier"],
                    "hold": r["hold"],
                    "journal": r["journal"],
                }
            )

    slim = [
        {
            k: r[k]
            for k in (
                "id",
                "cite",
                "year",
                "title",
                "primary",
                "fams",
                "doi",
                "source",
                "tier",
                "hold",
            )
        }
        for r in recs
    ]
    OUT_JSON.write_text(json.dumps(slim, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"unique {unique} combined {combined}")
    for fid, name in NAMES.items():
        print(f"{fid} {name:46} prim={prim[fid]:3} comb={comb[fid]:3} tgt={TARGETS[fid]:3} d={comb[fid]-TARGETS[fid]:+d}")
    print("wrote", OUT_MD)
    print("wrote", OUT_CSV)


if __name__ == "__main__":
    write_outputs(load())
