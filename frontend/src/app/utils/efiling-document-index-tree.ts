/**
 * Shared document-index grouping for advocate scrutiny + scrutiny-officer case details.
 * Types come from EfilingDocumentsIndex (list API): document_type on each row, optional parent FK.
 */

export type EfilingDocumentIndexRow = { document: any; depth: number };

export type EfilingDocumentIndexGroup = {
  document_type: string;
  rows: EfilingDocumentIndexRow[];
};

/** FK from API: `parent_document_index` and/or `parent_document_index_id`. */
export function getParentDocumentIndexId(doc: any): number | null {
  const raw = doc?.parent_document_index ?? doc?.parent_document_index_id;
  if (raw == null || raw === "") return null;
  if (typeof raw === "number" && !Number.isNaN(raw)) return raw;
  if (typeof raw === "object" && raw.id != null) return Number(raw.id);
  const n = Number(raw);
  return Number.isNaN(n) ? null : n;
}

function hasNonEmptyFilePartPath(doc: any): boolean {
  const v = doc?.file_part_path;
  if (v == null) return false;
  return String(v).trim().length > 0;
}

/** Rows with a non-empty `file_part_path` open the preview; empty/null path stays non-interactive. */
export function isEfilingDocumentIndexClickable(doc: any): boolean {
  return hasNonEmptyFilePartPath(doc);
}

type TreeNode = { document: any; children: TreeNode[] };

function nestDocumentIndexesInOrder(flat: any[]): TreeNode[] {
  if (!flat?.length) return [];

  const byId = new Map<number, any>();
  for (const d of flat) {
    if (d?.id != null) byId.set(Number(d.id), d);
  }
  const orderIndex = new Map<number, number>();
  flat.forEach((d, i) => {
    if (d?.id != null) orderIndex.set(Number(d.id), i);
  });

  const childMap = new Map<number, any[]>();
  for (const d of flat) {
    const pid = getParentDocumentIndexId(d);
    const idNum = d?.id != null ? Number(d.id) : NaN;
    if (pid != null && byId.has(pid) && idNum !== pid) {
      let list = childMap.get(pid);
      if (!list) {
        list = [];
        childMap.set(pid, list);
      }
      list.push(d);
    }
  }

  const roots: any[] = [];
  for (const d of flat) {
    const pid = getParentDocumentIndexId(d);
    const idNum = d?.id != null ? Number(d.id) : NaN;
    if (pid == null || !byId.has(pid) || idNum === pid) {
      roots.push(d);
    }
  }

  for (const [, kids] of childMap) {
    kids.sort(
      (a, b) =>
        (orderIndex.get(Number(a.id)) ?? 0) - (orderIndex.get(Number(b.id)) ?? 0),
    );
  }

  const buildTree = (doc: any): TreeNode => ({
    document: doc,
    children: (childMap.get(Number(doc.id)) ?? []).map(buildTree),
  });

  return roots.map(buildTree);
}

function flattenIndexTreeWithDepth(
  nodes: TreeNode[],
  depth = 0,
): EfilingDocumentIndexRow[] {
  const out: EfilingDocumentIndexRow[] = [];
  for (const n of nodes) {
    if (n?.document) out.push({ document: n.document, depth });
    out.push(...flattenIndexTreeWithDepth(n.children ?? [], depth + 1));
  }
  return out;
}

/**
 * One group per main document type (EfilingDocuments.document_type).
 * Rows are preorder tree: parent headers (no parent FK) then children under parent_document_index.
 */
export function groupEfilingDocumentIndexesByType(
  docs: any[],
): EfilingDocumentIndexGroup[] {
  if (!Array.isArray(docs) || docs.length === 0) return [];

  const map = new Map<string, any[]>();
  for (const doc of docs) {
    const type = String(doc?.document_type ?? "").trim() || "Main Document";
    const bucket = map.get(type);
    if (bucket) bucket.push(doc);
    else map.set(type, [doc]);
  }

  return Array.from(map.entries()).map(([document_type, items]) => ({
    document_type,
    rows: flattenIndexTreeWithDepth(nestDocumentIndexesInOrder(items)),
  }));
}

export function firstClickableEfilingDocumentIndexInList(
  docs: any[],
): any | null {
  if (!Array.isArray(docs)) return null;
  return docs.find((d) => isEfilingDocumentIndexClickable(d)) ?? null;
}

export function firstClickableEfilingDocumentIndexInGrouped(
  grouped: EfilingDocumentIndexGroup[],
): any | null {
  for (const g of grouped) {
    for (const row of g.rows) {
      if (isEfilingDocumentIndexClickable(row.document)) return row.document;
    }
  }
  return null;
}

export function trackByEfilingDocumentIndexRowId(
  _: number,
  row: EfilingDocumentIndexRow,
): number {
  return row.document?.id ?? _;
}
