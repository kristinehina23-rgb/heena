# Add these papers to Zotero

This folder is a one-step import of the Undermind evidence tables. This Cloud Agent cannot open your Zotero library, so the papers are packaged for **File → Import**.

**Import this file:** `papers-1-240.ris` (220 items).

The last uploaded table is labelled 181–240 but contains **40 rows (papers 181–220)**. Papers **221–240 are not in the Word file**. Do not import `papers-1-120.ris` as well, or you will duplicate the first 120 items.

## Recommended: import the RIS file

1. Open **Zotero**.
2. File → **Import**.
3. Choose `literature/zotero/papers-1-240.ris`.
4. Tick **Place imported collections and items into new collection**.
5. Name the collection, for example: `Teacher agency — Undermind 1–220`.
6. Finish. You should see **220 items**.

Each item already has:

- authors, title, year, journal/book, DOI and URL (where Crossref found them)
- **tags**: `thesis`, `undermind`, batch tags (`undermind-1-60` … `undermind-181-240`), plus `ecological-agency`, `recontextualization`, `materials-use`, `CFL-CAL`, `translanguaging` when those words appear in the evidence table
- a **note** with the evidence-table columns (framework, concept, method, context, finding, relevance)

After import, use the tag pane to filter. That keeps Chapter 2 pointed at the gap paragraph in `dissertation/GAP-STATEMENT.md`.

**Add these four Pakistan records by hand** (they are not in the 220-item RIS). Verified APA records are in `dissertation/chapter-02-literature-review.md` and `dissertation/REFERENCE-VERIFICATION.md`:

- Lu, X., Tan, A., Ma, Y., Feng, H., & Hanif, B. (2024). https://doi.org/10.52131/pjhss.2024.v12i4.2553
- Lu, X., & Hanif, B. (2025). https://doi.org/10.52015/daryaft.v17i02.436 — **related to Lu et al. (2024), not independent evidence**
- Naheed, U. (2026). https://doi.org/10.5281/zenodo.19115312
- Wang, C. (2022). Doctoral dissertation, Central China Normal University (no DOI; attach the PDF when you have it)

Chapter 2 no longer cites items marked metadata-only / abstract-unavailable in the evidence tables. Do not restore Shawer (2010, 2017), Guerrettaz, Engman and Matsumoto (2021), Hsiang et al. (2022), Lestari (2019), Tibebu (2020), Biesta and Tedder (2006), or the 2015 Priestley/Biesta/Robinson book without a verified full text.

## Optional: add by DOI only

Paste `dois.txt` (201 DOIs) into Zotero’s **Add Item(s) by Identifier**. You will still need the RIS file for items with no DOI, and you will lose the evidence-table notes unless you import the RIS.

## 22 items to check by hand

These have no reliable Crossref record. They are in the RIS file with `METADATA INCOMPLETE`. Attach a PDF or library record before you cite them.

**Core theory / methods (check first):** Bie06 (Biesta & Tedder 2006 working paper).

**Others:** Les19, Pha19, Med19, Gra20b, Qia13, Dua08, Wet11c, Fen13b, Zha10d, Mig16, Tib20, Can09, Kul15, Tav21, Guo18b, Riz18, Wal15, Tea20, Gan14, Lee14b, Sim17.

## Also in this folder

- `papers-1-240.bib` — same 220 items for Overleaf / XeLaTeX
- `papers-1-120.ris` / `papers-1-120.bib` — earlier subset; superseded
- `dois.txt` — one DOI per line
