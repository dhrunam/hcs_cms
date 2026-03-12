# HCS_CMS - Technology Stack Decision (SRS Aligned)

## Decision Context
- Reference source: `SRS for CMS.pdf`
- Court context: High Court of Sikkim
- Delivery model: Core-Periphery architecture over legacy CIS 1.0
- Immediate requirement: Stable government-grade workflow platform with compliance controls

## Final Direction for Current Program

### Approved Baseline (Use Now)
- Frontend: **Angular (SPA)**
- Backend: **Django (Python)**
- Database: **PostgreSQL**

This is the stack explicitly specified in the SRS and should be treated as the program baseline for Phase I to Phase III.

## Why This Is the Right Choice for Now
- SRS alignment: avoids scope drift and re-approval cycles.
- Governance fit: Django provides mature auth, admin workflows, and audit integration patterns.
- Legacy compatibility: easier controlled integration layer on top of CIS 1.0 tables.
- Team efficiency: predictable delivery for filing/scrutiny/registry-heavy workflows.
- Compliance posture: straightforward implementation of MFA, audit trails, and CERT-In logging requirements.

## FastAPI Consideration

### Should FastAPI replace Django now?
- **No**, not for the current SRS-governed rollout.

### Where FastAPI can still be useful later
- Async-heavy subsystems introduced as side services in later phases, such as:
  - transcription AI pipelines
  - high-volume document/OCR processing
  - real-time event streaming modules

### Recommended approach
- Keep Django as system-of-record workflow backend.
- Introduce FastAPI only as bounded microservices where async throughput is required.

## Angular vs Next.js (Program-Specific View)
- SRS explicitly anchors frontend on Angular.
- Angular supports enterprise module boundaries and role-based dashboard structure needed for judiciary workflows.
- Keeping Angular avoids rework in architecture documentation and stakeholder expectation management.

## Implementation Guidance by Layer
- UI Layer: Angular app with role-based modules (Judge, PS/PA, Advocate, FSO, Registry)
- API Layer: Django-based workflow APIs and integration adapters
- Data Layer: PostgreSQL for CMS + mapped access to CIS 1.0 structures
- Security Layer: MFA, RBAC, tamper-evident audit logs, log retention controls
- Integration Layer: Data consuming modules for CIS sync + external OTP/payment adapters

## Phase-Wise Technical Focus
- Phase I: eFiling core, CIS mapping (`inspectdb`), basic dashboards, migration start
- Phase II: registry expansion, AI-assisted scrutiny/research/translation
- Phase III: roster automation, urgent memo auto-listing, transcription stabilization

## Bottom Line
Use **Angular + Django + PostgreSQL** as the primary stack for the current CMS program. Introduce **FastAPI selectively** only for isolated async services after core SRS deliverables are stable.
