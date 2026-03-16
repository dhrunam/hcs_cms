# HCS CMS Project Manager Checklist

## Current Implementation Snapshot (As of 13 Mar 2026)
- Backend foundation is operational with Django 6 + DRF.
- Core migrations are running cleanly after dependency-chain correction.
- Efiling API CRUD endpoints are implemented for `Efiling`, `EfilingLitigant`, `EfilingCaseDetails`, and `EfilingActs`.
- Master API list endpoints are implemented for case types, states, districts, courts, org types, acts, and org names.
- URL and serializer/view test coverage has been expanded for active backend apps.
- External SSO introspection integration is implemented with fallback endpoint support.
- Temporary development mode is enabled to test CRUD APIs without authentication.

Use this checklist below for remaining milestone tracking and closure governance.

## How to Use
- Use this checklist in weekly PM reviews and sprint ceremonies.
- Mark each item as complete when evidence exists (document, demo, report, sign-off).
- Keep links to artifacts beside each checked item.

## A. Governance and Planning
- [ ] Project scope is frozen against SRS baseline.
- [ ] Sprint goals are updated for current sprint.
- [ ] SRS-to-backlog traceability is current.
- [ ] RAID log (Risks, Assumptions, Issues, Dependencies) is updated weekly.
- [ ] Critical path items are identified and tracked.
- [ ] All phase milestone dates are visible on team calendar.
- [ ] Stakeholder communication plan is active.

## B. Team and Delivery Cadence
- [ ] Sprint planning completed with committed scope.
- [ ] Daily standups are happening with blocker escalation.
- [ ] Sprint review/demo scheduled and completed.
- [ ] Sprint retrospective completed with action items.
- [ ] Team capacity and leave plan validated for sprint.
- [ ] Cross-team dependencies are confirmed (SSO, payments, OTP, CIS).

## C. Requirements and Functional Progress
- [ ] 4-step eFiling workflow status is tracked.
- [ ] Scrutiny workflow status is tracked.
- [ ] Registry dashboards for Civil/Criminal/Writ are tracked.
- [ ] Advocate portfolio and Bar ID linkage progress is tracked.
- [ ] Judge dashboard features (multi-view, notes, annotations) are tracked.
- [ ] Digital signature workflow progress is tracked.
- [ ] File tracking integration progress is tracked.
- [ ] AI module rollout status (scrutiny/research/translation/transcription) is tracked.

## D. Security and Compliance (Mandatory)
- [ ] MFA status for judicial and registry users is verified.
- [ ] RBAC matrix is approved and implemented.
- [ ] Tamper-evident audit trail is enabled for key actions.
- [ ] Log retention control for 180 days is validated.
- [ ] Incident response process supports <= 6-hour CERT-In reporting.
- [ ] Vulnerability/dependency scan is run for the sprint.
- [ ] Security exceptions (if any) are documented with approval.

## E. Architecture and Integration
- [ ] Core-periphery architecture assumptions are unchanged.
- [ ] CIS 1.0 inspectdb/table mapping is validated.
- [ ] Data consuming adapter contracts are versioned and approved.
- [ ] EC-prefixed filing number generation path is tested.
- [ ] External integration health checks are in place.
- [ ] SSO integration (resource server token validation) is tested end-to-end.

## F. Data Migration and Data Quality
- [ ] Migration scope (CNR-tagged eligible records) is agreed.
- [ ] Migration plan and rollback plan are approved.
- [ ] Dry run migration report is reviewed.
- [ ] Data deduplication rules for single person view are approved.
- [ ] Post-migration validation checklist is completed.
- [ ] Downtime and fallback procedure (physical filing) is communicated.

## G. Quality Assurance and UAT
- [ ] Definition of Done is applied to all stories.
- [ ] Test plan covers API, UI, integration, and security scenarios.
- [ ] Regression suite is executed each sprint.
- [ ] Performance baseline is measured and tracked.
- [ ] UAT scenarios are prepared with stakeholder sign-off criteria.
- [ ] Defect triage process is active and SLA-based.

## H. DevOps and Environment Readiness
- [ ] Dev, test, and staging environments are stable.
- [ ] Environment variables and secrets are managed securely.
- [ ] Backup and restore process is tested.
- [ ] DR drill schedule is approved.
- [ ] Monitoring and alerting dashboards are active.
- [ ] Release deployment checklist is ready.

## I. Documentation and Change Management
- [ ] API documentation is up to date.
- [ ] User guides/SOP drafts are updated per sprint.
- [ ] Release notes are prepared for each increment.
- [ ] Training plan for registry/judicial staff is active.
- [ ] Change requests are approved and version controlled.

## J. Phase Milestone Gates

### Phase I Gate (Target: 30.04.2026)
- [ ] eFiling pilot is operational.
- [ ] Basic dashboards are operational.
- [ ] CIS filing number generation flow is working.
- [ ] Phase I acceptance sign-off obtained.

### Phase II Gate (Target: 30.09.2026)
- [ ] Registry dashboard v1 is operational.
- [ ] FSO-advocate communication module is live.
- [ ] AI-assisted scrutiny and translation/research beta is available.
- [ ] Phase II hardening and UAT closure sign-off obtained.

### Phase III Gate (Target: 22.12.2026)
- [ ] Roster-based automated listing is operational.
- [ ] Urgent memo auto-listing is operational.
- [ ] Transcription module meets agreed reliability baseline.
- [ ] Performance, DR, and compliance evidence is complete.
- [ ] Final UAT, handover, and closure sign-off obtained.

## K. Weekly PM Snapshot (Fill Every Week)
- Week ending date: [ ]
- Sprint number: [ ]
- Overall status (Green/Amber/Red): [ ]
- Top 3 achievements: [ ]
- Top 3 risks/issues: [ ]
- Decisions needed from steering committee: [ ]
- Planned focus for next week: [ ]

## L. Critical KPI Tracking
- [ ] eFiling success rate >= 98%
- [ ] EC filing number generation success >= 99.5%
- [ ] Scrutiny SLA adherence >= 90%
- [ ] Audit log coverage for tracked actions = 100%
- [ ] UAT stakeholder satisfaction >= 4/5
