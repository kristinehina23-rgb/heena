export type Creator = {
  creatorType: string;
  firstName?: string;
  lastName?: string;
  name?: string;
};

export type Collection = {
  key: string;
  name: string;
  parentCollection: string | false;
};

export type Item = {
  key: string;
  version?: number;
  itemType: string;
  title: string;
  creators: Creator[];
  date?: string;
  publicationTitle?: string;
  publisher?: string;
  place?: string;
  volume?: string;
  issue?: string;
  pages?: string;
  DOI?: string;
  url?: string;
  abstractNote?: string;
  tags: string[];
  collections: string[];
  extra?: string;
  ISBN?: string;
  ISSN?: string;
  university?: string;
  conferenceName?: string;
  websiteTitle?: string;
  language?: string;
  shortTitle?: string;
};

export type LibrarySource = "demo" | "zotero";

export type Connection = {
  source: LibrarySource;
  userId?: string;
  apiKey?: string;
  libraryType: "user" | "group";
  groupId?: string;
};

export type CiteStyle = "apa" | "mla" | "chicago" | "bibtex";
