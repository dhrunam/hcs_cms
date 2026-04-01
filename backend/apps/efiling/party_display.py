"""Format petitioner / respondent lines for listings and cover pages."""


def _party_line_from_litigants(litigants, is_petitioner: bool) -> str:
    side = [l for l in litigants if bool(l.is_petitioner) == is_petitioner]
    side.sort(key=lambda x: (x.sequence_number or 0))
    names = [(getattr(l, "name", None) or "").strip() for l in side]
    names = [n for n in names if n]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and Anr."
    return f"{names[0]} and Ors."


def build_petitioner_vs_respondent(efiling, fallback_petitioner_name: str = "") -> str:
    """
    e.g. "A vs. B" or "A and Anr. vs. B and Ors."
    Uses sequence order within petitioner and respondent groups.
    """
    if efiling is None:
        efiling_litigants = []
    else:
        manager = getattr(efiling, "litigants", None)
        if manager is None:
            efiling_litigants = []
        else:
            efiling_litigants = list(manager.all())

    p = _party_line_from_litigants(efiling_litigants, True)
    r = _party_line_from_litigants(efiling_litigants, False)
    p_final = p or (fallback_petitioner_name or "").strip()
    if p_final and r:
        return f"{p_final} vs. {r}"
    if p_final:
        return p_final
    if r:
        return r
    return ""
