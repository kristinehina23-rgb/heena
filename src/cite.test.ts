import { describe, expect, it } from "vitest";
import { formatApa, formatBibtex, formatChicago, formatMla, yearFromDate } from "./cite";
import type { Item } from "./types";

const article: Item = {
  key: "ABCD12",
  itemType: "journalArticle",
  title: "Computing Machinery and Intelligence",
  creators: [{ creatorType: "author", firstName: "A. M.", lastName: "Turing" }],
  date: "October 1950",
  publicationTitle: "Mind",
  volume: "LIX",
  issue: "236",
  pages: "433–460",
  DOI: "10.1093/mind/LIX.236.433",
  tags: ["ai"],
  collections: [],
};

const book: Item = {
  key: "KUHN62",
  itemType: "book",
  title: "The Structure of Scientific Revolutions",
  creators: [{ creatorType: "author", firstName: "Thomas S.", lastName: "Kuhn" }],
  date: "1962",
  publisher: "University of Chicago Press",
  place: "Chicago",
  tags: [],
  collections: [],
};

describe("yearFromDate", () => {
  it("extracts a four-digit year", () => {
    expect(yearFromDate("October 1950")).toBe("1950");
  });

  it("uses n.d. when missing", () => {
    expect(yearFromDate(undefined)).toBe("n.d.");
  });
});

describe("citation formats", () => {
  it("formats APA journal articles with a DOI", () => {
    const citation = formatApa(article);
    expect(citation).toContain("Turing, A.");
    expect(citation).toContain("(1950)");
    expect(citation).toContain("Mind");
    expect(citation).toContain("https://doi.org/10.1093/mind/LIX.236.433");
  });

  it("italicizes book titles in APA", () => {
    expect(formatApa(book)).toContain("*The Structure of Scientific Revolutions*");
    expect(formatApa(book)).toContain("University of Chicago Press");
  });

  it("formats MLA with volume and pages", () => {
    const citation = formatMla(article);
    expect(citation).toContain("Turing, A. M.");
    expect(citation).toContain("vol. LIX");
    expect(citation).toContain("pp. 433–460");
  });

  it("formats Chicago notes-bibliography style", () => {
    const citation = formatChicago(article);
    expect(citation).toContain("Turing, A. M.");
    expect(citation).toContain("(1950)");
    expect(citation).toContain(": 433–460");
  });

  it("emits a BibTeX article entry", () => {
    const bib = formatBibtex(article);
    expect(bib).toMatch(/^@article\{turing1950ABCD,/);
    expect(bib).toContain("author = {Turing, A. M.}");
    expect(bib).toContain("journal = {Mind}");
    expect(bib).toContain("doi = {10.1093/mind/LIX.236.433}");
  });

  it("maps books to @book", () => {
    expect(formatBibtex(book)).toMatch(/^@book\{/);
    expect(formatBibtex(book)).toContain("publisher = {University of Chicago Press}");
  });
});
