# Courtroom reader–judge–listing flow — schema and logic

## Tables modified

| Table | Change |
|-------|--------|
| `courtroom_judge_decision` | **Added** nullable column `bench_role_group` (`varchar(32)`, indexed). Stores canonical role satisfied by the row: `JUDGE_CJ`, `JUDGE_J1`, or `JUDGE_J2`. Populated on each new decision and backfilled for existing rows where possible. |

## Tables created

None.

## Tables deleted

None.

## Related tables (unchanged shape)

- **`courtroom_forward`**: Reader forward (`efiling_id`, `forwarded_for_date`, `bench_key`, `listing_summary`).
- **`courtroom_forward_document`**: Hearing-pack document index ids per forward.
- **`reader_judge_assignment`**: Maps each `JudgeT` to a reader user.

## Logic consolidation

- **Removed** dead helper `_judge_approved_efiling_ids` from listing (never referenced).
- **Single helper** [`efiling_ids_with_all_required_approvals`](backend/apps/judge/courtroom_approval.py) replaces duplicated `judge_user__groups__name` loops in reader approved-cases and judge approved-lookup.
- **Role resolution** for new decisions: [`resolve_bench_role_group_for_forward`](backend/apps/judge/bench_role.py).
- **Cause list day** [`_cause_list_target_efiling_ids`](backend/apps/listing/views.py): union of forwards for that calendar date and cases with `listing_date` on that date (same bench), used for preview, PDF preview, and publish validation.

## Migration

- `judge.0003_courtroom_judge_decision_bench_role_group`: add field + data backfill.
