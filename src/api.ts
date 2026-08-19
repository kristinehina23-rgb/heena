import type { Collection, Connection, Item } from "./types";

const API_ROOT = "https://api.zotero.org";

export function libraryPrefix(connection: Connection): string {
  if (connection.libraryType === "group") {
    if (!connection.groupId?.trim()) {
      throw new Error("Group library requires a group ID.");
    }
    return `/groups/${encodeURIComponent(connection.groupId.trim())}`;
  }
  if (!connection.userId?.trim()) {
    throw new Error("User library requires a Zotero user ID.");
  }
  return `/users/${encodeURIComponent(connection.userId.trim())}`;
}

export function zoteroUrl(connection: Connection, path: string, params: Record<string, string> = {}): string {
  const search = new URLSearchParams({ limit: "100", ...params });
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${API_ROOT}${libraryPrefix(connection)}${suffix}?${search.toString()}`;
}

export function authHeaders(apiKey?: string): HeadersInit {
  const headers: Record<string, string> = {
    "Zotero-API-Version": "3",
  };
  if (apiKey?.trim()) {
    headers["Zotero-API-Key"] = apiKey.trim();
  }
  return headers;
}

type ZoteroTag = { tag?: string } | string;

export type ZoteroItemPayload = {
  key?: string;
  version?: number;
  data?: Record<string, unknown>;
};

export type ZoteroCollectionPayload = {
  key?: string;
  data?: {
    name?: string;
    parentCollection?: string | boolean;
  };
};

function asString(value: unknown): string | undefined {
  return typeof value === "string" && value.trim() ? value : undefined;
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((entry): entry is string => typeof entry === "string") : [];
}

export function mapZoteroItem(payload: ZoteroItemPayload): Item | null {
  const data = payload.data ?? {};
  const itemType = asString(data.itemType);
  if (!itemType || itemType === "attachment" || itemType === "note") return null;
  const key = asString(payload.key) ?? asString(data.key);
  if (!key) return null;

  const rawCreators = Array.isArray(data.creators) ? data.creators : [];
  const creators = rawCreators
    .map((entry) => {
      if (!entry || typeof entry !== "object") return null;
      const creator = entry as Record<string, unknown>;
      return {
        creatorType: asString(creator.creatorType) ?? "author",
        firstName: asString(creator.firstName),
        lastName: asString(creator.lastName),
        name: asString(creator.name),
      };
    })
    .filter((creator): creator is NonNullable<typeof creator> => creator !== null);

  const rawTags = Array.isArray(data.tags) ? (data.tags as ZoteroTag[]) : [];
  const tags = rawTags
    .map((tag) => (typeof tag === "string" ? tag : asString(tag?.tag)))
    .filter((tag): tag is string => Boolean(tag));

  return {
    key,
    version: typeof payload.version === "number" ? payload.version : undefined,
    itemType,
    title: asString(data.title) ?? "[Untitled]",
    creators,
    date: asString(data.date),
    publicationTitle: asString(data.publicationTitle),
    publisher: asString(data.publisher),
    place: asString(data.place),
    volume: asString(data.volume),
    issue: asString(data.issue),
    pages: asString(data.pages),
    DOI: asString(data.DOI),
    url: asString(data.url),
    abstractNote: asString(data.abstractNote),
    tags,
    collections: asStringArray(data.collections),
    extra: asString(data.extra),
    ISBN: asString(data.ISBN),
    ISSN: asString(data.ISSN),
    university: asString(data.university),
    conferenceName: asString(data.conferenceName),
    websiteTitle: asString(data.websiteTitle),
    language: asString(data.language),
    shortTitle: asString(data.shortTitle),
  };
}

export function mapZoteroCollection(payload: ZoteroCollectionPayload): Collection | null {
  const key = asString(payload.key);
  const name = asString(payload.data?.name);
  if (!key || !name) return null;
  const parent = payload.data?.parentCollection;
  return {
    key,
    name,
    parentCollection: typeof parent === "string" && parent ? parent : false,
  };
}

async function fetchJson(url: string, headers: HeadersInit): Promise<unknown> {
  const response = await fetch(url, { headers });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Zotero API ${response.status}: ${detail.slice(0, 180) || response.statusText}`);
  }
  return response.json();
}

export async function fetchZoteroLibrary(connection: Connection): Promise<{
  collections: Collection[];
  items: Item[];
}> {
  const headers = authHeaders(connection.apiKey);
  const [collectionJson, itemJson] = await Promise.all([
    fetchJson(zoteroUrl(connection, "/collections"), headers),
    fetchJson(zoteroUrl(connection, "/items/top", { sort: "dateModified", direction: "desc" }), headers),
  ]);

  const collections = Array.isArray(collectionJson)
    ? collectionJson.map((row) => mapZoteroCollection(row as ZoteroCollectionPayload)).filter((row): row is Collection => row !== null)
    : [];
  const items = Array.isArray(itemJson)
    ? itemJson.map((row) => mapZoteroItem(row as ZoteroItemPayload)).filter((row): row is Item => row !== null)
    : [];

  return { collections, items };
}
