# ClockWork readiness — SIH 26262

## Verdict and scope

The emerald mobile frontend is ready for a fictional-data prototype presentation and screenshots. It is not a secure operational approval system. Working interactions were exercised, not inferred from images. Backend code, stored databases and existing video files are preserved; no video was created or modified in this refresh.

The strongest demonstrated controls are **preserved SLA time**, **shared explainable deadline evaluation**, and **verification before compliance/validity changes**. These are useful implementation choices, not claims of uniqueness across competitors or guaranteed screening qualification.

## References and limitations

Primary evaluation reference: the problem statement supplied in this conversation—Background, Problem Statement, sections A–E, and the F heading—plus the user's explicit finalisation checklist. The supplied statement stops before the detailed F body. The complete corrected blueprint was read from Word paragraphs and tables: [AICTE Hackathon Verdict and Merged Blueprint.docx](reference/AICTE%20Hackathon%20Verdict%20and%20Merged%20Blueprint.docx). Its SHA-256 is `e0c4037001d37ad5940db5daeb9107adc18ef0d04480fc7d56b6d1c64f8c7d50`.

A [full third-party transcription of PS 26262](https://zaidsayyed.in/tools/sih-problem-statements/sih26262) was inspected to check the missing section: it describes configurable notices, escalation, six reports, audit coverage, security, integration and human oversight. It is not treated as authoritative policy. The [official problem-statement endpoint](https://sih.gov.in/sih2026PS) returned HTTP 403 during verification, and official-domain searches did not yield the complete statement. The blueprint and explicit user checklist independently supply those requirements. No competition scores, deadlines or selection predictions from third-party pages were adopted.

No official slide template or architecture-reference attachment was available in the repository/session. The presentation is a suggested outline; architecture diagrams follow the component grouping requested by the user. Applicable APH timings, pause permissions, route selection and escalation authorities still require official validation.

Other inspected references: ARCHITECTURE.md, PROJECT_STATUS.md, AUTHORIZATION.md, SIH_DEMO_REVIEW.md, API_CONTRACT.md and the actual React entry point, local services, API router, health, auth, audit and notification foundation. Older documents describe historical states; this review supersedes their presentation wording and readiness claims.

## Requirement matrix

Paths beginning `demo/` below refer to `frontend/src/demo/`. **Simulated** means a functioning browser-local interaction, not real authentication, delivery or shared persistence. **Implemented** means verified executable functionality within the stated local scope. **Partial**, **missing**, and **proposed** retain their ordinary meanings. Backend source inspection is explicitly separate from fresh frontend tests.

Verification references: **U** = `frontend/tests/demo-service.test.js`; **B** = `frontend/tests/demo.spec.js`; **P** = `frontend/tests/final-presentation.spec.js`; **M** = `frontend/tests/presentation-measurements.mjs`; **W** = `frontend/tests/wording.test.js`; **S** = source inspection, not a live integration test.

| Requirement | Screen/action | Code evidence | Verification | Status |
|---|---|---|---|---|
| Only Scrutiny | Case → Complete stage → Human decision | `demo/model.js: ROUTES`, `service.js: nextStage/changeCase` | U + M exact ordered sequence | Simulated |
| Scrutiny + EVC | Complete scrutiny → queue → schedule → visit → report → officer verification | `nextStage/enqueueEvc/evcAction` | U + M full route; B completes report; P schedules/breaches EVC | Simulated |
| EVC + SAC/SHC | EVC workflow then assigned committee completes SAC/SHC | `ROUTES`, `evcAction`, `can` | U + M exact ordered sequence | Simulated; SAC/SHC combined |
| Only EVC | Scheduling → visit → report verification → Human decision | Same route functions | U + M | Simulated |
| Authorised next-stage movement | Stage completion assigns owner, due date and next stage | `can`, `appFor`, `nextStage` | U invalid scope/stale version checks; B persona actions | Simulated; real authorisation not connected |
| Other routes / new filing | Rules can edit supported future stages | `validateRule/previewRule/publishRule` require four named routes | U + B invalid settings/version migration; S filing absent in frontend | Partial; arbitrary types and new filing missing |
| Return/revert with reasons | Case → Return with reason; institution resubmits | `changeCase`, pauseIntervals; `CaseDetail.jsx` retained reason | U repeated pauses/blank reasons; B + P return/resubmit | Simulated; arbitrary backward-stage revert missing |
| Preserve SLA | Paused/resumed state and active elapsed shown | `effectiveDue/remaining/activeDays` | M: two 7-day pauses retain 5 remaining / 9 active days | Simulated, verified arithmetic |
| Standard communications | Case → Communications | `service.js: event`, `CaseDetail.jsx` templates | B creates deficiency/resubmission entries; S rendering | Partial; templates and unsent records, no real letters/delivery |
| Factual case summaries | Case Overview; optional AI Assist | `CaseDetail.jsx`, `assistant.js` reads scoped records | B case sections; assistant unit tests; P summary/blocker/draft | Simulated; no live model |
| Role / Region / institution / committee views | Controls, Dashboard filters, case scope | `model.js: visible/can`, `reports.js: filterApps` | B five personas, four Regions, committee/institution scopes, filters | Simulated, not authenticated |
| Ageing / pendency / workload / bottlenecks | Dashboard charts and officer assignments | `DemoApp.jsx` derived counts, means, stage cohorts | B filters/drill-downs; P screenshots; M report counts | Partial; means available, anomaly/slowest-stage recommendations missing |
| Approaching / overdue items | Today → urgent action; Notifications | `targets/evaluate/scan`, `remaining` | M four date scenarios; P action/alert navigation | Simulated; no autonomous scheduler |
| EVC queue and new institutions | Registers → EVC → institution-type filter | `enqueueEvc`, `EvcRegister.jsx` | U one EVC record; P filtered new-institution queue | Simulated |
| EVC scheduling / completion | Assign committee/date; complete visit; submit/verify report | `evcAction` stage/date/scope checks | U + B full lifecycle; P scheduling/overdue ladder | Simulated; no real calendar integration |
| Undertaking conditions and dates | Undertaking register | `model.js` linked records; `Evidence.jsx` | U relations; P REG-DEMO-U | Partial; seeded records, no creation from conditional approvals |
| Submission and officer verification | Submit → awaiting officer verification → verify/reject with reason | `evidenceAction`, `Evidence.jsx` | U unauthorised/blank decisions; B rejection; P verification | Simulated; only filename/date metadata |
| Undertaking overdue escalation | Scan after due, inspect recipient/explanation | `targets/evaluate`, notification records | M overdue IDs/recipient ladder; P alerts | Simulated |
| Lease expiry and advance warnings | Documents → expired/expiring/valid | `validity`, `targets`, `Evidence.jsx` | U + M dates; P expired record | Simulated; general prescribed-document registry missing |
| Renewal and verification | Proposed renewal remains pending; officer updates verified expiry/history | `evidenceAction`, renewalHistory | U rejection/pending date invariants; B + P submission/verification | Simulated, verified state boundary |
| Configurable alerts / why / recipients | Rules → validate/preview/publish; Notifications → Why this alert? | Rule versioning; `wording.js: alertReason/alertCopy` | U/B rules; M recipient ladder; W historical explanation | Partial; timings editable, channels/recipient ladder fixed |
| Six reports | Reports → pendency, EVC, undertakings, documents, overdue, Region performance → CSV | `reports.js: report/csv/downloadReport` | U + M all selectors; B + P six actual downloads | Implemented local reports on simulated data |
| Application / alert / submission / verification audit | Case Timeline; Notifications activity | `event`, `Timeline`, `activityCopy` | U state/history; B + P timeline events; W clean summaries | Partial; editable local history, no real sent receipts/access audit |
| Closure audit | Seeded completed cases only | No final decision action in `can/changeCase` | U/M stop at Human decision; S no closure endpoint in Mongo router | Missing live closure/decision action |
| Human oversight | Manual stage, committee and evidence decisions with reasons | `can`, `evcAction`, `evidenceAction` | U + B authorisation boundaries; route tests issue no approval | Simulated; final decisions/general override incomplete |
| Security / confidentiality | Separate API-mode login/scoped reads | `backend/app/modules/auth`, scoped repositories | S current source; historical backend tests not rerun | Partial foundation, not security for demo personas |
| Protected storage | UI accepts sample file metadata only | `Evidence.jsx`; no file endpoint in current API router | P metadata flow; S route inventory | Proposed; no secure file-byte storage/download |
| Tamper-evident audit | Separate Mongo chain/transaction/outbox helpers | `backend/app/modules/audit`, `db/transactions.py` | S implementation exists; not connected to local actions | Partial foundation |
| Existing AICTE systems | Future adapter boundary in target diagram | Current router/seed; no connected adapter | S no real integration path | Proposed |

## Runtime distinction and architecture

**Current prototype:** React/Vite mobile screens invoke `DemoApp.act(operation)` with the current local state. Workflow/evidence/rule functions clone and return updated state; `saveDemo` writes localStorage before React state updates. `model.js` supplies timing/scope selectors; `targets/evaluate/scan` normalise approval/compliance deadlines. sessionStorage retains view choices. AI Assist uses deterministic scoped templates; notifications are local records. Uploaded file bytes are not stored. No backend API request occurred in the screenshot journey.

**Separate existing foundation:** API-mode React uses FastAPI `/api/v1`, MongoDB, cookie authentication, scoped reads, published-rule reads, audit/outbox helpers. The current API router exposes no operational workflow/EVC/evidence mutation endpoints; the scheduler health endpoint says disabled. Demo admin can read operational records whereas API admin cannot; this access-model mismatch must be reconciled. Regional demo roles are not individually authenticated assigned officers.

**Preserved legacy SQL runtime:** `backend.main:app` has authenticated filing, complete/return/resubmit and history endpoints in `backend/workflow.py`. Those are not integrated with the current default frontend or the Mongo runtime.

**Target:** authenticated React → FastAPI operational services → shared rules/transitions/deadlines → MongoDB and protected evidence storage; scheduled worker, audit records, authorised adapters and optional future backend AI assistance. Dashed diagram borders/arrows identify missing or incomplete components/connections. See [architecture sources and exports](presentation/architecture/README.md).

## Measured results and limits

Fresh production-function measurements are in [measurements.json](presentation/evidence/measurements.json). Dataset: 60 applications, 60 institutions, four Regions, 60 undertakings, 60 leases, 36 initial EVC entries; 52 open and eight seeded completed applications.

- All four route sequences matched configuration and stopped at Human decision, without issuing approval. Each scenario resets Cedar to that route's first stage; this is a controlled function test, not four separately filmed cases.
- At baseline/+1/+7/+30 days, active nonpaused overdue targets were 63/64/98/129; due today 1/0/1/0; upcoming seven-day targets 35/35/6/0. Overdue report IDs matched the corresponding nonpaused targets. Every eligible due/overdue/upcoming target had an alert record.
- Initial full-scope reports: pendency 52 rows, EVC 36, undertakings 60, documents 60, overdue 65, Region performance 24. The overdue report also includes two paused cases; the dashboard counts applications only (25 overdue initially), not all obligations.
- Independent +30-day scenario: 669 message records, five repeated scans, zero added messages, zero duplicate IDs. No concurrent delivery worker was tested.
- Two seven-day clarification pauses retained five remaining days and nine active days, with 14 paused days and two resubmissions.
- Undertaking remains pending until verification; renewal preserves the expired 23 October 2026 validity until verification and retains its prior version. The screenshot journey enters a new expiry of 1 December 2027.
- The screenshot journey advances +7 then +30 days, records 900 unsent messages, and adds none on a repeat scan. This differs intentionally from the independent +30 scenario.

No real-world time savings, AI accuracy, production impact or policy correctness was measured. The displayed demo/technical wording was removed from primary surfaces, not from the underlying provenance. About this prototype explains all simulation boundaries; AI Assist retains Preview, an information panel and unsent draft wording.

## Three differentiators, and what they do not prove

1. **Preserved SLA time:** active elapsed and remaining allowance survive repeated returns; policy permission to pause still needs validation.
2. **Shared explainable deadline evaluation:** application and compliance targets share one evaluator and versioned explanations; this is not a production scheduler or universal obligation lifecycle.
3. **Verification before status changes:** submission does not clear an undertaking or replace verified lease validity; actual document content review requires secure storage and backend integration.

Routing, dashboards, EVC, compliance monitoring and alerts are mandatory features. The three control behaviors are useful implementation differentiators. Green colours, spacing, initials and photographs are cosmetic improvements. Real delivery, authenticated operational writes, protected storage, full audit, external adapters and live AI are future capabilities. AI preview is optional and not presented as novelty required by the brief.

## Remaining gaps by priority

**P0 operational:** authorised persistent mutations and concurrency controls; real filing/conditional approvals/final decisions/closure; protected evidence bytes and access; unattended deadline evaluation and durable delivery/retry handling; connected complete audit coverage; validated APH routes/timelines/pause/recipient rules; account administration and deployment/recovery controls.

**P1 complete coverage:** other document/route types; configurable channels/recipients; authorised correction/override; formal communications; shared reporting; agreed AICTE integration contracts; access-model parity. Fixed 30-day expiry colouring should be reconciled with configurable reminder windows. Mean stage ageing is not automatic anomaly diagnosis.

**Source limitations:** complete authoritative PS F body, applicable APH extracts and official submission template were not verified. The architecture reference attachment was not available; requested grouping was followed. These limits do not block the delivered frontend assets, but prevent a claim of complete official compliance.

Ready for a prototype demonstration and manual recording with accurate narration. Not ready for secure operational deployment. No video work was performed. Executed results and preservation checks are in [VALIDATION.md](presentation/VALIDATION.md).
