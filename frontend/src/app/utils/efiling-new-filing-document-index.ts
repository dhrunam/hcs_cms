/**
 * Master rows named like "Annexure(s)" are stored for checklists but annexure
 * uploads are driven by the new-filing UI — omit from API-driven index lists.
 */
export function isFrontendManagedAnnexureDocumentIndexName(name: string): boolean {
  const raw = String(name ?? "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ");
  if (!raw) return false;
  const noStar = raw.replace(/\*+$/g, "").trim();
  return /^annexure\s*\(\s*s\s*\)$/.test(noStar);
}
