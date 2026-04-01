/** Match backend apps.efiling.party_display rules for listings / cover pages. */

export function normalizeIsPetitioner(value: unknown): boolean {
  return value === true || value === "true" || value === 1 || value === "1";
}

export function getOrderedPartyNames(
  litigants: unknown,
  isPetitioner: boolean,
): string[] {
  const list = Array.isArray(litigants) ? litigants : [];
  return list
    .filter(
      (l: any) =>
        normalizeIsPetitioner(l?.is_petitioner) ===
        normalizeIsPetitioner(isPetitioner),
    )
    .sort(
      (a: any, b: any) =>
        (Number(a?.sequence_number) || 0) - (Number(b?.sequence_number) || 0),
    )
    .map((l: any) => String(l?.name || "").trim())
    .filter((name) => !!name);
}

export function formatPartyLine(names: string[], fallback = ""): string {
  if (!names.length) return String(fallback || "").trim();
  if (names.length === 1) return names[0];
  if (names.length === 2) return `${names[0]} and Anr.`;
  return `${names[0]} and Ors.`;
}

/**
 * Full "Petitioner vs. Respondent" string from litigants (client-side).
 * Optional fallback when no petitioner litigants (e.g. initial form name).
 */
export function formatPetitionerVsRespondent(
  litigants: unknown,
  fallbackPetitionerName = "",
): string {
  const p = formatPartyLine(getOrderedPartyNames(litigants, true));
  const r = formatPartyLine(getOrderedPartyNames(litigants, false));
  const pFinal = p || String(fallbackPetitionerName || "").trim();
  if (pFinal && r) return `${pFinal} vs. ${r}`;
  if (pFinal) return pFinal;
  if (r) return r;
  return "";
}
