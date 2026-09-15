#!/usr/bin/env python3
"""Apply the official 240 one-primary-family assignments. Does not write Chapter 2."""

from __future__ import annotations

import csv
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
ASSIGN_DOCX = ROOT / "literature/240_primary_family_assignments.docx"
RIS = ROOT / "literature/zotero/papers-1-240.ris"
EVIDENCE_FILES = [
    (ROOT / "literature/240_paper_evidence_table_1-60.docx", 1),
    (ROOT / "literature/240_paper_evidence_table_61-120.docx", 61),
    (ROOT / "literature/240_paper_evidence_table_121-180.docx", 121),
    (ROOT / "literature/240_paper_evidence_table_181-240.docx", 181),
]
OUT_MD = ROOT / "dissertation/LITERATURE-ARRANGEMENT.md"
OUT_CSV = ROOT / "literature/zotero/literature-families.csv"
OUT_JSON = ROOT / "literature/zotero/literature-families.json"

FAMILY_CODE = {
    "Materials use and recontextualization": "F1",
    "Ecological teacher agency": "F2",
    "Translanguaging and multilingual mediation": "F3",
    "Curriculum policy and institutional conditions": "F4",
    "Localization, culture, and learner fit": "F5",
    "Teacher identity and professional learning": "F6",
    "Pakistan and South Asian contexts": "F7",
    "Chinese language pedagogy and contexts": "F8",
}
CODE_NAME = {v: k for k, v in FAMILY_CODE.items()}
DISPLAY_ORDER = ["F1", "F3", "F2", "F4", "F5", "F6", "F7", "F8"]
PRIMARY_TARGETS = {
    "F1": 81,
    "F3": 40,
    "F2": 35,
    "F4": 27,
    "F5": 23,
    "F6": 22,
    "F7": 5,
    "F8": 7,
}
COMBINED_TARGETS = {
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

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def cell_text(tc) -> str:
    texts = [t.text or "" for t in tc.iter(f"{W_NS}t")]
    return re.sub(r"\s+", " ", "".join(texts)).strip()


def docx_tables(path: Path) -> list[list[list[str]]]:
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    out = []
    for tbl in root.iter(f"{W_NS}tbl"):
        rows = []
        for tr in tbl.findall(f"{W_NS}tr"):
            cells = [cell_text(tc) for tc in tr.findall(f"{W_NS}tc")]
            if any(cells):
                rows.append(cells)
        out.append(rows)
    return out


def parse_assignments(path: Path) -> list[dict]:
    assignments = []
    for tbl in docx_tables(path):
        if not tbl:
            continue
        header = [c.lower() for c in tbl[0]]
        if len(header) < 3 or "rank" not in header[0] or "paper" not in header[1]:
            continue
        for row in tbl[1:]:
            if len(row) < 3 or not row[0].strip().isdigit():
                continue
            paper = row[1].strip()
            m = re.search(r"\[([^\]]+)\]", paper)
            key = m.group(1) if m else paper.strip("[]")
            fam = row[2].strip()
            if fam not in FAMILY_CODE:
                raise SystemExit(f"Unknown family for {key}: {fam}")
            assignments.append(
                {
                    "assignment_rank": int(row[0]),
                    "key": key,
                    "primary_family": fam,
                    "family_code": FAMILY_CODE[fam],
                }
            )
    assignments.sort(key=lambda a: a["assignment_rank"])
    if len(assignments) != 240:
        raise SystemExit(f"Expected 240 assignments, got {len(assignments)}")
    keys = [a["key"] for a in assignments]
    if len(set(keys)) != 240:
        raise SystemExit("Duplicate keys in assignment file")
    return assignments


def parse_evidence() -> dict[str, dict]:
    by_key = {}
    for path, start in EVIDENCE_FILES:
        tbl = docx_tables(path)[0]
        for i, row in enumerate(tbl[1:]):
            author = row[0] if row else ""
            m = re.search(r"\[([A-Za-z0-9]+)\]", author)
            if not m:
                continue
            key = m.group(1)
            by_key[key] = {
                "evidence_rank": start + i,
                "author_year": author,
                "journal": row[1] if len(row) > 1 else "",
                "method": row[4] if len(row) > 4 else "",
                "context": row[5] if len(row) > 5 else "",
                "finding": row[6] if len(row) > 6 else "",
            }
    return by_key


def parse_ris(path: Path) -> dict[str, dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r"\nER  -\s*\n", text)
    by_id = {}
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
        rid = (rec.get("ID") or [""])[0]
        if not rid or not rec.get("TI"):
            continue
        n1 = " ".join(rec.get("N1", []))
        by_id[rid] = {
            "authors": rec.get("AU", []),
            "year": (rec.get("PY") or rec.get("DA") or [""])[0][:4],
            "title": re.sub(r"\s+", " ", rec["TI"][0]).strip(),
            "doi": (rec.get("DO") or [""])[0],
            "journal": (rec.get("JO") or rec.get("T2") or [""])[0],
            "n1": n1,
            "hold": (
                "METADATA INCOMPLETE" in n1
                or "abstract unavailable" in n1.lower()
                or "metadata only" in n1.lower()
            ),
        }
    return by_id


def cite_from_evidence(author_year: str, year: str) -> str:
    s = re.sub(r"\s*\[[^\]]+\]\s*", " ", author_year)
    s = re.sub(
        r"\s*(full PDF|metadata only|abstract unavailable|unknown source).*$",
        "",
        s,
        flags=re.I,
    )
    s = re.sub(r",\s*\d{4}[a-z]?\s*$", "", s).strip()
    s = s.replace(" & ", " and ")
    s = re.sub(r"\s+", " ", s)
    return f"{s} ({year})" if s else f"[{year}]"


def md_cell(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


PAKISTAN_OVERLAY = [
    {
        "id": "Lu24",
        "cite": "Lu et al. (2024)",
        "year": "2024",
        "title": "Scenario analysis of localization and adaptation of Chinese language teaching",
        "doi": "10.52131/pjhss.2024.v12i4.2553",
        "note": "Related programme with Lu and Hanif (2025); count once. Needed for 2.4 even though F7 primary in the 240 is only five papers.",
        "hold": False,
    },
    {
        "id": "Lu25",
        "cite": "Lu and Hanif (2025)",
        "year": "2025",
        "title": "Pedagogical challenges faced by Pakistani teachers of the Chinese language, the role of Urdu language, and additional recommendations",
        "doi": "10.52015/daryaft.v17i02.436",
        "note": "Related to Lu et al. (2024); not independent evidence.",
        "hold": False,
    },
    {
        "id": "Naheed26",
        "cite": "Naheed (2026)",
        "year": "2026",
        "title": "Professional development for local Chinese language teachers in Pakistan",
        "doi": "10.5281/zenodo.19115312",
        "note": "2.4 teachers / materials landscape.",
        "hold": False,
    },
    {
        "id": "CWang22",
        "cite": "C. Wang (2022)",
        "year": "2022",
        "title": "国际传播视角下的巴基斯坦汉语教学研究",
        "doi": "",
        "note": "PDF outstanding. Landscape only.",
        "hold": True,
    },
    {
        "id": "Hanif23",
        "cite": "Hanif (2023)",
        "year": "2023",
        "title": "Current scenario and perspective of teaching Chinese at Confucius Institutes in Pakistan",
        "doi": "10.52131/pjhss.2023.1102.0530",
        "note": "Same programme background as Lu.",
        "hold": False,
    },
    {
        "id": "Azeem22",
        "cite": "Azeem et al. (2022)",
        "year": "2022",
        "title": "Chinese language teaching in Pakistan problems and solutions",
        "doi": "10.56220/uwjss2022/0501/04",
        "note": "2.4 institutional / materials landscape.",
        "hold": False,
    },
    {
        "id": "Khan22",
        "cite": "Khan et al. (2022)",
        "year": "2022",
        "title": "Chinese as a mandatory foreign language at a higher education institution in Pakistan",
        "doi": "10.1177/02627280221120328",
        "note": "2.4 policy / institutional setting.",
        "hold": False,
    },
    {
        "id": "Ali22",
        "cite": "Ali and David (2022)",
        "year": "2022",
        "title": "Challenges of teaching Chinese as a subject in an English-dominated region: Focus on Sindh, Pakistan",
        "doi": "10.51611/iars.irj.v12i01.2022.182",
        "note": "Pakistan extra. Assignment key Ali22b has no RIS/evidence record; do not merge with this item until confirmed.",
        "hold": False,
    },
    {
        "id": "Jabbar25",
        "cite": "Jabbar (2025)",
        "year": "2025",
        "title": "Chinese language education in Pakistan: Historical developments, current landscape, and future prospects",
        "doi": "10.63878/qrjs196",
        "note": "Landscape.",
        "hold": False,
    },
    {
        "id": "Aftab24",
        "cite": "Aftab and Abbasi (2024)",
        "year": "2024",
        "title": "Beliefs about difficulties in learning Chinese as a foreign language in a public sector university",
        "doi": "10.58921/sjl.v3i1.61",
        "note": "2.4 learner background.",
        "hold": False,
    },
    {
        "id": "Iftikhar24",
        "cite": "Iftikhar et al. (2024)",
        "year": "2024",
        "title": "Perceptions, challenges, and opportunities of Chinese language learning in Punjab and Sindh, Pakistan",
        "doi": "10.1155/2024/6662409",
        "note": "Landscape only until PDF is read.",
        "hold": True,
    },
]

FOUNDATIONAL = [
    {
        "id": "Bernstein00",
        "cite": "Bernstein (2000)",
        "year": "2000",
        "title": "Pedagogy, symbolic control and identity: Theory, research, critique (Rev. ed.)",
        "doi": "",
        "home": "2.1.1–2.1.3 (A0). Not one of the 240 assigned rows.",
    },
    {
        "id": "Emirbayer98",
        "cite": "Emirbayer and Mische (1998)",
        "year": "1998",
        "title": "What is agency?",
        "doi": "10.1086/231294",
        "home": "2.2.2 (B0). Not one of the 240 assigned rows.",
    },
    {
        "id": "Bandura01",
        "cite": "Bandura (2001)",
        "year": "2001",
        "title": "Social cognitive theory: An agentic perspective",
        "doi": "10.1146/annurev.psych.52.1.1",
        "home": "2.2.1 competing definition only. Not one of the 240 assigned rows.",
    },
]


def join_records(assignments, ris, evidence) -> list[dict]:
    rows = []
    for a in assignments:
        key = a["key"]
        r = ris.get(key)
        e = evidence.get(key)
        in_library = bool(r) and bool(e)
        year = (r or {}).get("year") or ""
        if not year and e:
            m = re.search(r"(19|20)\d{2}", e["author_year"])
            year = m.group(0) if m else ""
        if e and year:
            cite = cite_from_evidence(e["author_year"], year)
        elif r:
            authors = r["authors"]
            if not authors:
                cite = f"Anon ({year})"
            elif len(authors) == 1:
                cite = f"{authors[0].split(',')[0]} ({year})"
            elif len(authors) == 2:
                cite = f"{authors[0].split(',')[0]} and {authors[1].split(',')[0]} ({year})"
            else:
                cite = f"{authors[0].split(',')[0]} et al. ({year})"
        else:
            cite = f"[{key}]"
        title = (r or {}).get("title") or ""
        doi = (r or {}).get("doi") or ""
        journal = (e or {}).get("journal") or (r or {}).get("journal") or ""
        hold = False
        if r and r.get("hold"):
            hold = True
        if e and re.search(
            r"metadata only|abstract unavailable|unknown source",
            e["author_year"],
            re.I,
        ):
            hold = True
        if not in_library:
            hold = True
        rows.append(
            {
                **a,
                "cite": cite,
                "year": year,
                "title": title,
                "doi": doi,
                "journal": journal,
                "evidence_rank": (e or {}).get("evidence_rank"),
                "in_ris": bool(r),
                "in_evidence": bool(e),
                "bibliographic_status": "in-library" if in_library else "key-only",
                "hold": hold,
            }
        )
    return rows


def write_csv(rows: list[dict]) -> None:
    fields = [
        "assignment_rank",
        "key",
        "family_code",
        "primary_family",
        "cite",
        "year",
        "title",
        "doi",
        "journal",
        "evidence_rank",
        "in_ris",
        "in_evidence",
        "bibliographic_status",
        "hold",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def write_json(rows: list[dict], counts: Counter) -> None:
    payload = {
        "source": "literature/240_primary_family_assignments.docx",
        "note": "One primary family per paper. Combined/secondary tags are not in this file.",
        "primary_counts": {CODE_NAME[k]: counts[k] for k in DISPLAY_ORDER},
        "combined_targets": {CODE_NAME[k]: COMBINED_TARGETS[k] for k in DISPLAY_ORDER},
        "papers": rows,
        "pakistan_overlay": PAKISTAN_OVERLAY,
        "foundational": FOUNDATIONAL,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(rows: list[dict], counts: Counter) -> None:
    by_code = defaultdict(list)
    for r in rows:
        by_code[r["family_code"]].append(r)
    key_only = [r for r in rows if r["bibliographic_status"] == "key-only"]
    in_lib = [r for r in rows if r["bibliographic_status"] == "in-library"]
    hold_in_lib = [r for r in in_lib if r["hold"]]

    lines = []
    a = lines.append
    a("# Chapter 2 literature arrangement")
    a("")
    a("**Status: official primary families from `literature/240_primary_family_assignments.docx`. Do not write more Chapter 2 prose until this table is confirmed.**")
    a("")
    a("**Study.** Recontextualization of Chinese-Language Teaching Materials and Teacher Agency among Pakistani Teachers of Chinese: A Qualitative Study from an Ecological Perspective / 巴基斯坦本土中文教师的中文教材再语境化与教师能动性研究——一项生态视角下的质性研究.")
    a("")
    a("Each of the **240** papers has **one primary family**, assigned by main contribution, not every theme the paper touches. Secondary uses belong in a separate assigned-source / synthesis file. That file has **not** been uploaded, so this arrangement does **not** retag combined memberships.")
    a("")
    a("The previous auto-tag (`345` combined tags on `234` unique items) is superseded for primary assignment. Keep it only as history in git. Do not mix those tags with this file.")
    a("")
    a("## Two count systems")
    a("")
    a("| System | What it counts | Source | Total |")
    a("|---|---|---|---:|")
    a("| **Primary** | Unique papers, one family each | This assignment file | **240** |")
    a("| **Combined** | A paper may sit in more than one family | Counts supplied earlier; secondary file not in the repo | **431** |")
    a("")
    a("The two totals are compatible: `240` unique primaries + `191` extra (secondary) memberships = `431`. Until the secondary file arrives, do not invent those 191 tags.")
    a("")
    a("| Family | Combined (target) | Primary (official) | Implied secondary | Chapter 2 home |")
    a("|---|---:|---:|---:|---|")
    for code in DISPLAY_ORDER:
        combined = COMBINED_TARGETS[code]
        primary = counts[code]
        a(
            f"| {CODE_NAME[code]} | {combined} | {primary} | {combined - primary} | {CHAPTER_MAP[code]} |"
        )
    a(f"| **Total** | **431** | **{sum(counts.values())}** | **{431 - sum(counts.values())}** | |")
    a("")
    a("## Rank warning")
    a("")
    a("**Assignment rank is not evidence-table rank.** The assignment file numbers papers 1–240 in its own order. The four evidence tables number a different order (and only 220 rows). Do not treat assignment rank 141 as evidence-table row 141.")
    a("")
    a("The assignment preamble says the four evidence tables contain 240 unique papers. In this library the evidence tables plus `papers-1-240.ris` contain **220** bibliographic records. All 220 RIS IDs appear in the 240 assignments. **20 assignment keys have no title, DOI, or evidence-table row.**")
    a("")
    a("## Bibliographic coverage")
    a("")
    a(f"| Record | n |")
    a("|---|---:|")
    a(f"| Primary assignments | {len(rows)} |")
    a(f"| In RIS and evidence tables | {len(in_lib)} |")
    a(f"| Key only (no title in this library) | {len(key_only)} |")
    a(f"| In-library but metadata/PDF hold | {len(hold_in_lib)} |")
    a("")
    a("Machine-readable copy: `literature/zotero/literature-families.csv` and `literature/zotero/literature-families.json`. Regenerated by `literature/zotero/arrange_families.py`.")
    a("")
    a("## Writing rule (when writing resumes)")
    a("")
    a("| Rule | Meaning |")
    a("|---|---|")
    a("| One primary family | The paper is *discussed* under that family’s Chapter 2 home. |")
    a("| Secondary families | Wait for the assigned-source file. Do not dump the same study eight times. |")
    a("| Related publications | Lu et al. (2024) + Lu and Hanif (2025) = one programme. Zhao (2020, 2024) + Zhao et al. (2024b) = one Australian programme. |")
    a("| Hold | Metadata-only, PDF outstanding, or key-only. Do not cite as if read. |")
    a("| Pakistan extras | Outside the 240 unless a key is later confirmed. Still required for 2.4 because F7 primary here is only five papers. |")
    a("| Foundational texts | Bernstein (2000), Emirbayer and Mische (1998), Bandura (2001) are not in the 240. They remain concept-section sources. |")
    a("")
    a("## Key-only assignments (no RIS / evidence record)")
    a("")
    a("Do not invent titles for these twenty keys. They are the assignment-file ranks 141–160.")
    a("")
    a("| Assignment rank | Key | Primary family |")
    a("|---:|---|---|")
    for r in sorted(key_only, key=lambda x: x["assignment_rank"]):
        a(f"| {r['assignment_rank']} | `{r['key']}` | {r['primary_family']} |")
    a("")
    a("`Ali22b` is **not** merged with the Pakistan extra Ali and David (2022) until that identity is confirmed.")
    a("")

    for code in DISPLAY_ORDER:
        items = sorted(by_code[code], key=lambda x: x["assignment_rank"])
        a(f"## {code}  {CODE_NAME[code]}")
        a("")
        a(
            f"Official primary **{counts[code]}** (combined target **{COMBINED_TARGETS[code]}**). Home: {CHAPTER_MAP[code]}."
        )
        if code == "F7":
            a("")
            a("None of these five primaries is a verified Pakistan CFL classroom study. They are Nepal EFL (`Tha26`), Sri Lanka CFL textbooks (`Yas24`), a key-only row (`Ali22b`), Bangladesh EFL (`Sha14b`), and a Sri Lanka CFL checklist (`Das23`). Section 2.4 still depends on the Pakistan extras below.")
        a("")
        a("| Rank | Key | Cite | Title | Record | Hold |")
        a("|---:|---|---|---|---|---|")
        for r in items:
            rec = "in library" if r["bibliographic_status"] == "in-library" else "key only"
            hold = "yes" if r["hold"] else ""
            title = r["title"] if r["title"] else "—"
            a(
                f"| {r['assignment_rank']} | `{r['key']}` | {md_cell(r['cite'])} | {md_cell(title)} | {rec} | {hold} |"
            )
        a("")

    a("## Pakistan extras (outside the 240)")
    a("")
    a("F7 primary in the assignment file is **five** papers. Combined F7 is **25**. The difference is either secondary tags (not yet supplied) or these Pakistan studies, which are required for 2.4 and are not in `papers-1-240.ris`.")
    a("")
    a("| Cite | Title | Hold | Note |")
    a("|---|---|---|---|")
    for p in PAKISTAN_OVERLAY:
        a(
            f"| {md_cell(p['cite'])} | {md_cell(p['title'])} | {'yes' if p['hold'] else ''} | {md_cell(p['note'])} |"
        )
    a("")
    a("## Foundational texts (outside the 240)")
    a("")
    a("| Cite | Title | Home |")
    a("|---|---|---|")
    for p in FOUNDATIONAL:
        a(f"| {md_cell(p['cite'])} | {md_cell(p['title'])} | {md_cell(p['home'])} |")
    a("")
    a("## Related-publication groups (do not count twice)")
    a("")
    a("- Lu et al. (2024) and Lu and Hanif (2025); Hanif (2023) is programme background.")
    a("- Zhao (2020), Zhao (2024), and Zhao et al. (2024b / `Fac24`).")
    a("")
    a("## Still required before writing resumes")
    a("")
    a("- Confirm this primary-family table.")
    a("- Upload the assigned-source / synthesis file if combined (431) tags are to be used.")
    a("- Identify or supply bibliographic records for the 20 key-only assignments.")
    a("- CNKI (教材再语境化, 教师能动性, 本土化, 教材使用, 国际中文教育).")
    a("- C. Wang (2022) PDF; Iftikhar et al. (2024) PDF.")
    a("- Do not restore Shawer, Tibebu, Guerrettaz/Engman/Matsumoto (2021), Hsiang et al. (2022), Lestari (2019), Biesta and Tedder (2006), or the 2015 Priestley/Biesta/Robinson book without a full text.")
    a("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not ASSIGN_DOCX.exists():
        raise SystemExit(f"Missing {ASSIGN_DOCX}")
    assignments = parse_assignments(ASSIGN_DOCX)
    ris = parse_ris(RIS)
    evidence = parse_evidence()
    rows = join_records(assignments, ris, evidence)
    counts = Counter(r["family_code"] for r in rows)
    for code, n in PRIMARY_TARGETS.items():
        if counts[code] != n:
            raise SystemExit(f"{code} expected {n} primaries, got {counts[code]}")
    write_csv(rows)
    write_json(rows, counts)
    write_md(rows, counts)
    key_only = sum(1 for r in rows if r["bibliographic_status"] == "key-only")
    print(f"Wrote {len(rows)} primaries; {key_only} key-only; counts={dict(counts)}")
    print(f"  {OUT_MD}")
    print(f"  {OUT_CSV}")
    print(f"  {OUT_JSON}")


if __name__ == "__main__":
    main()
