import "./styles.css";
import { fetchZoteroLibrary } from "./api";
import {
  creatorSortName,
  firstLast,
  formatCitation,
  itemTypeLabel,
  lastFirst,
  yearFromDate,
} from "./cite";
import { DEMO_COLLECTIONS, DEMO_ITEMS } from "./demo-data";
import type { CiteStyle, Collection, Connection, Item } from "./types";

type SortKey = "title" | "creator" | "year" | "type";

const STORAGE_KEY = "heena-zotero-connection";
const root = document.querySelector<HTMLDivElement>("#app");
if (!root) throw new Error("Missing #app");
const app = root;

let connection: Connection | null = loadConnection();
let collections: Collection[] = [];
let items: Item[] = [];
let selectedCollection = "all";
let selectedTag: string | null = null;
let selectedKey: string | null = null;
let query = "";
let sortKey: SortKey = "creator";
let citeStyle: CiteStyle = "apa";
let errorMessage = "";
let statusMessage = "";
let showConnect = false;
let showAdd = false;
let busy = false;

function loadConnection(): Connection | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Connection) : null;
  } catch {
    return null;
  }
}

function persistConnection(next: Connection | null) {
  if (!next) localStorage.removeItem(STORAGE_KEY);
  else localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
}

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function allTags(source: Item[]): string[] {
  return [...new Set(source.flatMap((item) => item.tags))].sort((a, b) => a.localeCompare(b));
}

function filteredItems(): Item[] {
  const q = query.trim().toLowerCase();
  return items
    .filter((item) => {
      if (selectedCollection === "unfiled") return item.collections.length === 0;
      if (selectedCollection !== "all" && !item.collections.includes(selectedCollection)) return false;
      if (selectedTag && !item.tags.includes(selectedTag)) return false;
      if (!q) return true;
      const haystack = [
        item.title,
        item.abstractNote,
        item.publicationTitle,
        item.conferenceName,
        ...item.creators.map((creator) => `${creator.firstName ?? ""} ${creator.lastName ?? ""} ${creator.name ?? ""}`),
        ...item.tags,
      ]
        .join(" ")
        .toLowerCase();
      return haystack.includes(q);
    })
    .sort((a, b) => {
      const dir = (left: string, right: string) => left.localeCompare(right, undefined, { sensitivity: "base" });
      if (sortKey === "title") return dir(a.title, b.title);
      if (sortKey === "year") return dir(yearFromDate(b.date), yearFromDate(a.date));
      if (sortKey === "type") return dir(a.itemType, b.itemType);
      return dir(creatorSortName(a), creatorSortName(b));
    });
}

function selectedItem(): Item | undefined {
  return items.find((item) => item.key === selectedKey) ?? filteredItems()[0];
}

function childCollections(parent: string | false): Collection[] {
  return collections.filter((collection) => collection.parentCollection === parent);
}

function renderTree(parent: string | false): string {
  return childCollections(parent)
    .map((collection) => {
      const nested = renderTree(collection.key);
      return `<li>
        <button type="button" data-collection="${escapeHtml(collection.key)}" class="${selectedCollection === collection.key ? "active" : ""}">${escapeHtml(collection.name)}</button>
        ${nested ? `<ul class="tree nested">${nested}</ul>` : ""}
      </li>`;
    })
    .join("");
}

function fieldValue(form: HTMLFormElement, name: string): string {
  const field = form.elements.namedItem(name);
  if (field instanceof HTMLInputElement || field instanceof HTMLTextAreaElement || field instanceof HTMLSelectElement) {
    return field.value.trim();
  }
  return "";
}

function renderGate() {
  app.innerHTML = `
    <section class="gate">
      <div class="gate-card">
        <div class="mark"><span></span> Heena library</div>
        <h1>A reading room for your Zotero shelves.</h1>
        <p class="lede">Browse collections, search the stack, and copy citations. Connect a Zotero user or group library, or open the built-in sample shelves first.</p>
        <div class="actions">
          <button class="btn" id="open-demo">Open demo library</button>
          <button class="btn secondary" id="toggle-connect">${showConnect ? "Hide connection" : "Connect Zotero"}</button>
        </div>
        ${errorMessage ? `<p class="error">${escapeHtml(errorMessage)}</p>` : ""}
        ${
          showConnect
            ? `<form class="connect" id="connect-form">
                <div class="fields">
                  <label>Library
                    <select name="libraryType">
                      <option value="user">User library</option>
                      <option value="group">Group library</option>
                    </select>
                  </label>
                  <label>User ID
                    <input name="userId" placeholder="Numeric user ID" />
                  </label>
                  <label>Group ID
                    <input name="groupId" placeholder="Optional for groups" />
                  </label>
                  <label>API key
                    <input name="apiKey" placeholder="From zotero.org/settings/keys" />
                  </label>
                </div>
                <p class="hint">Create a key at zotero.org/settings/keys. Public libraries can omit the key.</p>
                <button class="btn" type="submit" ${busy ? "disabled" : ""}>${busy ? "Opening…" : "Open library"}</button>
              </form>`
            : ""
        }
      </div>
    </section>
  `;

  document.getElementById("open-demo")?.addEventListener("click", () => {
    connection = { source: "demo", libraryType: "user" };
    persistConnection(connection);
    collections = structuredClone(DEMO_COLLECTIONS);
    items = structuredClone(DEMO_ITEMS);
    selectedKey = items[0]?.key ?? null;
    errorMessage = "";
    render();
  });
  document.getElementById("toggle-connect")?.addEventListener("click", () => {
    showConnect = !showConnect;
    render();
  });
  document.getElementById("connect-form")?.addEventListener("submit", (event) => {
    event.preventDefault();
    const form = event.currentTarget as HTMLFormElement;
    void connectZotero({
      source: "zotero",
      libraryType: fieldValue(form, "libraryType") === "group" ? "group" : "user",
      userId: fieldValue(form, "userId"),
      groupId: fieldValue(form, "groupId"),
      apiKey: fieldValue(form, "apiKey"),
    });
  });
}

async function connectZotero(next: Connection) {
  busy = true;
  errorMessage = "";
  render();
  try {
    const library = await fetchZoteroLibrary(next);
    connection = next;
    persistConnection(next);
    collections = library.collections;
    items = library.items;
    selectedCollection = "all";
    selectedTag = null;
    selectedKey = items[0]?.key ?? null;
    statusMessage = `${items.length} items from Zotero`;
  } catch (error) {
    errorMessage = error instanceof Error ? error.message : "Could not open the Zotero library.";
    connection = null;
  } finally {
    busy = false;
    render();
  }
}

function renderModal() {
  if (!showAdd) return "";
  return `
    <div class="modal-backdrop" id="modal">
      <form class="modal" id="add-form">
        <h3>Add to the demo shelves</h3>
        <label>Title <input name="title" required /></label>
        <div class="fields">
          <label>First name <input name="firstName" /></label>
          <label>Last name <input name="lastName" required /></label>
        </div>
        <div class="fields">
          <label>Type
            <select name="itemType">
              <option value="journalArticle">Journal article</option>
              <option value="book">Book</option>
              <option value="conferencePaper">Conference paper</option>
              <option value="webpage">Web page</option>
              <option value="preprint">Preprint</option>
            </select>
          </label>
          <label>Year <input name="date" placeholder="2024" /></label>
        </div>
        <label>Publication / venue <input name="venue" /></label>
        <label>Abstract <textarea name="abstractNote" rows="4"></textarea></label>
        <div class="cite-tools">
          <button class="btn" type="submit">Save item</button>
          <button class="btn secondary" type="button" id="cancel-add">Cancel</button>
        </div>
      </form>
    </div>
  `;
}

function renderLibrary() {
  const rows = filteredItems();
  const current = selectedItem();
  if (current && current.key !== selectedKey) selectedKey = current.key;
  const tags = allTags(items);

  app.innerHTML = `
    <div class="shell">
      <header class="topbar">
        <div class="brand"><strong>Heena</strong><em>${connection?.source === "demo" ? "demo library" : "zotero"}</em></div>
        <div class="search"><input id="search" value="${escapeHtml(query)}" placeholder="Search titles, authors, tags" /></div>
        <div class="top-actions">
          ${connection?.source === "demo" ? `<button class="btn" id="add-item">Add item</button>` : ""}
          <button class="btn ghost" id="export-bibtex">Export BibTeX</button>
          <button class="btn ghost" id="disconnect">Switch library</button>
        </div>
      </header>
      <main class="workspace">
        <aside class="pane sidebar">
          <h2>Collections</h2>
          <ul class="tree">
            <li><button type="button" data-collection="all" class="${selectedCollection === "all" ? "active" : ""}">My library</button></li>
            ${renderTree(false)}
            <li><button type="button" data-collection="unfiled" class="${selectedCollection === "unfiled" ? "active" : ""}">Unfiled</button></li>
          </ul>
          <h2>Tags</h2>
          <div class="tag-cloud">
            ${tags
              .map(
                (tag) =>
                  `<button type="button" data-tag="${escapeHtml(tag)}" class="${selectedTag === tag ? "active" : ""}">${escapeHtml(tag)}</button>`,
              )
              .join("")}
          </div>
        </aside>
        <section class="pane list">
          <div class="list-head">
            <button type="button" data-sort="title">Title</button>
            <button type="button" data-sort="creator">Creator</button>
            <button type="button" data-sort="year">Year</button>
            <button type="button" data-sort="type">Type</button>
          </div>
          ${
            rows.length === 0
              ? `<div class="empty">Nothing on this shelf matches the current filters.</div>`
              : rows
                  .map((item) => {
                    const creator = item.creators[0];
                    return `<button class="row ${item.key === selectedKey ? "active" : ""}" data-item="${escapeHtml(item.key)}">
                      <span class="title">${escapeHtml(item.title)}</span>
                      <span class="meta">${escapeHtml(creator ? lastFirst(creator) : "—")}</span>
                      <span class="meta">${escapeHtml(yearFromDate(item.date))}</span>
                      <span class="meta">${escapeHtml(itemTypeLabel(item.itemType))}</span>
                    </button>`;
                  })
                  .join("")
          }
        </section>
        <section class="pane detail">
          ${
            current
              ? `<p class="status">${escapeHtml(statusMessage || itemTypeLabel(current.itemType))}</p>
                 <h3>${escapeHtml(current.title)}</h3>
                 <div class="creators">${escapeHtml(current.creators.map(firstLast).join(", ") || "Unknown creator")}</div>
                 <div class="chips">
                   <span class="chip">${escapeHtml(yearFromDate(current.date))}</span>
                   ${current.publicationTitle ? `<span class="chip">${escapeHtml(current.publicationTitle)}</span>` : ""}
                   ${current.conferenceName ? `<span class="chip">${escapeHtml(current.conferenceName)}</span>` : ""}
                   ${current.DOI ? `<span class="chip">DOI ${escapeHtml(current.DOI)}</span>` : ""}
                   ${current.tags.map((tag) => `<span class="chip">${escapeHtml(tag)}</span>`).join("")}
                 </div>
                 ${current.abstractNote ? `<p class="abstract">${escapeHtml(current.abstractNote)}</p>` : ""}
                 <p class="muted">${current.url ? `<a href="${escapeHtml(current.url)}" target="_blank" rel="noreferrer">${escapeHtml(current.url)}</a>` : ""}</p>
                 <div class="cite-tools">
                   <label>Citation
                     <select id="cite-style">
                       <option value="apa" ${citeStyle === "apa" ? "selected" : ""}>APA</option>
                       <option value="mla" ${citeStyle === "mla" ? "selected" : ""}>MLA</option>
                       <option value="chicago" ${citeStyle === "chicago" ? "selected" : ""}>Chicago</option>
                       <option value="bibtex" ${citeStyle === "bibtex" ? "selected" : ""}>BibTeX</option>
                     </select>
                   </label>
                   <button class="btn" id="copy-cite">Copy citation</button>
                 </div>
                 <div class="cite-box" id="citation">${escapeHtml(formatCitation(current, citeStyle))}</div>`
              : `<div class="empty">Select an item to inspect it.</div>`
          }
        </section>
      </main>
    </div>
    ${renderModal()}
  `;

  const search = document.getElementById("search") as HTMLInputElement | null;
  search?.addEventListener("input", () => {
    query = search.value;
    render();
    const nextSearch = document.getElementById("search") as HTMLInputElement | null;
    nextSearch?.focus();
    nextSearch?.setSelectionRange(query.length, query.length);
  });

  document.querySelectorAll<HTMLButtonElement>("[data-collection]").forEach((button) => {
    button.addEventListener("click", () => {
      selectedCollection = button.dataset.collection ?? "all";
      selectedKey = null;
      render();
    });
  });
  document.querySelectorAll<HTMLButtonElement>("[data-tag]").forEach((button) => {
    button.addEventListener("click", () => {
      const tag = button.dataset.tag ?? null;
      selectedTag = selectedTag === tag ? null : tag;
      selectedKey = null;
      render();
    });
  });
  document.querySelectorAll<HTMLButtonElement>("[data-sort]").forEach((button) => {
    button.addEventListener("click", () => {
      sortKey = (button.dataset.sort as SortKey) ?? "creator";
      render();
    });
  });
  document.querySelectorAll<HTMLButtonElement>("[data-item]").forEach((button) => {
    button.addEventListener("click", () => {
      selectedKey = button.dataset.item ?? null;
      render();
    });
  });
  document.getElementById("cite-style")?.addEventListener("change", (event) => {
    citeStyle = (event.target as HTMLSelectElement).value as CiteStyle;
    render();
  });
  document.getElementById("copy-cite")?.addEventListener("click", async () => {
    if (!current) return;
    await navigator.clipboard.writeText(formatCitation(current, citeStyle));
    statusMessage = "Citation copied";
    render();
  });
  document.getElementById("export-bibtex")?.addEventListener("click", () => {
    const blob = new Blob([filteredItems().map((item) => formatCitation(item, "bibtex")).join("\n\n")], {
      type: "application/x-bibtex",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "heena-library.bib";
    link.click();
    URL.revokeObjectURL(url);
  });
  document.getElementById("disconnect")?.addEventListener("click", () => {
    connection = null;
    persistConnection(null);
    collections = [];
    items = [];
    render();
  });
  document.getElementById("add-item")?.addEventListener("click", () => {
    showAdd = true;
    render();
  });
  document.getElementById("cancel-add")?.addEventListener("click", () => {
    showAdd = false;
    render();
  });
  document.getElementById("add-form")?.addEventListener("submit", (event) => {
    event.preventDefault();
    const form = event.currentTarget as HTMLFormElement;
    const itemType = fieldValue(form, "itemType") || "journalArticle";
    const venue = fieldValue(form, "venue");
    const item: Item = {
      key: `LOCAL${Date.now().toString(36).toUpperCase()}`,
      itemType,
      title: fieldValue(form, "title") || "[Untitled]",
      creators: [
        {
          creatorType: "author",
          firstName: fieldValue(form, "firstName"),
          lastName: fieldValue(form, "lastName"),
        },
      ],
      date: fieldValue(form, "date"),
      publicationTitle: itemType === "journalArticle" ? venue : undefined,
      conferenceName: itemType === "conferencePaper" ? venue : undefined,
      websiteTitle: itemType === "webpage" ? venue : undefined,
      publisher: itemType === "book" ? venue : undefined,
      abstractNote: fieldValue(form, "abstractNote"),
      tags: ["added"],
      collections: selectedCollection !== "all" && selectedCollection !== "unfiled" ? [selectedCollection] : [],
    };
    items = [item, ...items];
    selectedKey = item.key;
    showAdd = false;
    statusMessage = "Added to demo library";
    render();
  });
}

function render() {
  if (!connection) renderGate();
  else renderLibrary();
}

void (async function boot() {
  if (connection?.source === "demo") {
    collections = structuredClone(DEMO_COLLECTIONS);
    items = structuredClone(DEMO_ITEMS);
    selectedKey = items[0]?.key ?? null;
  } else if (connection?.source === "zotero") {
    try {
      const library = await fetchZoteroLibrary(connection);
      collections = library.collections;
      items = library.items;
      selectedKey = items[0]?.key ?? null;
      statusMessage = `${items.length} items from Zotero`;
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : "Could not reopen Zotero.";
      connection = null;
      persistConnection(null);
    }
  }
  render();
})();
