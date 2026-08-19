# Heena · Zotero library

A browser for [Zotero](https://www.zotero.org/) libraries: collections, search, item details, and citation export. The app talks to [Zotero Web API v3](https://www.zotero.org/support/dev/web_api/v3/basics) or opens a built-in demo shelf so you can try it without credentials.

## Run

```bash
npm install
npm test
npm run dev
```

Then open the printed local URL. Use **Open demo library** to browse sample papers, or **Connect Zotero** with a numeric user ID (or group ID) and an API key from [zotero.org/settings/keys](https://www.zotero.org/settings/keys). Public libraries can omit the key.

```bash
npm run build
npm run preview
```

## What it does

- Three-pane layout: collections and tags, item list, detail card
- Quick search across titles, authors, abstracts, and tags
- APA, MLA, Chicago, and BibTeX citations, plus a `.bib` export of the current list
- Demo mode can add local items; they stay in the current browser session
- Zotero credentials are stored only in `localStorage` on this machine
