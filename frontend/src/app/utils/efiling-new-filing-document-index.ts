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
 * uploads and fallback lists used in WP(C) Main Petition validation.
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
 * Required Main Petition index labels (excluding annexure master rows).
 * Prefer API-driven names when present so validation matches the upload UI.
 */
export function getWpMainPetitionRequiredIndexNames(
  fetchedFromApi: { name: string }[],
  fallbackWpMandatory: string[],
): string[] {
  if (fetchedFromApi.length > 0) {
    return fetchedFromApi
      .map((x) => String(x.name ?? "").trim())
      .filter(Boolean)
      .filter((n) => !isFrontendManagedAnnexureDocumentIndexName(n));
  }
  return fallbackWpMandatory.filter(
    (name) => !isFrontendManagedAnnexureDocumentIndexName(name),
  );
}
