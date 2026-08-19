import { describe, expect, it } from "vitest";
import { authHeaders, libraryPrefix, mapZoteroCollection, mapZoteroItem, zoteroUrl } from "./api";
import type { Connection } from "./types";

const user: Connection = {
  source: "zotero",
  libraryType: "user",
  userId: "12345",
  apiKey: "secret",
};

describe("libraryPrefix", () => {
  it("builds a user library prefix", () => {
    expect(libraryPrefix(user)).toBe("/users/12345");
  });

  it("builds a group library prefix", () => {
    expect(libraryPrefix({ ...user, libraryType: "group", groupId: "99" })).toBe("/groups/99");
  });

  it("rejects a group library without an id", () => {
    expect(() => libraryPrefix({ ...user, libraryType: "group" })).toThrow(/group ID/i);
  });
});

describe("zoteroUrl", () => {
  it("targets the v3 collections endpoint", () => {
    expect(zoteroUrl(user, "/collections")).toBe(
      "https://api.zotero.org/users/12345/collections?limit=100",
    );
  });

  it("passes extra query parameters", () => {
    expect(zoteroUrl(user, "/items/top", { sort: "title" })).toContain("sort=title");
  });
});

describe("authHeaders", () => {
  it("sends the API version and key headers", () => {
    expect(authHeaders("abc")).toEqual({
      "Zotero-API-Version": "3",
      "Zotero-API-Key": "abc",
    });
  });
});

describe("mapZoteroItem", () => {
  it("maps Zotero JSON into the library item shape", () => {
    const item = mapZoteroItem({
      key: "ABCDE1",
      version: 12,
      data: {
        itemType: "journalArticle",
        title: "A Test Paper",
        creators: [{ creatorType: "author", firstName: "Ada", lastName: "Lovelace" }],
        date: "1843",
        tags: [{ tag: "computing" }],
        collections: ["XYZ"],
        DOI: "10.0/test",
      },
    });
    expect(item).toMatchObject({
      key: "ABCDE1",
      title: "A Test Paper",
      tags: ["computing"],
      collections: ["XYZ"],
      DOI: "10.0/test",
    });
    expect(item?.creators[0]).toEqual({
      creatorType: "author",
      firstName: "Ada",
      lastName: "Lovelace",
      name: undefined,
    });
  });

  it("skips notes and attachments", () => {
    expect(mapZoteroItem({ key: "N1", data: { itemType: "note", title: "secret" } })).toBeNull();
    expect(mapZoteroItem({ key: "A1", data: { itemType: "attachment", title: "pdf" } })).toBeNull();
  });
});

describe("mapZoteroCollection", () => {
  it("maps nested collections", () => {
    expect(
      mapZoteroCollection({
        key: "COL1",
        data: { name: "Language models", parentCollection: "ML" },
      }),
    ).toEqual({
      key: "COL1",
      name: "Language models",
      parentCollection: "ML",
    });
  });
});
