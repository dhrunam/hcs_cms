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

/**
 * Normalize index labels so API names (e.g. "Affidavit(s)", "Vakalatnama *") match
 * uploads and API-driven lists used in WP(C) Main Petition validation.
 */
export function normalizeDocumentIndexNameForMatch(name: string): string {
  let t = String(name ?? "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ")
    .replace(/\*+$/g, "")
    .replace(/\(s\)/gi, "")
    .trim();
  return t;
}

/** Child rows created by structured upload, e.g. "Annexure P1". */
export function isUploadedAnnexurePartName(name: string): boolean {
  return /^annexure\s+[arp]\s*\d+$/i.test(
    String(name ?? "").replace(/\s+/g, " ").trim(),
  );
}

/**
 * Required Main Petition index labels from the document-index API
 * (excluding annexure master rows). Empty when there is no per-case-type config.
 */
export function getWpMainPetitionRequiredIndexNames(
  fetchedFromApi: { name: string }[],
): string[] {
  return fetchedFromApi
    .map((x) => String(x.name ?? "").trim())
    .filter(Boolean)
    .filter((n) => !isFrontendManagedAnnexureDocumentIndexName(n));
}
