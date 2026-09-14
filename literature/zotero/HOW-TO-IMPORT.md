# Add these papers to Zotero

This folder is a one-step import of **papers 1–120** from the Undermind evidence tables. This Cloud Agent cannot open your Zotero library, so the papers are packaged for **File → Import**.

## Recommended: import the RIS file

1. Open **Zotero**.
2. File → **Import**.
3. Choose `literature/zotero/papers-1-120.ris`.
4. Tick **Place imported collections and items into new collection**.
5. Name the collection, for example: `Teacher agency — Undermind 1–120`.
6. Finish. You should see **120 items**.

Each item already has:

- authors, title, year, journal/book, DOI and URL (where Crossref found them)
- **tags**: `thesis`, `undermind`, `undermind-1-60` or `undermind-61-120`, plus `ecological-agency`, `recontextualization`, `materials-use`, `CFL-CAL`, `translanguaging` when those words appear in the evidence table
- a **note** with the evidence-table columns (framework, concept, method, context, finding, relevance)

After import, use the tag pane to filter. That is the fastest way to keep Chapter 2 pointed at the gap paragraph.

## Optional: add by DOI only

If you prefer Zotero to fetch a fresh copy of each item:

1. File → Import, or the magic-wand **Add Item(s) by Identifier**.
2. Paste the contents of `dois.txt` (111 DOIs).
3. You will still need the RIS file for the **9 items with no DOI**, and you will **lose the evidence-table notes** unless you import the RIS.

## Nine items to check by hand

These have no reliable DOI. They are in the RIS file with a note `METADATA INCOMPLETE`. Find the PDF or a library record and attach it in Zotero before you cite them:

| Key | Paper |
|---|---|
| Bie06 | Biesta & Tedder, 2006, *How is agency possible?* (Exeter working paper — core theory) |
| Les19 | Lestari, 2019, teacher agency and localisation in Indonesia |
| Pha19 | Phan, 2019, English textbook use in Vietnamese classrooms |
| Med19 | Mede & Yalçin, 2019, textbook adaptation strategies |
| Gra20b | Grammatosi, 2020, PhD thesis on coursebook use |
| Qia13 | Wang Qiang, 2013, 课程·教材·教法 |
| Dua08 | Duarte & Escobar, 2008, adapted material and motivation |
| Wet11c | Wette, 2011, TESOL in Context |
| Fen13b | Zhang Fengjuan, 2013, Shandong Foreign Language Teaching Journal |

## Also in this folder

- `papers-1-120.bib` — same 120 items for Overleaf / XeLaTeX
- `dois.txt` — one DOI per line

Papers **121–240** are not in the evidence tables yet. Add them the same way when that file arrives.
