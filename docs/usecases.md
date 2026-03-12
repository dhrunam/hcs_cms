# HCS CMS Use Cases

## Scope and Sources
This document consolidates use cases from the following project documents:
- docs/SRS_for_CMS_extracted.txt
- docs/HCS_CMS_20_Sprint_Plan.md
- docs/HCS_CMS_Project_Timeline.md
- docs/HCS_CMS_Gantt_One_Page_Summary.md
- docs/HCS_CMS_SRS_Gantt.csv
- docs/HCS_CMS_SRS_Burndown.csv
- docs/HCS_CMS_Tech_Stack_Decision.md
- docs/README.md

## Actors
- Advocate
- Litigant
- Filing Scrutiny Officer (FSO)
- Registry Officer (Civil/Criminal/Writ)
- Hon'ble Judge
- Judicial Staff (PS/PA)
- Chief Justice (roster authority)
- System Administrator
- External Services: SSO, OTP/Aadhaar, ePayment gateway, CIS 1.0

## Use Case Index
- UC-01: Authenticate User via SSO
- UC-02: Submit eFiling in 4 Steps
- UC-03: Upload Searchable PDF Documents
- UC-04: Complete ePayment for Filing
- UC-05: Verify Filing using OTP/Aadhaar
- UC-06: Create and Accept Digital Vakalath
- UC-07: Perform Scrutiny of eFiled Case
- UC-08: Communicate Defects between FSO and Advocate
- UC-09: Generate EC-Prefixed Filing Number in CIS 1.0
- UC-10: Manage Registry Section Queues
- UC-11: Track Legacy Physical File Movement
- UC-12: View Advocate Portfolio by Bar ID
- UC-13: Download Orders and Real-Time Status
- UC-14: Manage My Partners Collaboration
- UC-15: Review Case Bundle in Multi-View Mode
- UC-16: Annotate Case Records (Notes and Highlights)
- UC-17: Sign Interim Orders and Final Judgments
- UC-18: Operate PS/PA Cause List and Draft Order Views
- UC-19: Produce Roster-Based Cause List
- UC-20: Auto-List Urgent Memos
- UC-21: Run AI-Assisted Scrutiny Recommendations
- UC-22: Use AI Research and Translation
- UC-23: Stabilize Courtroom Transcription Workflow
- UC-24: Migrate Legacy eFiling 3.0 Data
- UC-25: Deduplicate Identity Records for Single Person View
- UC-26: Maintain Audit Trail and CERT-In Controls

## Detailed Use Cases

### UC-01: Authenticate User via SSO
- Primary actor: Any CMS user
- Goal: Access CMS APIs and dashboards through enterprise SSO
- Preconditions:
  - User has valid account in SSO identity provider
  - CMS client app is registered with SSO provider
- Trigger: User opens CMS and clicks login
- Main flow:
  1. User is redirected to SSO login.
  2. User authenticates with required factors (MFA for judicial and registry users).
  3. SSO returns access token to client.
  4. Backend validates token and maps identity to local profile.
  5. User is granted role-scoped access.
- Alternate flow:
  - Invalid or expired token: access denied and user is prompted to re-authenticate.
- Postconditions:
  - Authenticated session established with role-based authorization context.

### UC-02: Submit eFiling in 4 Steps
- Primary actor: Advocate or litigant
- Goal: File a case electronically
- Preconditions:
  - Actor is authenticated
  - Case type and filing metadata template available
- Main flow:
  1. Enter case metadata.
  2. Upload searchable PDF set.
  3. Complete ePayment.
  4. Complete OTP/Aadhaar verification.
  5. System creates filing acknowledgement and sends to scrutiny queue.
- Alternate flow:
  - Validation failure in any step blocks next step and prompts correction.
- Postconditions:
  - Filing recorded with traceable status for scrutiny.

### UC-03: Upload Searchable PDF Documents
- Primary actor: Advocate or litigant
- Goal: Attach compliant documents to filing
- Preconditions:
  - Filing draft exists
- Main flow:
  1. User uploads PDF documents.
  2. System checks format and searchable text compliance.
  3. System stores and links documents to draft filing.
- Alternate flow:
  - Non-compliant files are rejected with corrective message.
- Postconditions:
  - Document bundle is ready for payment and verification steps.

### UC-04: Complete ePayment for Filing
- Primary actor: Advocate or litigant
- Supporting actor: ePayment gateway
- Goal: Pay applicable court fee for filing
- Preconditions:
  - Filing draft has required metadata and documents
- Main flow:
  1. User initiates payment.
  2. CMS redirects to payment gateway.
  3. Gateway returns success callback.
  4. CMS marks payment status as successful.
- Alternate flow:
  - Payment failure or timeout marks transaction as failed/pending and allows retry.
- Postconditions:
  - Filing can proceed to OTP/Aadhaar verification.

### UC-05: Verify Filing using OTP/Aadhaar
- Primary actor: Advocate or litigant
- Supporting actor: OTP/Aadhaar service
- Goal: Validate filing identity and submission intent
- Preconditions:
  - Payment completed for filing
- Main flow:
  1. User requests OTP challenge.
  2. User submits OTP/Aadhaar confirmation.
  3. CMS verifies response with external service.
  4. Filing submission is finalized.
- Alternate flow:
  - OTP mismatch or timeout triggers retry path.
- Postconditions:
  - Filing enters scrutiny workflow.

### UC-06: Create and Accept Digital Vakalath
- Primary actors: Advocate, litigant
- Goal: Create and accept digital authorization of representation
- Preconditions:
  - Parties are authenticated and linked to matter
- Main flow:
  1. Advocate initiates vakalath document.
  2. Litigant reviews and accepts digitally.
  3. CMS attaches accepted vakalath to case record.
- Postconditions:
  - Representation is digitally recorded and auditable.

### UC-07: Perform Scrutiny of eFiled Case
- Primary actor: Filing Scrutiny Officer
- Goal: Accept or return filing based on compliance checks
- Preconditions:
  - Filing is present in scrutiny queue
- Main flow:
  1. FSO opens filing bundle and metadata.
  2. FSO verifies compliance checklist.
  3. FSO marks filing accepted or defected.
- Alternate flow:
  - Defected filing is returned with comments to advocate.
- Postconditions:
  - Accepted filing is eligible for CIS number generation.

### UC-08: Communicate Defects between FSO and Advocate
- Primary actors: FSO, Advocate
- Goal: Resolve scrutiny defects quickly with full traceability
- Preconditions:
  - Filing has one or more defects
- Main flow:
  1. FSO sends defect message in case thread.
  2. Advocate receives notification and responds.
  3. Advocate re-submits corrected documents or metadata.
  4. FSO re-evaluates and closes defect loop.
- Postconditions:
  - Defect communication is timestamped in audit trail.

### UC-09: Generate EC-Prefixed Filing Number in CIS 1.0
- Primary actor: System
- Supporting actor: CIS 1.0 data consuming module
- Goal: Create official filing number after scrutiny acceptance
- Preconditions:
  - Filing status is accepted by scrutiny
  - CIS mapping and connectivity are available
- Main flow:
  1. CMS sends accepted filing payload to CIS integration layer.
  2. CIS allocates official filing number.
  3. CMS records number with EC prefix for e-filed identification.
- Alternate flow:
  - Integration failure triggers retry and incident log.
- Postconditions:
  - Filing is officially registered and moves to registry flow.

### UC-10: Manage Registry Section Queues
- Primary actor: Registry Officer
- Goal: Process cases across Civil/Criminal/Writ sections
- Preconditions:
  - Cases have entered registry queue
- Main flow:
  1. Officer filters queue by section and status.
  2. Officer updates processing steps.
  3. Officer routes case to next registry or listing stage.
- Postconditions:
  - Registry workflow is trackable per section.

### UC-11: Track Legacy Physical File Movement
- Primary actor: Registry Officer
- Goal: Track location of legacy physical records
- Preconditions:
  - File tracking module enabled
- Main flow:
  1. Officer records file handover event.
  2. Receiving section confirms receipt.
  3. System updates latest location timeline.
- Postconditions:
  - Physical file movement is traceable end-to-end.

### UC-12: View Advocate Portfolio by Bar ID
- Primary actor: Advocate
- Goal: Access all linked matters from a single portfolio
- Preconditions:
  - Advocate profile is linked with Bar ID
- Main flow:
  1. Advocate opens portfolio dashboard.
  2. System loads all associated cases.
  3. Advocate filters by status, court stage, and date.
- Postconditions:
  - Advocate can monitor all linked matters centrally.

### UC-13: Download Orders and Real-Time Status
- Primary actor: Advocate
- Goal: Retrieve latest orders and case updates
- Preconditions:
  - Advocate has access rights to case
- Main flow:
  1. Advocate selects case in portfolio.
  2. System shows timeline and latest orders.
  3. Advocate downloads signed order copy.
- Postconditions:
  - Advocate has current case status and documents.

### UC-14: Manage My Partners Collaboration
- Primary actor: Senior Advocate
- Supporting actors: Junior advocate, clerk
- Goal: Delegate drafting and case preparation access
- Preconditions:
  - Senior advocate account is active
- Main flow:
  1. Senior advocate adds partner to workspace.
  2. Senior assigns scoped access rights.
  3. Partner collaborates on draft artifacts.
- Postconditions:
  - Team collaboration occurs with controlled permissions.

### UC-15: Review Case Bundle in Multi-View Mode
- Primary actor: Hon'ble Judge
- Goal: Efficiently navigate large digital case records
- Preconditions:
  - Case bundle is available digitally
- Main flow:
  1. Judge opens case in courtroom interface.
  2. Judge toggles normal, flip, and split views.
  3. Judge navigates records during hearing.
- Postconditions:
  - Judicial review is completed in paperless mode.

### UC-16: Annotate Case Records (Notes and Highlights)
- Primary actor: Hon'ble Judge
- Goal: Add private notes and highlights on documents
- Preconditions:
  - Judge has opened case bundle
- Main flow:
  1. Judge opens notepad and annotation tools.
  2. Judge marks highlights and adds notes.
  3. System saves annotation context securely.
- Postconditions:
  - Judicial working notes are available for subsequent sessions.

### UC-17: Sign Interim Orders and Final Judgments
- Primary actor: Hon'ble Judge
- Goal: Digitally sign judicial output and publish to parties
- Preconditions:
  - Draft order/judgment is prepared
- Main flow:
  1. Judge reviews final draft.
  2. Judge applies digital signature.
  3. System seals and publishes signed artifact.
  4. Advocate dashboard receives order instantly.
- Postconditions:
  - Signed order is authoritative and downloadable.

### UC-18: Operate PS/PA Cause List and Draft Order Views
- Primary actor: Judicial Staff (PS/PA)
- Goal: Support judge with structured draft and listing workflows
- Preconditions:
  - PS/PA assigned to relevant bench
- Main flow:
  1. PS/PA prepares cause list draft and support artifacts.
  2. PS/PA prepares draft order package for review.
  3. Judge reviews and approves or returns edits.
- Postconditions:
  - Staff-assisted judicial workflow is completed with accountability.

### UC-19: Produce Roster-Based Cause List
- Primary actor: Registry Officer
- Supporting actor: Chief Justice (roster authority)
- Goal: Generate cause list using approved roster rules
- Preconditions:
  - CJ roster rules are configured
- Main flow:
  1. Registry triggers list generation window.
  2. System applies roster rule engine.
  3. Generated list is reviewed and published.
- Postconditions:
  - Daily listing follows approved roster logic.

### UC-20: Auto-List Urgent Memos
- Primary actor: Registry Officer
- Goal: Prioritize urgent matters through dedicated listing path
- Preconditions:
  - Urgency criteria and approval matrix configured
- Main flow:
  1. Urgent memo is submitted and tagged.
  2. Rule engine routes matter to priority listing queue.
  3. Registry validates and confirms auto-listing outcome.
- Postconditions:
  - Urgent matters receive accelerated listing processing.

### UC-21: Run AI-Assisted Scrutiny Recommendations
- Primary actor: Filing Scrutiny Officer
- Goal: Improve scrutiny speed and consistency using AI hints
- Preconditions:
  - AI scrutiny module enabled
- Main flow:
  1. FSO opens filing for scrutiny.
  2. AI suggests likely formatting/metadata defects.
  3. FSO accepts, rejects, or overrides suggestions.
- Postconditions:
  - Final scrutiny decision remains human-controlled and auditable.

### UC-22: Use AI Research and Translation
- Primary actors: Judge, Registry Officer, Advocate (as configured)
- Goal: Access legal research aid and translation support
- Preconditions:
  - AI module is available for pilot or production users
- Main flow:
  1. User submits query/text.
  2. System returns research references or translated content.
  3. User applies result in judicial/registry workflow.
- Postconditions:
  - AI output assists work but does not replace official decisioning.

### UC-23: Stabilize Courtroom Transcription Workflow
- Primary actors: Judge, Court staff
- Goal: Produce reliable courtroom transcript support
- Preconditions:
  - Transcription module deployed and calibrated
- Main flow:
  1. Hearing audio is processed by transcription service.
  2. Staff reviews transcript for quality.
  3. Approved transcript is attached to case context.
- Postconditions:
  - Transcript supports downstream judicial workflow.

### UC-24: Migrate Legacy eFiling 3.0 Data
- Primary actor: System Administrator
- Supporting actor: CIS/data team
- Goal: Move eligible legacy cases into new CMS
- Preconditions:
  - Migration plan and window approved
- Main flow:
  1. Export eligible registered/CNR-tagged records.
  2. Transform and map metadata/documents to CMS format.
  3. Import data and validate integrity.
  4. Generate migration audit report.
- Alternate flow:
  - During migration downtime, physical filing fallback is enabled.
- Postconditions:
  - Legacy baseline data is available in CMS with traceability.

### UC-25: Deduplicate Identity Records for Single Person View
- Primary actor: System Administrator
- Supporting actors: Registry/data quality team
- Goal: Resolve duplicate litigant/advocate identities
- Preconditions:
  - Identity matching rules defined
- Main flow:
  1. System detects probable duplicates.
  2. Reviewer validates merge candidates.
  3. System merges identities and preserves history links.
- Postconditions:
  - Single person view improves accuracy across workflows.

### UC-26: Maintain Audit Trail and CERT-In Controls
- Primary actor: System Administrator
- Goal: Enforce security and compliance requirements continuously
- Preconditions:
  - Logging and incident response controls are configured
- Main flow:
  1. System records tamper-evident audit events for document/case actions.
  2. System retains logs for 180 days in approved jurisdiction.
  3. Security team monitors incident alerts.
  4. Incident reporting workflow supports 6-hour reporting requirement.
- Postconditions:
  - Compliance controls are demonstrable for audits.

## Phase Mapping Summary
- Phase I use cases: UC-01 to UC-11 and UC-24
- Phase II use cases: UC-08, UC-10 to UC-14, UC-21, UC-22, UC-25
- Phase III use cases: UC-19, UC-20, UC-23, plus scale and hardening aspects of UC-26

## Notes
- Current repository has evolved toward external SSO token validation for API access.
- Some legacy statements in docs/README.md still describe embedded OAuth server endpoints.
- This use case document keeps business and workflow intent from SRS and sprint planning as the baseline.
