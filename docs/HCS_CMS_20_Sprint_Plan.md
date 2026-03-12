# HCS_CMS - 20 Sprint Execution Plan (SRS Aligned)

## Plan Basis
- Source: `SRS for CMS.pdf` (Sikkim High Court CMS)
- Timeline: 10.03.2026 to 22.12.2026
- Team: 4 full-stack developers
- Core architecture model: Core-Periphery (CIS 1.0 core + indigenous CMS periphery)
- Stack baseline: Angular + Django + PostgreSQL

## Phase and Sprint Mapping

### Phase I: Core Filing & Foundation (10.03.2026 - 30.04.2026)
- Sprint 1: SRS traceability, workflow mapping, scope freeze
- Sprint 2: CIS 1.0 schema mapping (`inspectdb`) + data consuming interface design
- Sprint 3: Angular-Django foundation, RBAC, MFA, audit log setup
- Sprint 4: 4-step eFiling + basic judge/advocate/scrutiny dashboards + Phase I acceptance

### Phase II: Registry & AI Introduction (02.05.2026 - 30.09.2026)
- Sprint 5: Registry dashboard baseline and role flows
- Sprint 6: Civil/Criminal/Writ section workflow modules
- Sprint 7: Advocate portfolio management by Bar ID + order/status access
- Sprint 8: FSO-Advocate communication module
- Sprint 9: AI-assisted scrutiny for formatting/metadata defects
- Sprint 10: Digital Vakalath and My Partners collaboration
- Sprint 11: Legacy physical file tracking system integration
- Sprint 12: AI research + translation module (initial)
- Sprint 13: Judge digital tools (notepad/highlight/annotation)
- Sprint 14: Digital signature pipeline for interim/final orders
- Sprint 15: Registry hardening, UAT cycle, and Phase II sign-off

### Phase III: Optimization & Stabilization (01.10.2026 - 22.12.2026)
- Sprint 16: Roster analysis and automated listing engine (CJ roster driven)
- Sprint 17: Urgent memo auto-listing and priority routing
- Sprint 18: Courtroom transcription AI stabilization
- Sprint 19: Performance, DR, and CERT-In compliance readiness
- Sprint 20: Final UAT, stakeholder handover, and closure readiness

## Sprint-Wise Deliverables and Acceptance Focus

### Sprint 1
**Deliverables**
- SRS requirement matrix, role matrix, as-is/to-be workflows
**Acceptance**
- All SRS major requirements mapped to planned sprints

### Sprint 2
**Deliverables**
- CIS 1.0 table mapping, adapter contracts, EC filing numbering rule spec
**Acceptance**
- Legacy schema mapped without modifying CIS core schema

### Sprint 3
**Deliverables**
- Base app shell, authentication, MFA, tamper-evident audit trail
**Acceptance**
- Judicial and registry users can log in via MFA with role-scoped access

### Sprint 4
**Deliverables**
- 4-step eFiling, scrutiny handoff, basic stakeholder dashboards
**Acceptance**
- Accepted scrutiny triggers EC-prefixed filing number generation in CIS 1.0

### Sprint 5
**Deliverables**
- Registry dashboard v1
**Acceptance**
- Registry roles can process and monitor assigned queues

### Sprint 6
**Deliverables**
- Civil/Criminal/Writ section flows
**Acceptance**
- Section-wise routing and status tracking functional

### Sprint 7
**Deliverables**
- Bar ID linked case portfolio with real-time status and order downloads
**Acceptance**
- Advocate can search and track all linked matters by Bar ID

### Sprint 8
**Deliverables**
- In-app chat/communication between FSO and advocates
**Acceptance**
- Defect clarifications are captured with timestamped audit trail

### Sprint 9
**Deliverables**
- AI-based defect recommendation for high-volume filings
**Acceptance**
- AI suggestions shown to scrutiny officer with manual override

### Sprint 10
**Deliverables**
- Digital Vakalath lifecycle + partner collaboration feature
**Acceptance**
- Senior advocate can add juniors/clerks and control access

### Sprint 11
**Deliverables**
- File tracking for legacy physical records
**Acceptance**
- Record location movement traceable by section

### Sprint 12
**Deliverables**
- AI research and translation module (beta)
**Acceptance**
- Controlled pilot users can invoke translation/research from dashboard

### Sprint 13
**Deliverables**
- Judge annotation tools (private notes, highlight, split/flip views)
**Acceptance**
- Judicial users can annotate digital records in-session

### Sprint 14
**Deliverables**
- Digital signature support for orders/judgments
**Acceptance**
- Signed orders become available on advocate dashboard

### Sprint 15
**Deliverables**
- Phase II stabilization fixes, registry UAT closure
**Acceptance**
- Phase II functionality accepted by nominated stakeholders

### Sprint 16
**Deliverables**
- Automated listing based on roster rules
**Acceptance**
- Cause list generation follows configured CJ roster logic

### Sprint 17
**Deliverables**
- Urgent memo auto-listing logic
**Acceptance**
- Urgent matters receive priority listing path with audit trail

### Sprint 18
**Deliverables**
- Courtroom transcription AI stabilization
**Acceptance**
- Transcription module meets baseline accuracy and reliability targets

### Sprint 19
**Deliverables**
- Load/performance reports, DR drill, CERT-In controls checklist
**Acceptance**
- 180-day logs and 6-hour incident reporting SOP validated

### Sprint 20
**Deliverables**
- Final UAT closure, handover pack, closure report
**Acceptance**
- Program is ready for post-Phase III operations by 22.12.2026

## Cross-Sprint Mandatory Tracks
- Security and dependency updates
- Audit trail completeness checks
- Data quality and identity deduplication
- SRS traceability updates
- User SOP and training documentation

## Team Split
- Dev 1: architecture, CIS integration, security/compliance
- Dev 2: eFiling + advocate/litigant experience
- Dev 3: scrutiny + registry + file tracking modules
- Dev 4: judicial dashboards + listing/roster + AI integrations

## Program KPIs
- eFiling success rate >= 98%
- EC filing number generation success >= 99.5%
- Scrutiny turnaround SLA adherence >= 90%
- Audit log coverage for tracked actions = 100%
- UAT stakeholder satisfaction >= 4/5
