# Sikkim High Court CMS - Phase-wise Project Timeline (SRS Aligned)

## Scope Baseline
- Program target: Sikkim High Court indigenous CMS aligned to Kerala HC CMS model.
- Architecture model: Core-Periphery (CIS 1.0 as core data layer, CMS as web-enabled periphery).
- Stack baseline from SRS: Angular (frontend), Django (backend), PostgreSQL (database).
- Workflow baseline: eFiling -> Scrutiny -> Filing Number in CIS 1.0 -> Registry flow -> Listing -> Courtroom operations -> Disposal.

## Current Progress Update (As of 13 Mar 2026)
- Backend app structure is active with modular APIs under `/api/v1/`.
- Efiling and master data APIs are implemented and testable.
- Accounts API is operational, including `/api/v1/accounts/users/me/`.
- SSO token introspection path has been integrated in backend authentication logic.
- For development testing, API auth/permission checks are temporarily relaxed to accelerate CRUD verification.
- Milestones related to full 4-step eFiling, dashboards, payment/OTP, and advanced workflow modules remain in planned/in-progress state.

## Approved Implementation Phases

### Phase I: Core Filing & Foundation (10.03.2026 - 30.04.2026)
**Objectives**
- Deliver eFiling foundation and initial role dashboards.
- Establish CIS 1.0 integration and migration from existing portal.

**Tasks**
- Build 4-step eFiling flow: metadata entry, searchable PDF upload, ePayment, OTP/Aadhaar authentication.
- Implement basic dashboards for Judge, Advocate/Litigant, and Scrutiny stakeholders.
- Implement digital Vakalath creation and acceptance flow.
- Build filing acknowledgement and scrutiny handoff workflow.
- Integrate Data Consuming layer to push accepted e-filed data into CIS 1.0.
- Implement `EC`-prefixed filing number generation trigger after scrutiny acceptance.
- Use Django `inspectdb` mapping for CIS 1.0 legacy tables without schema alteration.
- Migrate eligible records from existing eFiling 3.0 portal (registered and CNR-tagged cases).
- Set up security controls: MFA for internal users, tamper-evident audit trail, CERT-In log retention baseline.

**Milestones**
- eFiling live for pilot users.
- Basic dashboards operational.
- CIS 1.0 filing number generation running for accepted filings.

### Phase II: Registry Expansion & AI Introduction (02.05.2026 - 30.09.2026)
**Objectives**
- Expand registry operations and strengthen stakeholder dashboards.
- Introduce AI capabilities for assisted operations.

**Tasks**
- Build registry dashboard modules for Writ, Criminal, and Civil sections.
- Add real-time communication channel between Filing Scrutiny Officers and advocates.
- Expand advocate portfolio management by Bar ID with live status and order download.
- Implement partner management (senior-junior-clerk collaboration).
- Build AI-assisted scrutiny checks for high-volume filings (formatting + metadata defects).
- Introduce AI modules for legal research assistance and translation.
- Strengthen data quality layer for single person view (deduplication of litigant/advocate identities).
- Expand compliance reporting for audit and incident traceability.

**Milestones**
- Registry dashboard v1 operational.
- AI-assisted scrutiny and translation/research modules available in controlled rollout.

### Phase III: Optimization & Stabilization (01.10.2026 - 22.12.2026)
**Objectives**
- Optimize listing/roster operations and stabilize advanced AI features.
- Complete production hardening and institutional adoption.

**Tasks**
- Implement roster analysis and advanced automated listing based on CJ-approved roster.
- Deliver Auto-Listing for urgent memos.
- Stabilize courtroom transcription AI modules.
- Improve PS/PA staff views for draft order and cause list support workflows.
- Finalize legacy record file-tracking integrations across registry sections.
- Execute performance tuning, security hardening, DR drills, and final UAT closure.

**Milestones**
- Advanced registry and roster functions complete.
- Transcription AI stabilized for production use.
- Program closure readiness achieved by 22.12.2026.

## Cross-Cutting Compliance Requirements
- CERT-In logging retention: maintain system/application logs within Indian jurisdiction for rolling 180 days.
- Incident reporting: report cybersecurity incidents to CERT-In within 6 hours of discovery.
- Mandatory MFA for judicial and registry accounts.
- Tamper-evident audit trail for every document/case action.

## Team Allocation (4 Developers)
- Dev 1: platform architecture, CIS integration, security/compliance controls.
- Dev 2: eFiling + advocate/litigant dashboard workflows.
- Dev 3: scrutiny + registry workflows + file tracking modules.
- Dev 4: judicial/staff dashboards + listing/roster + AI integration support.

## Key Program Risks
- CIS 1.0 legacy data inconsistencies impacting mapping/migration.
- Delays in external dependencies (OTP, Aadhaar, payment rails).
- AI model quality for scrutiny/transcription in initial rollout.
- Change management for registry process transition from hybrid to paperless flow.
