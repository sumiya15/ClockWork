# ClockWork — suggested SIH presentation outline

No official PPT template was found in the repository. This is paste-ready suggested content, not an official slide rubric. PS 26262: Integrated AICTE Approval Workflow Automation, Compliance Monitoring and Alert Management System.

## 1. Problem
Approval movement, committee visits, undertakings and document validity create connected deadlines across institutions and officials. A missed handoff or an unverified submission can leave a case unresolved. Officials need an actionable view of responsibility, elapsed time and evidence status.

Visual: 01-today or 01b-today-actions.

## 2. Solution
ClockWork brings applications, EVC visits, undertakings and lease validity into one mobile workspace. Today links urgent records to actions; scoped dashboards show pendency and workload. Human decisions remain explicit.

Current deliverable: a working frontend presentation prototype with fictional data and browser persistence. Communications and AI Assist are simulated.

Visual: 02-dashboard and 09-compact-cases.

## 3. Connected workflow
Four configured routes move to the next stage after an authorised simulated action. Returns require reasons. EVC scheduling, visit completion and report verification are separate. Evidence receipt remains pending until an officer verifies it. Six CSV reports and case history support review.

Visual: 03c-case-route, 04-evc, 08-reports.

## 4. Three implementation differentiators
- Preserved SLA time: two seven-day pause/resubmit cycles retained nine active days and five remaining days in the functional measurement.
- Shared explainable deadline evaluation: application and compliance targets use common threshold evaluation; alerts show deadline, rule version and responsible authority. Five repeated scans added zero alerts at a fixed date.
- Verification before change: submitted lease renewal left the old expired validity in force; officer verification updated the expiry and retained history.

These are demonstrated implementation choices, not claims of uniqueness among competing products. Workflow monitoring, compliance and alerts themselves are mandatory requirements.

Visual: 03b-case-resumed, 05b-alert-explanation, 07-lease-pending / 07b-lease-history.

## 5. Current architecture
React mobile interface → shared local application state → workflow/deadline functions → localStorage persistence. Session storage retains view choices. AI Assist reads scoped facts through deterministic templates. Communication records are local simulations; evidence stores metadata, not document bytes.

Use [current-prototype.png](architecture/current-prototype.png). FastAPI and MongoDB foundations exist separately and do not power the demonstrated workflow mutations.

## 6. Target architecture and feasibility
React → FastAPI → MongoDB, with server-authorised workflow transitions, shared rules/deadline evaluation, protected document storage, scheduled workers and authorised integration adapters. Officer verification gates remain explicit. Future AI assistance belongs behind a scoped backend endpoint with human review.

Use [target-system.png](architecture/target-system.png). Solid foundation boxes indicate existing code, not production certification. Dashed components and connections are incomplete or proposed.

Next delivery priorities: validate applicable APH rules and authority mapping; implement domain APIs and server enforcement; secure document handling; add reliable scheduled delivery and protected audit history; test authorised integrations end to end.

## 7. Measured prototype results
Dataset: 60 applications, 60 institutions, four Regions, 36 EVC records, 60 undertakings and 60 leases. All four configured routes reached a human-decision gate in direct functional tests. Baseline overdue targets: 63 of 152 active targets; independent +30-day scenario: 129. Five repeat scans added zero alerts and produced zero duplicate IDs. Undertaking and renewal submissions stayed pending until verification.

These are synthetic functional results, not accuracy, time-saving or production impact estimates. Browser walkthrough covers Scrutiny + EVC; other routes were exercised through production frontend functions.

## 8. Intended impact and limitations
Intended benefits: clearer ownership, earlier follow-up, consistent evidence status and less manual status consolidation. Field evaluation is still needed to measure those benefits.

The prototype does not deliver communications, store evidence bytes securely, authenticate workspace personas, issue statutory approvals or integrate with AICTE systems. Final decision/closure remains incomplete. AI Assist is a preview, not a running model.

Visual: 14-about-prototype; optional AI images 11–13 only if time permits.

## 9. References
- User-supplied PS 26262 and explicit requirement checklist: primary evaluation reference; supplied text ends at the F heading.
- Repository blueprint: `docs/reference/AICTE Hackathon Verdict and Merged Blueprint.docx` (provenance and hash in readiness review).
- [Official SIH problem-statement page](https://sih.gov.in/sih2026PS): access returned HTTP 403 during review.
- [Supplemental transcription of PS 26262](https://zaidsayyed.in/tools/sih-problem-statements/sih26262): full text inspected, third-party and not independently authenticated against the official source.
- [Evidence-based requirement matrix](../SIH_26262_READINESS.md), [validation](VALIDATION.md), [screenshot index](SCREENSHOT_INDEX.md).

No claim of screening qualification or official scoring is made. Existing video files were not updated; record the current UI using VIDEO_SCRIPT.md.
