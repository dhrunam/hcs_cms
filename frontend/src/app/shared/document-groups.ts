export interface DocumentGroupSection {
  key: string;
  label: string;
  sequence: number | null;
  items: any[];
}

export type DocumentDisplaySection =
  | { kind: "doc"; doc: any }
  | { kind: "vakalatGroup"; id: string; label: string; items: any[] };

function asNumber(value: any): number | null {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function isAccessVakalatnama(doc: any): boolean {
  const part = String(doc?.document_part_name ?? "").toLowerCase();
  return part.startsWith("vakalatnama - ");
}

function isVakalatnamaDoc(doc: any): boolean {
  const type = String(doc?.document_type ?? "").toLowerCase();
  const part = String(doc?.document_part_name ?? "").toLowerCase();
  return type.includes("vakalat") || part.includes("vakalat");
}

function groupLabel(doc: any): string {
  if (isVakalatnamaDoc(doc)) return "Vakalatnama";
  return String(doc?.document_type || doc?.document_part_name || "Documents");
}

function docMatchesQuery(doc: any, q: string): boolean {
  if (!q) return true;
  const name = String(doc?.document_part_name ?? "").toLowerCase();
  const type = String(doc?.document_type ?? "").toLowerCase();
  return name.includes(q) || type.includes(q);
}

export function groupDocumentsForDisplay(
  docs: any[],
  query: string = "",
): DocumentGroupSection[] {
  const list = Array.isArray(docs) ? docs : [];
  const q = query.trim().toLowerCase();
  const sections = new Map<string, DocumentGroupSection>();

  for (const doc of list) {
    if (!docMatchesQuery(doc, q)) continue;
    const sequence = asNumber(doc?.document_sequence);
    const label = groupLabel(doc);
    const key = `${sequence ?? "na"}::${label.toLowerCase()}`;
    const existing = sections.get(key);
    if (existing) {
      existing.items.push(doc);
      continue;
    }
    sections.set(key, { key, label, sequence, items: [doc] });
  }

  const out = Array.from(sections.values());
  for (const section of out) {
    section.items.sort((a: any, b: any) => {
      const aAccess = isAccessVakalatnama(a);
      const bAccess = isAccessVakalatnama(b);
      if (aAccess !== bAccess) return aAccess ? 1 : -1;
      return Number(a?.id || 0) - Number(b?.id || 0);
    });
  }

  out.sort((a, b) => {
    if (a.sequence === null && b.sequence === null) return a.label.localeCompare(b.label);
    if (a.sequence === null) return 1;
    if (b.sequence === null) return -1;
    if (a.sequence !== b.sequence) return a.sequence - b.sequence;
    return a.label.localeCompare(b.label);
  });
  return out;
}

export function orderDocumentsForDisplay(docs: any[], query: string = ""): any[] {
  const list = Array.isArray(docs) ? docs : [];
  const q = query.trim().toLowerCase();
  const filtered = list.filter((doc) => docMatchesQuery(doc, q));
  const ordered = [...filtered].sort((a: any, b: any) => {
    const aSeq = asNumber(a?.document_sequence);
    const bSeq = asNumber(b?.document_sequence);
    if (aSeq === null && bSeq === null) {
      const aAccess = isAccessVakalatnama(a);
      const bAccess = isAccessVakalatnama(b);
      if (aAccess !== bAccess) return aAccess ? 1 : -1;
      return Number(a?.id || 0) - Number(b?.id || 0);
    }
    if (aSeq === null) return 1;
    if (bSeq === null) return -1;
    if (aSeq !== bSeq) return aSeq - bSeq;
    const aAccess = isAccessVakalatnama(a);
    const bAccess = isAccessVakalatnama(b);
    if (aAccess !== bAccess) return aAccess ? 1 : -1;
    return Number(a?.id || 0) - Number(b?.id || 0);
  });

  const seqCounts = new Map<number, number>();
  return ordered.map((doc: any, idx: number) => {
    const seq = asNumber(doc?.document_sequence);
    if (seq === null) {
      return { ...doc, display_index_label: String(idx + 1) };
    }
    const seen = seqCounts.get(seq) || 0;
    seqCounts.set(seq, seen + 1);
    const label = seen === 0 ? `${seq}` : `${seq} (${seen})`;
    return { ...doc, display_index_label: label };
  });
}

export function buildCollapsedDisplaySections(docs: any[]): DocumentDisplaySection[] {
  const sections: DocumentDisplaySection[] = [];
  let currentVakalatItems: any[] = [];

  const flushVakalat = () => {
    if (!currentVakalatItems.length) return;
    const first = currentVakalatItems[0];
    sections.push({
      kind: "vakalatGroup",
      id: `vakalat-${String(first?.id || first?.document_sequence || "group")}`,
      label: `Vakalatnamas (${currentVakalatItems.length})`,
      items: currentVakalatItems,
    });
    currentVakalatItems = [];
  };

  for (const doc of Array.isArray(docs) ? docs : []) {
    if (isVakalatnamaDoc(doc)) {
      currentVakalatItems.push(doc);
      continue;
    }
    flushVakalat();
    sections.push({ kind: "doc", doc });
  }
  flushVakalat();
  return sections;
}
