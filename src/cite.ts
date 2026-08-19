import type { Creator, Item } from "./types";

export function yearFromDate(date?: string): string {
  if (!date) return "n.d.";
  const match = date.match(/\d{4}/);
  return match ? match[0] : "n.d.";
}

export function primaryCreators(item: Item): Creator[] {
  const authors = item.creators.filter((creator) => creator.creatorType === "author");
  return authors.length > 0 ? authors : item.creators;
}

export function lastFirst(creator: Creator): string {
  if (creator.name?.trim()) return creator.name.trim();
  const last = creator.lastName?.trim() ?? "";
  const first = creator.firstName?.trim() ?? "";
  if (last && first) return `${last}, ${first}`;
  return last || first || "Anonymous";
}

export function firstLast(creator: Creator): string {
  if (creator.name?.trim()) return creator.name.trim();
  return [creator.firstName, creator.lastName].filter(Boolean).join(" ").trim() || "Anonymous";
}

export function creatorLastName(creator: Creator): string {
  if (creator.lastName?.trim()) return creator.lastName.trim();
  if (creator.name?.trim()) {
    const parts = creator.name.trim().split(/\s+/);
    return parts[parts.length - 1] ?? creator.name;
  }
  return creator.firstName?.trim() || "Anonymous";
}

function joinAuthors(
  creators: Creator[],
  format: (creator: Creator, index: number, total: number) => string,
  lastJoin: string,
): string {
  if (creators.length === 0) return "Anonymous";
  if (creators.length === 1) return format(creators[0], 0, 1);
  if (creators.length === 2) {
    return `${format(creators[0], 0, 2)} ${lastJoin} ${format(creators[1], 1, 2)}`;
  }
  const head = creators
    .slice(0, -1)
    .map((creator, index) => format(creator, index, creators.length))
    .join(", ");
  const tail = format(creators[creators.length - 1], creators.length - 1, creators.length);
  return `${head}, ${lastJoin} ${tail}`;
}

function sentenceCaseTitle(title: string): string {
  const trimmed = title.trim();
  if (!trimmed) return "[Untitled]";
  return trimmed.replace(/\.$/, "");
}

function quotedTitle(title: string): string {
  const trimmed = title.trim() || "[Untitled]";
  return `“${trimmed.replace(/\.$/, "")}.”`;
}

function italic(text: string): string {
  return `*${text}*`;
}

function apaName(creator: Creator): string {
  if (creator.name) return creator.name;
  const last = creator.lastName ?? "Anonymous";
  const initials = (creator.firstName ?? "")
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => `${part[0]}.`)
    .join(" ");
  return initials ? `${last}, ${initials}` : last;
}

export function formatApa(item: Item): string {
  const authors = joinAuthors(primaryCreators(item), (creator) => apaName(creator), "&");
  const year = yearFromDate(item.date);
  const title = sentenceCaseTitle(item.title);
  const container = item.publicationTitle || item.websiteTitle || item.conferenceName;
  const parts = [`${authors} (${year}). ${title}.`];

  if (item.itemType === "book" || item.itemType === "thesis") {
    const pub = [item.publisher, item.university].filter(Boolean).join(". ");
    if (pub) parts[0] = `${authors} (${year}). ${italic(title)}. ${pub}.`;
    else parts[0] = `${authors} (${year}). ${italic(title)}.`;
  } else if (container) {
    let loc = italic(container);
    if (item.volume) loc += `, ${item.volume}`;
    if (item.issue) loc += `(${item.issue})`;
    if (item.pages) loc += `, ${item.pages}`;
    parts.push(`${loc}.`);
  }

  if (item.DOI) parts.push(`https://doi.org/${item.DOI.replace(/^https?:\/\/doi.org\//i, "")}`);
  else if (item.url) parts.push(item.url);

  return parts.filter(Boolean).join(" ").replace(/\s+/g, " ").trim();
}

export function formatMla(item: Item): string {
  const authors = joinAuthors(primaryCreators(item), (creator, index) => {
    return index === 0 ? lastFirst(creator) : firstLast(creator);
  }, "and");
  const title = quotedTitle(item.title);
  const container = item.publicationTitle || item.websiteTitle || item.conferenceName || item.publisher;
  const chunks = [authors.endsWith(".") ? authors : `${authors}.`, title];
  if (container) chunks.push(`${italic(container)},`);
  if (item.volume) chunks.push(`vol. ${item.volume},`);
  if (item.issue) chunks.push(`no. ${item.issue},`);
  chunks.push(`${yearFromDate(item.date)}.`);
  if (item.pages) chunks.push(`pp. ${item.pages}.`);
  if (item.DOI) chunks.push(`https://doi.org/${item.DOI.replace(/^https?:\/\/doi.org\//i, "")}.`);
  return chunks.join(" ").replace(/\s+,/g, ",").replace(/\s+\./g, ".").replace(/\s+/g, " ").trim();
}

export function formatChicago(item: Item): string {
  const authors = joinAuthors(primaryCreators(item), (creator, index) => {
    return index === 0 ? lastFirst(creator) : firstLast(creator);
  }, "and");
  const title = quotedTitle(item.title);
  const container = item.publicationTitle || item.websiteTitle || item.conferenceName;
  const year = yearFromDate(item.date);
  const parts = [`${authors}.`, title];
  if (item.itemType === "book") {
    parts[1] = `${italic(sentenceCaseTitle(item.title))}.`;
    if (item.place) parts.push(`${item.place}:`);
    if (item.publisher) parts.push(`${item.publisher},`);
    parts.push(`${year}.`);
  } else if (container) {
    parts.push(`${italic(container)}`);
    if (item.volume) parts.push(`${item.volume},`);
    if (item.issue) parts.push(`no. ${item.issue}`);
    parts.push(`(${year})`);
    if (item.pages) parts.push(`: ${item.pages}.`);
    else parts.push(".");
  } else {
    parts.push(`${year}.`);
  }
  if (item.DOI) parts.push(`https://doi.org/${item.DOI.replace(/^https?:\/\/doi.org\//i, "")}.`);
  return parts.join(" ").replace(/\s+,/g, ",").replace(/\s+\./g, ".").replace(/\s+/g, " ").trim();
}

function bibtexType(itemType: string): string {
  switch (itemType) {
    case "book":
      return "book";
    case "bookSection":
      return "incollection";
    case "conferencePaper":
      return "inproceedings";
    case "thesis":
      return "phdthesis";
    case "webpage":
      return "misc";
    case "preprint":
      return "unpublished";
    default:
      return "article";
  }
}

function bibtexKey(item: Item): string {
  const author = primaryCreators(item)[0];
  const last = author ? creatorLastName(author).replace(/[^A-Za-z]/g, "") : "anon";
  return `${last.toLowerCase()}${yearFromDate(item.date)}${item.key.slice(0, 4)}`;
}

function bibEscape(value: string): string {
  return value.replace(/[{}\\]/g, "\\$&");
}

export function formatBibtex(item: Item): string {
  const fields: Array<[string, string | undefined]> = [
    ["title", item.title],
    [
      "author",
      primaryCreators(item)
        .map((creator) =>
          creator.name ? creator.name : `${creator.lastName ?? ""}, ${creator.firstName ?? ""}`.replace(/, $/, ""),
        )
        .join(" and "),
    ],
    ["year", yearFromDate(item.date) === "n.d." ? undefined : yearFromDate(item.date)],
    ["journal", item.publicationTitle],
    ["booktitle", item.conferenceName],
    ["publisher", item.publisher],
    ["address", item.place],
    ["volume", item.volume],
    ["number", item.issue],
    ["pages", item.pages],
    ["doi", item.DOI],
    ["url", item.url],
    ["isbn", item.ISBN],
    ["issn", item.ISSN],
    ["school", item.university],
  ];
  const body = fields
    .filter(([, value]) => Boolean(value?.trim()))
    .map(([key, value]) => `  ${key} = {${bibEscape(value!.trim())}}`)
    .join(",\n");
  return `@${bibtexType(item.itemType)}{${bibtexKey(item)},\n${body}\n}`;
}

export function formatCitation(item: Item, style: "apa" | "mla" | "chicago" | "bibtex"): string {
  switch (style) {
    case "mla":
      return formatMla(item);
    case "chicago":
      return formatChicago(item);
    case "bibtex":
      return formatBibtex(item);
    default:
      return formatApa(item);
  }
}

export function creatorSortName(item: Item): string {
  const creator = primaryCreators(item)[0];
  return creator ? creatorLastName(creator).toLowerCase() : "";
}

export function itemTypeLabel(itemType: string): string {
  const labels: Record<string, string> = {
    journalArticle: "Journal article",
    book: "Book",
    bookSection: "Book section",
    conferencePaper: "Conference paper",
    thesis: "Thesis",
    webpage: "Web page",
    preprint: "Preprint",
    report: "Report",
    newspaperArticle: "Newspaper",
    magazineArticle: "Magazine",
  };
  return labels[itemType] ?? itemType;
}
