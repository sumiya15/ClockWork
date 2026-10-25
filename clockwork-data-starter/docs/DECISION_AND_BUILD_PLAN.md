# ClockWork: decision, data and build plan

Prepared 25 October 2026. The uploaded Word blueprint is the agreed product design. Its examples are not proof of official policy. Planning assumption: roughly 48 hours for a narrow working demonstration; the college deadline and team capacity remain unknown.

## Current evidence

The uploaded document was read in full here. The shared workspace has no ClockWork source tree; the Windows folder is not mounted here. Therefore the reported FastAPI startup checks are a local-agent report, not independently re-run in this environment. The earlier unrelated code was left unchanged. The included data kit was implemented and checked here; it is a separate deliverable, not a complete ClockWork application.

## What ClockWork solves

An official needs to know which approval/compliance action is pending, who must act, which deadline applies and what changes when an institution resubmits evidence. A dashboard can show a red count while still leaving those questions unanswered.

The agreed core is one obligation engine for stage processing, EVC work, undertakings and document validity. Unified storage does not mean identical clock behaviour: a processing timer can follow an authorized pause rule while fixed document expiry still arrives. Humans retain verification and regulatory decisions.

Common features include login, charts, filters, status colours, reminders and CSV exports. These are useful infrastructure, but the proposed platform becomes more convincing when one correct workflow demonstrates accountable next actions and traceable deadline decisions. Do not claim global novelty, low competition or knowledge of other submissions.

Claims to avoid: automatic APH compliance before rules are validated; operational accuracy from synthetic tests; an uploaded document already being verified; a role dropdown proving backend permissions; live integrations based on a mock adapter; reduced processing time without measurements; and tamper-proof audit based only on a hash chain.

## Three approaches within the fixed project

| Approach | User difficulty and mechanism | Data/dependencies | Demo | Extra effort beyond a shared core, estimate | Failure cases |
|---|---|---|---|---|---|
| A. Explainable deadline engine with pause-aware clocks and replay | The official cannot tell whether an item is genuinely overdue. Pin rule versions, keep pause intervals, distinguish fixed expiry from processing clocks, explain the next action, and preview changes under a demo clock. | Owner, stage, due date, pause/resume history, rule version and evidence state. No paid API or ML. | A paused EVC task is still within its adjusted deadline while the same institution's lease remains expired until verification. | Approximately 8-14 focused engineering hours for the distinguishing engine and tests, plus the application core. | Wrong rule or owner produces wrong notices. Missing dates/versions need manual correction. Simulation alone does not prove scheduled delivery. |
| B. Evidence-first compliance fulfilment | Institutions submit documents but cannot tell what remains unfulfilled. Link each condition to scoped upload, evidence version, officer verification/rejection and a reason. | Conditions, evidence metadata/files, verified expiry, recipient scope; token and file-storage handling. | A renewal is uploaded, rejected with a specific reason, corrected and verified; history remains visible. | Approximately 12-20 additional hours, depending on file/token handling and UI. | File presence is not document authenticity. Leaked tokens, wrong record scope or treating upload as approval can cause errors. |
| C. Stage bottleneck diagnosis and an actionable Today list | A supervisor sees many pending items but cannot locate the blocking stage. Group by region/stage/owner, use transparent ageing summaries and explicitly stated anomaly rules. | Reliable event timestamps and enough comparable completed stages. No model required. | A supervisor filters one fictional region, sees a stage with high synthetic ageing, and opens its actual pending owner/action. | Approximately 8-16 additional hours for defensible summaries and drill-downs. | Small or synthetic histories do not establish real workload norms. Averages can be misleading; missing timestamps should not become zero-day cases. |

Choose A as the main story. B still supplies required basic undertaking/document handling, and C still supplies required dashboard visibility; they are not separate new projects or permission to discard the agreed requirements. Polish A first instead of making every module an alleged innovation. The estimates are planning judgments, not measured team performance or guaranteed delivery times.

## One defensible example

At the fixed demonstration time, 25 October 2026 00:00 UTC:

- DEMO-APP-001 belongs to the fictional DEMO-INST-001 and is at EVC on the Scrutiny+EVC route.
- DEMO-OBL-001-STAGE has an original due date of 24 October. DEMO-PAUSE-001 records a return from 20 to 23 October: three paused days. Its effective due is 27 October, so it has a warning rather than an overdue flag.
- DEMO-DOC-001 and DEMO-OBL-001-DOCUMENT retain the expired 24 October date. A submitted renewal proposes a later expiry, but verification is still pending. It remains overdue, with a next action for an authorized officer.
- A simple original-date comparison marks both items overdue. The reference engine distinguishes them, identifies the rule version and returns supporting dates and owner.
- The officer can inspect the reason, correct a wrong source value through a later audited application action, or verify/reject evidence. The engine itself cannot decide statutory approval.
- If owner, date or rule version is missing, it returns unknown/manual correction. It must not send an invented notice or quietly infer institutional identity.

The kit checks the snapshot calculation. A full replay UI, actual permission checks, human actions, stored event changes and the running scheduler must still be implemented in the local application before they can appear as completed video features.

## Data strategy

Public reference documents can inform vocabulary and later rule validation. They do not provide application movement, officers' actions, confidential evidence or reliable operational ground truth. No freely reusable AICTE operational event dataset was verified in this research; this is not a claim that none exists.

Use the bundled 40 synthetic applications for the demonstration. The number follows scenario coverage: four route combinations, four fictional regions, five role types, normal/upcoming/overdue work, pauses, returns and evidence states. It is not a representative statistical sample.

The separate evaluation files contain 25 rule examples and 12 raw-import examples. They include exact thresholds, a pre-existing breach during a pause, pending vs verified renewal, equivalent timezones, missing owner/date/rule, invalid chronology, duplicate submission keys, similar names with distinct IDs and conflicting identifiers. Complaint wording similarity and RB/PGRC case linking are not part of this fixed approval project and are not implemented.

No training dataset is needed. No ML model is justified for the main mechanism. If an optional model is proposed later, obtain legitimate labelled data, a meaningful baseline and independent held-out institution/scenario groups first.

### Source research

Exact URLs, observation dates, access notes and intended uses are also machine-readable in source_catalog.json. Public reference files and personal contact details were not copied into the operational dataset.

| Source | Exact URL | Fields/content inspected | Licence/access | Intended use and limitation |
|---|---|---|---|---|
| AICTE Approval Process Handbook 2024-25 to 2026-27, government-hosted copy | https://cdnbbsr.s3waas.gov.in/s35938b4d054136e5d59ada6ec9c295d7a/uploads/2025/03/2025031399.pdf | Selected scrutiny/re-scrutiny, EVC and route-table passages; not a complete legal review. | PDF accessible. No general reuse licence verified; link/reference rather than bundle it. | Terminology and rule-review checklist. Does not validate every proposed 30/15/7-day example or later amendment. |
| AICTE 2026-27 addendum | https://aicte.gov.in/downloads/aph/Final%20Addendum%202026-27.pdf | Official search listing found; document body not inspected. | Direct request returned 403. | Pending policy-validation dependency; obtain an authorized readable copy. |
| Goa DHE AISHE college list | https://dhe.goa.gov.in/resource/getResource/%201%20128/ | Institution names, AISHE codes and districts. File says generated 16 October 2020. | Publicly readable. DHE page is copyrighted; no open bulk-data licence verified. Terms: https://dhe.goa.gov.in/resource/getPage/disclaimer | Optional historical identity-format reference only, not current approval status. Includes contact details that this project does not need and must not import. |
| AISHE final-report index | https://aishe.gov.in/aishe-final-report/ | Links labelled 2023-24 and 2022-23 reports/Excel. Report workbooks not inspected in this task. | Page accessible. https://aishe.gov.in/website-policies/ permits downloading but restricts reproduction/other reuse; do not assume GODL. | Optional background statistics only after checking a table's definition and reuse terms. Not operational events or deadline labels. |
| AICTE approved-institution dashboard | https://facilities.aicte-india.org/dashboard/pages/angulardashboard.php#!/approved | Row schema/export/API not inspected. | Direct fetch timed out. Reuse licence and programmatic access not verified. | Possible future registry verification, not a runtime dependency or claimed integration. |

Do not use real institution registry data as evidence of actual pending complaints, compliance failures or expiries. AISHE and AICTE identifiers are distinct namespaces. Public visibility by itself is not proof of an open redistribution licence. The application demonstration must read its local fixture and bundled frontend assets after setup; no public lookup, external font or CDN UI dependency should be required for its core journey.

## Honest evaluation

Expected labels were explicitly specified from the demonstration semantics and stored separately from algorithm inputs. They were authored by the assistant and need student-team review. They are not AICTE labels, unseen blind tests or a validated operational benchmark. No training/tuning split is claimed.

The simple baseline checks the original due date, honors completed state and ignores pauses and verified renewal dates. Compare overdue false positives and false negatives only where the expected label is binary; report unknown/manual-review cases separately. Refer to VERIFICATION.md for observed counts, not targets.

The operational fixtures and rule examples have separate scenario-group namespaces. If the team later tunes rules against the examples, preserve this suite as regression coverage and obtain new independently authored cases; do not relabel the same examples as an unseen holdout. A real pilot would additionally measure notice usefulness, missed actions and time to identify the next responsible owner.

## Milestones and acceptance checks

| Milestone | Scope and requirement mapping | Observable acceptance check |
|---|---|---|
| 1. Source handoff and data foundation | Word blueprint, canonical fixtures, SQLAlchemy entities, SQLite, idempotent seed, provenance, persisted demo clock | Local agent reads the actual Word file. Seed twice keeps 40 applications with no duplicates. An edited record and clock survive a separate process restart. Invalid imports get explicit outcomes. |
| 2. Authentication and scoped reads | Real login/logout, hashed credentials, server-side sessions, five proposed roles; protected lists/details | Anonymous access denied. Institution A cannot read B by guessed URL. Regional scope and committee assignment apply to records, documents and counts. No password/session fields leak. |
| 3. Approval state machine | Configured routes, authorized movement, return with reason, resubmission, stage-specific owner and timeline | Scrutiny+EVC enters EVC only after an authorized completion. An invalid/skipped transition fails. Return reason and pause interval persist; statutory decisions remain human actions. |
| 4. Distinguishing deadline engine | Type-specific clocks, pinned versions, why-lines, safe unknown state, configurable escalation, APScheduler/outbox and demo-clock controls | Paused EVC and expired document differ correctly. Repeat scheduler ticks or repeating the same clock advance do not duplicate notifications. Crossing a threshold records the correct recipient, rule and reason. Restart preserves state. |
| 5. Required compliance workflow | EVC queue, undertaking register, lease/document register, scoped upload links, officer verification, protected encrypted storage, summaries/templates and reports | Pending upload stays pending. Officer verification changes only the right record. Expired/foreign tokens fail. Reports agree with scoped records. Record encryption as pending unless actually configured and tested. |
| 6. Usable frontend | React/Tailwind Today, Dashboard, Registers, Case, Rules/Reports and institution upload page; clear statuses and polling | Every visible action works or is labelled unavailable. Role views match backend scope. Refresh preserves edits. Show one large readable timeline/reason panel rather than many tiny screenshots. |
| 7. Final demonstration proof | Actual browser rehearsal, restart, failure example, screenshots and video | Record the real working interface, identify synthetic data and demo time, show saved outcome and a difficult case, and disclose mock integrations. |

If the preparation window is only 48 hours, prioritize source/data, secure access, one correct route and the deadline example, then a minimal readable interface. Complete required compliance paths next; label any remaining blueprint items planned. Do not claim complete coverage of the Word document from a narrow working slice. Optional work: OCR date prefill with officer confirmation, live mail delivery, richer calendar and real adapters after access is available. LLM briefs, workload balancing and an opaque compliance score are excluded by the agreed plan.

## Evaluator questions to rehearse

1. What is different from a normal dashboard? Demonstrate type-specific accountable deadlines and their supporting events, rather than only stating that alerts exist.
2. Are these real AICTE records? No. They are reproducible fictional records; public sources inform background and later rule validation only.
3. Where did the timelines come from? The demonstration configuration and agreed blueprint. Official values require checking the applicable handbook, amendments and authorized procedures.
4. Does a document upload make the institution compliant? No. Show pending evidence and the authorized verification step.
5. What if a rule or identifier is wrong? Hold for correction with a reason. Preserve identity boundaries and a versioned audit record of a correction.
6. How do you stop duplicate alerts? Demonstrate the live outbox uniqueness constraint and repeated-tick test once implemented. The kit's stable key alone is not sufficient evidence.
7. Is the audit tamper-proof? No such claim is justified here. A later protected hash chain can reveal changes under stated assumptions, but a privileged attacker can rewrite a chain without independent anchoring.
