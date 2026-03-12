# HCS_CMS - One-Page Gantt Summary (SRS Aligned)

## Project Snapshot
- Court: High Court of Sikkim
- Program: Indigenous Case Management System (Core-Periphery with CIS 1.0)
- Team: 4 Full-Stack Developers
- Duration: 10.03.2026 to 22.12.2026
- Stack baseline: Angular + Django + PostgreSQL

## Phase Timeline (SRS Dates)

| Workstream | Mar-2026 | Apr-2026 | May-Jun 2026 | Jul-Aug 2026 | Sep-2026 | Oct-2026 | Nov-2026 | Dec-2026 |
|---|---|---|---|---|---|---|---|---|
| 1. Core Filing & Foundation (Phase I) | ████ | ████ |  |  |  |  |  |  |
| 2. CIS 1.0 Integration + Migration (Phase I) | ████ | ████ |  |  |  |  |  |  |
| 3. Registry Expansion (Phase II) |  |  | ████ | ████ | ████ |  |  |  |
| 4. Advocate/Judge Dashboard Enhancements (Phase II) |  |  | ████ | ████ | ████ |  |  |  |
| 5. AI Introduction: Scrutiny/Research/Translation (Phase II) |  |  | ████ | ████ | ████ |  |  |  |
| 6. Roster Analysis + Auto Listing (Phase III) |  |  |  |  |  | ████ | ████ |  |
| 7. Transcription AI Stabilization (Phase III) |  |  |  |  |  | ████ | ████ | ████ |
| 8. Final Hardening, UAT, Closure (Phase III) |  |  |  |  |  |  | ████ | ████ |

Legend: `████` = Active execution window

## Milestones
- **M1 (30.04.2026)**: Phase I complete (eFiling, basic dashboards, CIS 1.0 integration baseline)
- **M2 (30.09.2026)**: Phase II complete (registry expansion + initial AI modules)
- **M3 (22.12.2026)**: Phase III complete (optimization + stabilization)

## Critical Dependencies
- CIS 1.0 table mapping via `inspectdb` finalized early in Phase I
- Data migration access from existing eFiling 3.0 portal
- OTP/Aadhaar and ePayment dependency readiness for 4-step filing flow
- CJ roster rule finalization before Phase III listing automation

## Compliance Controls (Must Run Throughout)
- CERT-In log retention: 180 days (India-hosted)
- Cyber incident reporting readiness: <= 6 hours
- Mandatory MFA for judicial and registry accounts
- Tamper-evident audit trail for all case/document actions

## Top Risks
- Legacy data quality inconsistencies during migration
- AI model quality variability in early rollouts
- Delays in external integrations (OTP/payment)
- Adoption curve for paperless registry/judicial workflows
