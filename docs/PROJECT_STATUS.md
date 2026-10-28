# Latest: presentation wording polished

## Presentation wording polish (2026-10-25)

Primary alert content now shows a readable deadline status, overdue/remaining days and next action. Historical alerts use their recorded deadline and scan date, not today's current record. Full rule/threshold references remain in expandable **Why this alert?** details. Recipient labels use Institution document coordinator; timeline update counts use singular/plural correctly. Case elapsed time no longer leads with a rule version. Communications, activity, reports and assistant dates use readable dates; encoded spaces are normalized at presentation boundaries without rewriting stored records.

AI Assist has a compact **AI preview** label and an **About AI preview** information button. Its keyboard-accessible dialog explains sample-record responses, no live model, draft review and simulated messages/approvals. A small shared **Demo** badge remains visible. More > **About this demo** collects imagery, rule, local-storage and simulation explanations. Photos retain short not-inspection-evidence captions; uploads still explicitly say files are not uploaded. Copy uses the same polished text shown on screen.

Verified: lint/build passed; 8 assistant/wording unit tests passed; all 8 Playwright browser checks passed in 46.1 seconds (workflows, persona/filter scopes, persistence/reset, 360/390/430 layouts, clipboard/fallback, image fallback, information dialog and detailed alert explanations). Console/API diagnostics passed. Refreshed 390x844 captures in docs/screenshots/mobile/, including 09-notifications, 12-institution-profile, 14/15 AI responses and 19-23 compact cards/EVC assistant. Notification and AI summary captures visually inspected. No backend, dependency, workflow or stored-data migration changes.

Changed files: wording.js; AssistantPanel, Notifications, CaseDetail, InstitutionProfile, Evidence, RulesReports; DemoApp.jsx, ui.jsx, assistant.js, demo.css; wording.test.js and demo.spec.js; presentation docs and mobile PNGs.

Commands: `node --test frontend/tests/assistant.test.js frontend/tests/wording.test.js`; `npm --prefix frontend run lint`; `npm --prefix frontend run build`; `CLOCKWORK_EXTERNAL_SERVER=1 CAPTURE_MOBILE=1` with `node frontend/node_modules/@playwright/test/cli.js test --config frontend/playwright.demo.config.js` (PowerShell environment variables set separately). Test-owned Vite ran at port 5175 and was stopped afterward.

Next bounded task: record the walkthrough using current screenshots. Real AI, external delivery and production authorization remain outside this frontend work.

---
# Latest update: compact mobile cards and case-aware AI Assist

2026-10-25. Frontend-only refinement complete; backend and persisted dataset schema unchanged.

Changed: ui.jsx, DemoApp.jsx, InstitutionIdentity.jsx, caseGuidance.js, CampusImage.jsx, InstitutionProfile.jsx, CaseDetail.jsx, AssistantPanel.jsx, assistant.js and demo.css. These replace list photography with stable initials and useful metadata, restrict the single campus exterior to INST-2, expose AI Assist on Today/all Case sections, and provide EVC facts, linked references, next-screen actions and response retry. Updated assistant/browser checks, attribution, frontend guide, assistant design and SIH review.

Actual checks: `node --test frontend/tests/assistant.test.js` (6 passed); `npm --prefix frontend run lint` (passed); `npm --prefix frontend run build` (passed, 40 modules). Playwright with CLOCKWORK_EXTERNAL_SERVER=1 and CAPTURE_MOBILE=1: `node frontend/node_modules/@playwright/test/cli.js test --config frontend/playwright.demo.config.js` (7 passed, 44.8 seconds). Test-owned Vite used port 5175. Initial run found one stale photo caption, corrected before the final passing run. Browser coverage includes workflow journey, all personas/filters, reload/reset, 360/390/430 widths, image fallback, assistant case switching, copy fallback, retry, EVC navigation and no console errors/API requests.

390x844 captures saved under docs/screenshots/mobile/: 12 profile, 13 case overview, 19 Today compact cards, 20 compact institution cards, 21 EVC summary, 22 EVC blockers, 23 EVC reminder. Cards and blocker screenshots visually inspected. Earlier photo-list screenshots 16/17 are superseded historical artifacts.

Limits: one licensed campus exterior available; other profiles intentionally use initials covers. AI is explicitly a simulated preview, no running model or sending. Missing delay reasons remain unavailable. Presentation refinements do not establish production authentication or statutory authority. Existing unrelated user edits preserved. Next bounded task: rehearse Today AI Assist -> overdue CW-2026-009 -> blocker -> reminder -> EVC link using the updated captures.

---

# Current status: photographic presentation layer complete

2026-10-25: Added actual campus, laboratory equipment, classroom and library photographs from Pexels. Downloaded only optimized 800px variants: four JPEGs total 302,876 bytes. The previous rate-limited Wikimedia source was not retried. Source pages, photographers, Pexels License, direct download URLs, dimensions and SHA-256 values are recorded in IMAGE_ATTRIBUTION.md. No dependency, extracted tool, archive or database was deleted; disk space was checked first (~267 MB available).

## Focused changes

- `frontend/public/photos/{campus,laboratory,classroom,library}.jpg`: real local photographs, also verified byte-identical in production dist/photos.
- `frontend/src/demo/CampusImage.jsx`: local image selection, alt text, crop positions, explicit illustrative/fictional captions, retained inline loading-error fallback, and small facilities gallery.
- `DemoApp.jsx`: compact Today campus banner below metrics. Dashboard/report charts remain photo-free.
- `screens/InstitutionProfile.jsx`, `ui.jsx`: campus covers/thumbnails and exact illustrative-photo label. Real photos do not establish fictional institutions' facilities.
- `screens/EvcRegister.jsx`: selected-record facilities preview, explicitly not verified inspection evidence. Workflow actions/statuses remain unchanged.
- `demo.css`: restrained image crops and three-column mobile gallery. `frontend/tests/demo.spec.js`: local photo loading, no external request dependency, three widths, navigation and actual decoding-error fallback.
- Updated IMAGE_ATTRIBUTION.md, FRONTEND_DEMO.md and SIH_DEMO_REVIEW.md. Existing simulated AI, dataset, backend and user changes preserved.

## Actual verification

- `npm.cmd --prefix frontend run lint`: passed.
- `npm.cmd --prefix frontend run build`: passed, 38 modules, final run 218 ms.
- With the documented test-owned Vite server on 5175 and CLOCKWORK_EXTERNAL_SERVER=1, `node node_modules/@playwright/test/cli.js test --config playwright.demo.config.js`: **6 passed in 37.3s**, clean exit. No console/runtime errors or unexpected backend requests. New image check blocks external HTTP requests and verifies local JPEG dimensions; navigation/fallback and 360/390/430 widths passed.
- Sequential opt-in captures with `--grep 'phone walkthrough|institution imagery|local photographic'`: **3 passed in 15.4s**. Final gallery framing recheck/capture with `--grep 'local photographic'`: **1 passed in 2.9s**.
- All 18 PNGs in docs/screenshots/mobile verified 390x844. Affected photo screens visually inspected for crops, label readability and overlap. No videos/traces generated. Test server stopped after work; unrelated servers untouched.

## Updated presentation artifacts

- `16-today-photo.png`: compact campus banner.
- `17-institution-photo-cards.png`: campus thumbnails.
- `12-institution-profile.png`: campus cover.
- `13-case-overview.png`: case cover.
- `18-evc-facility-photos.png`: laboratory, classroom and library gallery.

Remaining screenshots 01-15 were also refreshed through the preserved workflow/assistant journeys. Set 01-10 uses 1 December 2026; photo/profile/AI sets 11-18 use 25 October 2026. Do not imply the stock photos depict verified facilities, inspection results or real institutional endorsement.

No photo-delivery blocker remains. This layer is ready for prototype PPT/screenshots and recording; underlying production/security/official-reference limitations remain as documented. Offline means locally hosted assets with no external image service, not a new service worker or file:// app. Next task is presentation rehearsal or actual PPT review, not backend rebuilding.

---

# Prior status

# Current status: institution profiles and AI preview verified for presentation

Updated 2026-10-25. The frontend-only enhancement is complete and verified for prototype PPT screenshots and a rehearsed mobile recording. A real model, real authentication, external delivery and production readiness are not claimed. Backend code, database, extracted tools and user edits remain preserved. No MongoDB archive was deleted in this run; roughly 277 MB was already free at the start and about 249 MB remained after capture.

## Implemented files and purpose

- `frontend/src/demo/CampusImage.jsx`, `assets/campus-1.svg` through `campus-3.svg`, `screens/InstitutionProfile.jsx`: fictional scoped profiles, local illustrative campus imagery, thumbnails, inline decoding-error fallback and application/requirement links. Photos could not be downloaded because Wikimedia returned HTTP 429; no broken remote image dependency or false photo claim was introduced.
- `frontend/src/demo/assistant.js`, `screens/AssistantPanel.jsx`: replaceable deterministic async service, scope checks, case-specific summaries/pending/next actions, review-only drafts, supported questions, citations, loading/error/retry, clipboard/manual-copy fallback. Missing date/stage data is reported unavailable. Responses are ephemeral and invalidated on case/scope/revision changes.
- `DemoApp.jsx`, `screens/CaseDetail.jsx`, `ui.jsx`, `demo.css`: More and case entry points, institution navigation, coherent navy/blue/emerald styling and existing SVG system. Fixed the Today month abbreviation for single-digit dates and keyboard focus restoration after modal close.
- `frontend/index.html`, `frontend/public/favicon.svg`: local favicon fixes the console 404 found by browser checks.
- `frontend/tests/assistant.test.js`, `frontend/tests/demo.spec.js`, `frontend/playwright.demo.config.js`: assistant service tests and expanded mobile checks; every browser test watches console/runtime errors and backend API requests. Optional external test server avoids a Windows teardown hang. Capture is opt-in, sequential, without video/trace artifacts.
- `docs/FRONTEND_DEMO.md`, `SIH_DEMO_REVIEW.md`, `IMAGE_ATTRIBUTION.md`, `ASSISTANT_DESIGN.md`: actual setup, walkthrough, evidence, asset provenance and future authorized FastAPI/model integration. No new framework/dependency was installed.

## Actual commands and outcomes

- `node --test frontend/tests/assistant.test.js frontend/tests/demo-service.test.js`: **13 passed**, 695 ms on the last service run.
- `npm.cmd --prefix frontend run lint`: **passed**.
- `npm.cmd --prefix frontend run build`: **passed**, 41 modules; final run 390 ms.
- Started a test-owned server from frontend: `node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5175 --strictPort`.
- With CLOCKWORK_EXTERNAL_SERVER=1, `node node_modules/@playwright/test/cli.js test --config playwright.demo.config.js`: **5 passed in 41.0 seconds**, exit 0. Covers full workflow, every individual filter/persona, all mobile sections, keyboard, assistant, images, copy/retry, persistence/reset, and 360/390/430 widths; no console/runtime errors or /api requests.
- Final single-digit month-label check: phone walkthrough **1 passed in 9.3s**. Actual corrupt-image fallback check: institution/assistant journey **1 passed in 8.3s**.
- With CLOCKWORK_EXTERNAL_SERVER=1 and CAPTURE_MOBILE=1, same command with `--grep 'phone walkthrough|institution imagery'`: **2 passed in 16.4 seconds**, exit 0. Captured sequentially after verification. The owned server was stopped with Ctrl+C afterward; unrelated servers were not stopped.

Initial managed-server runs exposed a missing favicon and focus-restoration issue, which were fixed. The Windows Playwright-managed server hung during teardown; the documented two-terminal workflow produces clean test exits. No physical device test was performed; browser checks used Edge mobile emulation.

## Delivered presentation artifacts

All 15 PNGs in `docs/screenshots/mobile/` were validated at 390x844, visually reviewed and copied atomically; total size about 720 KB. The requested new set is:

1. `11-dashboard-assist.png`
2. `12-institution-profile.png` (illustrative campus, not a photograph)
3. `13-case-overview.png`
4. `14-ai-case-summary.png`
5. `15-ai-reminder-draft.png`

New set 11-15 uses 25 October 2026 consistently. Refreshed workflow set 01-10 uses 1 December 2026 after clock advancement. AI captures visibly retain the Simulated AI preview label. The institution action fits above navigation; no page overflow/overlap was found. Original SVG workflow diagram remains available. No narrated video was recorded.

## Remaining limits and next task

No implementation blocker remains for the presented frontend path. Photograph retrieval is the explicit fallback limitation; imagery is original local illustration. Official SIH problem statement/ID, reference PPT/PDF and submission format remain unavailable. Existing blueprint gaps (new filing, conditional-approval undertaking creation, general override, production audit/storage/authentication) remain separately documented. The assistant is simulated and cannot send or approve.

Next smallest task: supply the actual PPT/problem statement for a slide-level coverage check and record the documented workflow plus optional 60-90-second assistant segment. Do not restart backend phases or add a real model without a separate scoped implementation task.

---

# Historical status before final verification

# Current status: profiles and simulated AI implemented; browser checks disk-blocked

Added `CampusImage.jsx`, three original campus SVGs, `screens/InstitutionProfile.jsx`, `assistant.js`, `screens/AssistantPanel.jsx` and assistant unit tests. Integrated scoped profiles and AI Assist through More, case overview and case-card thumbnails. Existing workflows, backend, dependency metadata and storage schema are preserved. Assistant answers are deterministic, cited and scoped; no model is running. Copy/retry/loading/unknown-information states and review-only drafts are implemented. Images are labeled illustrations, not photographs; fallback is inline.

Updated FRONTEND_DEMO.md, SIH_DEMO_REVIEW.md, IMAGE_ATTRIBUTION.md and ASSISTANT_DESIGN.md. No TypeScript/framework/chart/icon/animation/AI dependency was installed.

Actual checks: 12 unit tests passed; lint and production build passed (41 modules). Browser test additions and updated screenshots are **unverified**, deliberately deferred because disk free space dropped from ~22 MB to <7 MB. Existing submission screenshots were not overwritten. No downloaded archive or database was removed. Permission to remove only `.local/tools/mongodb.zip` (313,441,273 bytes) was requested and is pending.

Next bounded task: free disk space with approval, run `npx playwright test --config playwright.demo.config.js` in frontend, fix any failures, then opt-in sequential image capture for the institution/assistant journey and visual review. Do not describe the enhanced frontend as fully presentation-ready before those checks. Planned new PNG names 11 through 15 are recorded in FRONTEND_DEMO.md; they do not yet exist as verified deliverables.

---

# Current status: mobile polish implemented; final browser review awaits disk space

## Recovery and changes in this run

Verified `frontend/src/demo/ui.jsx` is complete, with every required shared export intact. Removed only reproducible Python bytecode caches and a zero-byte interrupted documentation temporary file. No source, reference document, submitted screenshot, extracted tool, archive or database was deleted. Downloaded MongoDB ZIP removal is awaiting permission: `.local/tools/mongodb-complete.zip` (805,009,624 bytes) and `.local/tools/mongodb.zip` (313,441,273 bytes).

Changed `frontend/src/demo/demo.css`: navy/blue base, restrained emerald actions, darker secondary text, clear focus outlines, larger header touch targets, coherent SVG sizes and reduced-motion handling. Corrected notification separator text in `screens/Notifications.jsx`. Business logic, backend and localStorage schema are unchanged.

Updated `frontend/tests/demo.spec.js` and `frontend/playwright.demo.config.js`: every test checks console/runtime errors and unexpected API access; added keyboard filter-sheet and case-section checks; default tests produce no screenshots/videos/traces. Opt-in sequential screenshot capture uses 1 December 2026 consistently. Existing submission PNGs remain untouched pending verification. Added small local vector `docs/screenshots/mobile/workflow-overview.svg`; no remote pictures or AI service added.

Updated FRONTEND_DEMO.md with exact recording/reset/capture instructions and SIH_DEMO_REVIEW.md with current source review, coverage evidence, AI/imagery limits and gaps. Correct blueprint re-read in full; official problem statement/ID and reference PPT/PDF remain unavailable.

## Actual checks

- `node --test frontend/tests/demo-service.test.js`: 8 passed (827 ms).
- `npm.cmd --prefix frontend run lint`: passed.
- `npm.cmd --prefix frontend run build`: passed, 34 modules (299 ms before final punctuation-only fix).
- New full browser suite and final PNG capture: **not run in this turn**, deliberately deferred for insufficient disk headroom. Historical browser checks below predate the current visual/test revision.

Disk space fell from 5.6 MB to zero during inspection. Reproducible bytecode-cache removal recovered about 31 MB, still inadequate headroom for reliable browser profiles/captures on a fluctuating full drive. Do not call this revision screenshot/recording ready yet. Next bounded task: approve the two redundant ZIP deletions or free space externally; then run the complete four-test browser suite, fix failures, capture sequentially, inspect every PNG and update this status with actual results. Do not delete database files. Browser test server remains on isolated port 5175.

---

# Latest update: green palette and workspace labels

Changed only presentation styling/copy and matching browser-test selectors. `frontend/src/demo/demo.css` uses forest/emerald colors with dark green primary buttons. DemoApp and screen labels use Workspace, Rules, Evidence and Activity. More > About ClockWork discloses fictional records and simulated actions; messages still truthfully indicate they are not sent, and approval/upload limitations remain. No credentials/login or new navigation was added. Backend, persisted data schema and business rules are unchanged.

Checks: lint and production build passed. All three browser tests reported passing (workflow 7.3s, personas/filters 19.3s, responsive layouts/rules/evidence 4.5s); the runner again stalled in Windows server teardown and was interrupted after test completion. Final footer-copy cleanup was lint/build checked. Existing published screenshots predate this change; current green captures are in frontend/test-results/mobile/ and should be refreshed for the next presentation export.

---

# Current status: mobile SIH presentation demo complete

Updated 2026-10-25. The immediate scope is the standalone React/Tailwind presentation demo, not backend Phase 2. Backend code and stored databases were preserved; no backend service or database was required for these checks. Git metadata is now present; no commits, resets, or pushes were performed. Older status below is historical.

## Changes and working behavior

- `frontend/src/demo/DemoApp.jsx`, `demo.css`, and `ui.jsx`: compact navy app shell, reserved bottom navigation, mobile cards/charts, filter sheets, full-screen record details, and retained navigation/filter state. More contains rules, reports, notifications and separate demo controls.
- `frontend/src/demo/screens/DemoControls.jsx`: shared simulated persona, date, scan and reset controls. The other screen modules adapt case history/actions, EVC scheduling/calendar, evidence/verification, rules, reports and notifications to phone use.
- `frontend/src/demo/model.js`, `service.js`, and `reports.js`: 60 fictional applications across four Regions, 120 linked undertaking/document records, meaningful persona/filter scopes, deterministic 2026-10-25 seed date, calculated notifications and metrics, completed/resubmitted states, and version 3 local persistence. Older saved data is preserved with an explicit improved-seed reset offer; old storage keys remain untouched.
- `frontend/tests/demo-service.test.js`, `frontend/tests/demo.spec.js`, and `frontend/playwright.demo.config.js`: focused service checks and mobile journeys. The test-owned frontend uses port 5175 to avoid disturbing an existing server on 5173.
- README, `FRONTEND_DEMO.md`, `SIH_DEMO_REVIEW.md`, acceptance checklist and migration notes describe the actual presentation scope, sources, walkthrough and limitations. Ten real browser screenshots are in `docs/screenshots/mobile/`.

Return/resubmit preserves remaining configured SLA; scrutiny adds an EVC queue entry once. Scheduling, visit completion and report verification remain distinct. Evidence submission updates officer queues immediately; verification updates counts. Pending lease renewals retain the old expiry until accepted. Six reports, CSV downloads, rule preview/publication, idempotent simulated alerts, scoped personas, reload persistence and reset work locally. All messages, access controls, approvals and uploads are explicitly simulated.

## Commands actually run and results

- `node --test frontend/tests/demo-service.test.js`: **8 passed**, final run approximately 536 ms.
- `npm.cmd --prefix frontend run lint`: **passed**.
- `npm.cmd --prefix frontend run build`: **passed**, 34 modules transformed.
- From `frontend`: `npx.cmd playwright test --config playwright.demo.config.js`: **3 passed in 31.2 seconds** on the final run.

Browser checks used an Edge mobile/touch viewport, not physical phones. They exercised the full walkthrough, all five personas, four Regions, eight committees, every individual filter option, honest combined-filter empty states, back navigation, reload persistence, legacy-data migration, reset, blank reasons, invalid rule preview and immediate dashboard updates. Layout checks covered 360, 390 and 430 px widths, including dialogs, calendar and filter sheet. The journey made no application API requests and reported no page errors. Screenshots were captured at 390 ? 844 and visually reviewed for readable content and navigation overlap. Backend/API-mode tests were not rerun because this scope did not change them.

## Presentation artifacts

`docs/screenshots/mobile/`: `01-today.png`, `02-dashboard.png`, `03-case-timeline.png`, `04-case-escalation.png`, `05-evc-register.png`, `06-undertaking-verification.png`, `07-document-renewal.png`, `08-document-verified.png`, `09-notifications.png`, `10-reports.png`.

See `FRONTEND_DEMO.md` for startup commands and the deterministic five-minute mobile walkthrough. A narrated video has not been recorded.

## Limitations, assumptions and next bounded task

This is browser-local simulation, not production authentication, statutory approval, encrypted document storage, durable audit or external delivery. Uploads store metadata, not document bytes. Published demo timelines are examples, not official policy. Existing production-phase acceptance items remain separate.

The correct supplied blueprint was inspected as DOCX text; the review uses section/paragraph references rather than invented page numbers. No official SIH problem statement/ID or reference PPT/PPTX/PDF was found. `SIH_DEMO_REVIEW.md` maps available requirements and ranks remaining gaps, including new application filing, automatic undertaking creation from a new conditional approval, and general reasoned overrides. Presentation readiness does not establish production readiness or SIH selection.

Next smallest useful task: supply the exact official SIH problem statement (ID/year included) and reference presentation files, reconcile only presentation-critical differences, then record the documented mobile walkthrough. No backend phase is restarted by this task.

---

# Historical status before the mobile redesign

# Current status: completed standalone frontend workflow demo

The user's untruncated presentation requirements are implemented in the existing
React/Tailwind demo. This scope replaces the immediate backend Phase 2 task;
FastAPI, MongoDB, legacy SQL, API-mode screens and dependency metadata were not
changed. No database service was started or accessed. No Git metadata is present
in this workspace, so no commit/diff status is claimed.

## What changed and why

- `frontend/src/demo/model.js` (new): 50 applications / 4 Regions, 25 linked evidence
  records, pinned rule definitions, shared calendar arithmetic and persona scopes.
- `service.js` (extended): v1-preserving upgrade to v2 localStorage; consistent local
  workflow/EVC/evidence changes; pause intervals, rule publication/migration preview,
  unique queue entries, idempotent milestone evaluation and unsent channel messages.
- `reports.js` and `ui.jsx` (new): six scoped report projections/CSV and shared visual
  components. These replace copied calculations in the original single screen file.
- `screens/CaseDetail.jsx`, `EvcRegister.jsx`, `Evidence.jsx`, `RulesReports.jsx`,
  `Notifications.jsx` (new): working screens separated by responsibility.
- `DemoApp.jsx` and `demo.css`: preserved shell/design, wired personas, shared clock,
  reset, navigation, Today/Dashboard, focused upload path and all new interactions.
- `frontend/tests/demo-service.test.js` and expanded `demo.spec.js`: meaningful local
  behavior checks plus the actual five-minute walkthrough and migration/storage tests.
- `playwright.demo.config.js`: bounded longer journey timeout; separate from the
  unchanged API-mode test configuration.
- `docs/FRONTEND_DEMO.md`: reconciliation table, exact timed walkthrough, architecture,
  data ownership, timing, roles, six metric definitions and explicit limitations.
  Acceptance/migration/API/data/auth/timing notes distinguish demo from production.
  Refreshed screenshots are delivered in `docs/screenshots/`.

## Working behavior

All four routes stop at Human decision. Local actions check persona/scope/state
and expected version; EVC queue creation is unique per application. Returns pause
only configured stages, and repeated resubmissions retain remaining active SLA.
EVC scheduling, visit completion, report submission and officer report verification
are distinct. Evidence requires submission and decision reasons; rejection retains
history. Pending renewals leave the old verified expiry effective until acceptance.

Five selectable simulated personas limit visible records and actions, including
reports. Admin cannot perform workflow/verification decisions. Bureau/admin control
the date and scans. Every newly crossed threshold is recorded; channel messages are
coalesced per target/scan and repeated scans add nothing. All channels say not sent.
Focused institution links expose one evidence target with filename-only submissions.
All local edits are saved before changing visible React state; failed writes report
errors. Reset restores data, clock, messages, settings, persona, filters and local tab.

## Actual checks

- `node --test frontend/tests/demo-service.test.js`: **7 passed**, approximately
  205 ms final run. Covers four routes, stale/duplicate actions, persona scopes,
  repeated pauses, nonpausable clocks, due-day boundary, explicit committee assignment,
  report verification boundary, multi-threshold scan idempotency, renewal rejection/
  verification, rule preview/versioning, scoped reports and formula-safe CSV.
- `npm.cmd --prefix frontend run lint`: **passed**.
- `npm.cmd --prefix frontend run build`: **passed**, 33 modules, approximately
  285 kB JS / 32 kB CSS before gzip. No added dependencies.
- From frontend: `npx.cmd playwright test --config playwright.demo.config.js`:
  **3 journeys passed in 13.8 seconds** in the final run, including final screenshot
  regeneration after calendar typography cleanup.
  The full journey asserts no API requests and no page errors. It covers all six
  downloads, reloads, officer/institution/committee actions, pause remaining-time,
  alerts, rules, evidence verification/rejection, migration and storage-write failure.
- Visual review: desktop Dashboard, Case, Notifications, focused upload, mobile,
  and EVC calendar. A calendar glyph encoding problem found visually was fixed
  with HTML arrow entities and empty-day labels before final regeneration.
- One initial service test failed because its fixture retained the wrong committee
  persona from the prior stage; corrected the fixture. The subsequent seven checks
  pass. An accidental root-directory npx invocation was canceled before retrying
  from frontend. No new toolchain or package installation was needed.

## Persistence and migration

New key: `clockwork.presentation.v2`. Legacy v1 IDs/names/dates/history survive
additive upgrade; v1 is not overwritten. A dedicated browser test verifies this and
confirms reset leaves that backup key intact. Use Reset Demo explicitly for the
new deterministic Cedar walkthrough. No application database migration/cutover.
The original API entry remains available with `VITE_APP_MODE=api`.

## Honest limits / next smallest task

This is single-tab browser storage, not secure authentication, multi-user concurrency,
a signed/audited workflow, production file storage or real delivery. Focused links
are public simulated links, not magic-link credentials. File bytes are never retained.
No real policy compliance or source-document authenticity is claimed. No backend
Phase 2 tests/services were run and production acceptance is not marked complete.
The missing historical reference roadmap remains unresolved for later backend work;
it does not block the complete current frontend request.

Next smallest task: rehearse and record the exact five-minute script in
FRONTEND_DEMO.md. A narrated video has not been produced. No implementation blocker
remains for the requested frontend demo scope.

---

## Historical implementation notes (superseded frontend scope)

# Current scope: standalone frontend presentation ? 2026-10-25

User replaced the Phase 2 implementation goal with a polished frontend-only SIH demo. Backend workflow Phase 2 is NOT complete; all existing backend and MongoDB code/data are preserved. No Git metadata exists in this workspace.

Added frontend/src/demo/{service.js,DemoApp.jsx,demo.css}, demo browser tests/config and docs/FRONTEND_DEMO.md. Updated main.jsx to select demo by default; VITE_APP_MODE=api preserves the original App. Existing Playwright config selects API mode and foundation tests. README and migration plan document the additive change.

Working local scope: 50 fictional applications, 4 Regions, all four route types, ranked Today, 30-day strip, four Dashboard filters, shared-data charts, case return/resubmit/complete with local history, EVC queue, undertaking/lease records, filename-only evidence and separate simulated verification, filtered CSV, persistence and confirmed reset. No API requests are made by demo code. Scope limits and walkthrough are in FRONTEND_DEMO.md.

Checks: final lint and production build passed. Both standalone browser journeys passed in 12.9 seconds; see final verification entry below. No backend services or database tests were started for this scope. First browser run exposed test locator/buffer issues, corrected before rerun.

The user message ends at ?Case detail ... curr?; remaining screen requirements are unknown. Next bounded task: reconcile that missing scope with the implemented demo, then record the five-minute walkthrough. Production acceptance items below remain historical, not upgraded by a local simulation.

---

# Project status — 2026-10-25

## Latest architecture review

Reviewed current sources against architecture and the supplied acceptance checklist.
See `ARCHITECTURE_REVIEW.md` for prioritized findings and an end-to-end request trace;
`ACCEPTANCE_CHECKLIST.md` now records the user's actual phase acceptance criteria.

Fixed one bounded defect in `backend/app/modules/auth/service.py`: login/logout
could use stale actor/scope in audit metadata after a concurrent account change.
Fresh transaction identity must now match the identity used for audit arguments;
otherwise 409 rolls back session and audit changes. Existing frontend error handling
shows the retry message and does not treat a conflicting logout as successful.
API/AUTHORIZATION docs describe this added conflict response; data/timing contracts
did not change. This is a foundation correction, not Phase 2 implementation.

Two new tests in `backend/tests/integration/test_foundation.py` reproduced the defect
before the fix (both returned 200 instead of expected 409). After the fix those two,
plus existing cookie/expiry/revocation, audit-failure rollback and five-role isolation
tests passed: **five focused real MongoDB tests, 7.1 seconds**. The command was:

```powershell
.\.venv\Scripts\python.exe -m unittest backend.tests.integration.test_foundation.FoundationTests.test_login_scope_change_cannot_commit_stale_audit_identity backend.tests.integration.test_foundation.FoundationTests.test_logout_role_change_is_retryable_without_false_revocation backend.tests.integration.test_foundation.FoundationTests.test_cookie_csrf_rotation_logout_and_expiry backend.tests.integration.test_foundation.FoundationTests.test_audit_failure_rolls_back_session_and_logout backend.tests.integration.test_foundation.FoundationTests.test_all_roles_and_region_institution_committee_isolation -v
```

Static local import analysis found **no cycles across 44 backend/app modules**.
Remaining findings include malformed-audit verification errors, split effective
deadline/order semantics, absent login limiting, and documented cross-layer ownership
tensions. Browser/build/legacy suites were not rerun in this bounded backend fix;
their earlier results remain historical evidence below. No new framework or database
migration was introduced. Next smallest review fix: malformed audit-entry verification.

## Completed scope

### Prerequisite review for the next phase

An earlier implementation request contains `Phase [NUMBER]`; phase-specific
work remains pending selection. The subsequent architecture review above was
separately authorized and completed. The status, migration plan, API/timing docs and actual
router/auth/obligation/engine/transaction/frontend paths were inspected. No separate
acceptance checklist existed, so the Phase 1 evidence is made explicit below.
The missing roadmap remains unresolved; this review does not invent its contents.

| Phase 1 acceptance item | Evidence / result |
|---|---|
| Validated settings; DB-down liveness/readiness distinction | Both `backend.tests.unit.test_settings` checks passed again in this review |
| Real Mongo lifecycle, indexes and transaction semantics | Previous 11 real Mongo integration tests passed; not rerun in this prerequisite-only review |
| Five-role scope isolation, cookie/CSRF/expiry/revocation | Covered by the previously passed integration suite; actual auth guards/services re-inspected |
| Real/demo clock separation and calendar boundaries | Engine clock/timing inspected; previous real Mongo boundary/security-clock test passed |
| Validated immutable rule versions and shared obligation schema | Rule model inspected; previous versioning/preserving-seed checks passed |
| Atomic domain/audit/outbox persistence | Transaction boundary inspected; previous failure/concurrency tests passed |
| React-to-FastAPI scoped read path | Actual Today/API/router/service path inspected; previous two browser journeys passed |
| Client lint and production build | Both passed again in this review |
| Requirements source reconciliation | Open: requested roadmap file still absent |

No phase implementation, database mutation or API/data/timing behavior change was
made by this review. Next action: select the phase number and bounded scope; the
existing recommendation remains the Phase 2 SCRUTINY_ONLY workflow slice below.

Phase 0 assessment/migration/architecture are written against the corrected Word
blueprint and detailed current task. **Source reconciliation remains open:** the
requested `docs/reference/ClockWork_Codex_Prompt_and_Roadmap.md` was not found in the
workspace, Documents or Downloads. Its location was requested; no answer received
during implementation. This does not block the independent foundation implemented here.

Phase 1 foundation is implemented and verified: MongoDB replica-set lifecycle and
indexes, settings, five-role cookie authentication and scope guards, injected real/demo
time, immutable validated demo rules, shared obligation model and authorized read API,
transactional audit/outbox boundary, explicit preserving seed, and a working React
login -> scoped obligations -> logout path. Admin has read-only published rules.

This is NOT completion of approval/deadline processing on MongoDB. Working SQL
processing remains available through the unchanged legacy entry point. No data cutover,
production deployment, remote push, Git initialization, SQL wipe or user-data import occurred.

## Folder-layout follow-up

Implemented the supplied layout for existing functionality. Source moves were
checked to remain inside the workspace and refused existing destinations. Domains
now live in `backend/app/modules`, with `api`, `core`, `db`, `engine`, development
scripts and separate unit/integration tests. React now uses `app`, `components/ui`,
`features`, `lib` and `styles`. New seed definitions live in root `config`;
`backend/pyproject.toml` and `backend/.env.example` were added. Unimplemented feature
directories remain a documented growth plan rather than empty scaffolding.

Follow-up verification: OpenAPI before/after is identical; dependency metadata
matches direct pins; 11 real Mongo integration tests + 2 DB-independent tests passed
(18.3s), both Playwright browser tests passed, and client lint/build passed. Original
SQL source/tests were not changed or rerun; their discovery still collects 38 tests.
Original API entry points and URL paths remain unchanged. Seed/test commands below
use their new module paths. No schema/data migration was performed.

## Changed files and reasons (current paths)

* `backend/fdr/` was snapshotted in `.local/superseded-fdr-source.zip` and refactored
  into `backend/app/`. Deposit indexes/two-role bearer design were replaced. There
  is no FDR or Flutter code in the active implementation.
* `backend/app/main.py`, `core/{settings,errors,paths}.py`, `api/{router,health}.py`,
  `db/{lifecycle,indexes,transactions}.py`: application
  assembly, validated configuration, pool/index lifecycle, errors, redacted JSON logs,
  liveness/readiness and explicitly disabled scheduler health.
* `backend/app/modules/auth/{routes,schemas,service,repository,guards}.py`: Argon2, opaque
  digest-backed sessions, cookie/CSRF protection, expiry/revocation and five-role scope.
* `backend/app/modules/institutions/{routes,schemas,service,repository}.py`: scoped institution reads.
* `backend/app/modules/obligations/{routes,schemas,service,repository}.py`: common model,
  scope/pagination and separate deadline/evidence/lifecycle views.
* `backend/app/engine/{clock,rules,timing}.py`, `modules/rules/{routes,service,repository}.py`,
  `config/demo_rules.json`: injected business time, shared rule contract, calendar semantics and published versions.
* `backend/app/modules/audit/{service,repository}.py`, `notifications/{schemas,repository}.py`:
  atomic audit head, canonical chain verification and idempotent transactional outbox.
* `backend/scripts/seed.py`: four-route/four-Region synthetic preserving development seed.
* `backend/tests/integration/{test_foundation,browser_runner}.py`,
  `backend/tests/unit/test_settings.py`: real Mongo/browser and DB-independent checks.
* `backend/requirements-mongo.txt`, `requirements-mongo-lock.txt`: separate direct and
  resolved new-runtime pins; legacy dependency files unchanged. `backend/pyproject.toml`
  records matching dependency metadata; `backend/.env.example` owns new runtime settings.
* `frontend/package.json`, `package-lock.json`, `vite.config.js`, `eslint.config.js`,
  `index.html`, `.env.example`: new React/Vite/Tailwind client (previous folder empty).
* `frontend/src/main.jsx`, `src/app/{App,Layout}.jsx`, `src/components/ui/Badge.jsx`,
  `src/styles/index.css`, `src/lib/client.js`, `src/features/auth/Login.jsx`,
  `src/features/today/Today.jsx`, `src/features/rules/Rules.jsx`: shared top bar,
  sign-in, real scoped reads, details, pagination, errors and read-only admin configuration.
* `frontend/playwright.config.js`, `tests/foundation.spec.js`: two real browser journeys.
* `infra/{compose.yaml,start_mongo.ps1,init_replica.py,stop_mongo.py}`: isolated local
  replica-set setup and dbpath-guarded shutdown; Compose is an unexecuted alternative.
* `README.md`, `.env.example`, `.gitignore`: current setup and safe runtime ignores;
  historical SQL instructions/variables retained.
* `docs/{REPOSITORY_ASSESSMENT,ARCHITECTURE,MIGRATION_PLAN,DATA_MODEL,API_CONTRACT,
  RULES_AND_TIMING,AUTHORIZATION,DEMO,PROJECT_STATUS}.md`: grounded architecture/handoff.
* `docs/reference/README.md` and corrected Word file: source provenance/missing roadmap.
  Package `__init__.py` files establish the above modules; no generic interface layer added.

## Actual commands and results

| Command/check | Observed result |
|---|---|
| `git status --short` | Not a Git repository; no diff baseline available |
| `python -m unittest discover -s backend/tests -v` | 38 legacy tests passed, 86.5s; temporary SQL databases |
| `python -m unittest backend.tests.integration.test_foundation backend.tests.unit.test_settings -v` | 13 tests passed on real MongoDB 8.0.28 rs0; final full run 18.0s |
| `python -m backend.tests.integration.browser_runner` | Two Playwright/Edge tests passed against disposable Mongo/API; runner exit 0 and `.last-run.json` passed/no failures |
| `npm.cmd run lint` | Passed |
| `npm.cmd run build` | Passed, Vite 8.3.5; generated production bundle |
| `npm.cmd install` | Pinned packages installed, lock generated; audit reported zero vulnerabilities |
| `python -m pip check` | Passed |
| `python -m backend.scripts.seed` | Succeeded in separate clockwork_demo_local; no SQL migration |
| `audit.service.verify` on local demo | True |
| Blueprint copy comparison | Identical bytes; SHA-256 e0c4037001d37ad5940db5daeb9107adc18ef0d04480fc7d56b6d1c64f8c7d50 |

Mongo tests cover Region/institution/committee isolation, admin denial of operational
scope, no mass assignment, pagination, CSRF, cookie rotation/logout/expiry, real unique
index races, concurrent audit transactions across independent clients, audit/session/
outbox failure rollback, chain edit/missing-entry detection, rule immutability,
preserving seed, local due-day boundary, evidence-vs-deadline separation, demo-vs-security
time, invalid settings and DB-down liveness/readiness. They do not claim future
scan/magic-link/upload/report correctness. Existing SQL tests cover its four routes,
concurrent actions, pauses, version checks and failure atomicity only on the SQL runtime.

Browser test confirms one institution cannot see another Region, cookie survives reload,
no token appears in JS storage/document.cookie, logout revokes access, and admin rules
do not confer operational access. `frontend/test-results/today.png` was visually inspected.
An initial runner had a wrong working-directory calculation; corrected. A sandboxed
browser run stalled on completion and was cancelled, then rerun successfully with
approved browser execution outside the sandbox. Its generated abandoned test DB was
explicitly cleaned; final test-database inventory was empty. A mistyped focused test
selector failed to find a method, then the correct selector passed. No product test
failure is being hidden as a pass.

## Migration state and limits

Original `backend/main.py`, SQL modules/tests/config, starter data and `data/*.sqlite3`
are preserved. The new frontend talks only to `/api/v1` on the Mongo runtime. There
is no automatic SQL-to-Mongo conversion, no dual writes and no claim of data parity.
The local demo Mongo database is separately seeded and its files remain under
ignored `.local/mongo-demo-data`. The API/client started by tests were stopped.
The workspace MongoDB was then gracefully stopped with `infra/stop_mongo.py`;
demo data was retained. Start it again with `infra/start_mongo.ps1` before preview/tests.

Remaining: Mongo workflow transitions; rescrutiny/pause event persistence; scheduler,
scans and fast-forward; real worker/retries; rule editing/simulation; EVC visit actions;
undertaking/document verification; encrypted files and scoped magic links; dashboard,
six exports, communications/case summaries, full audit/access coverage and 40–60-case
rehearsal. Login rate limiting/account administration are also not implemented.
No production readiness claim. Docker/bash, HTTPS deployment and multi-process/load
operation have not been exercised; concurrent independent DB clients were exercised.

## Next smallest useful task

First provide/reconcile the missing roadmap. Then port **SCRUTINY_ONLY filing and
assigned-owner return/resubmit** into the Mongo service using atomic audit/outbox,
idempotency keys and expected versions, preserving baseline due and attempt history.
Add real Mongo parity/concurrency tests before exposing the client action. Do not
port every later screen at once or cut over stored SQL data.

Next prompt: “Read PROJECT_STATUS and the supplied roadmap, reconcile any differences,
then implement only the Phase 2 SCRUTINY_ONLY filing/return/resubmit slice with real
Mongo transaction and authorization tests. Preserve the legacy runtime and data.”

To run the current preview, follow README/DEMO: start the local replica set if stopped,
then `python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8002 --no-access-log`
and `npm.cmd run dev` from frontend. Existing seed is retained; no reset is needed.

## Frontend demo final verification
- npm.cmd --prefix frontend run lint: passed.
- npm.cmd --prefix frontend run build: passed (25 modules).
- npx.cmd playwright test --config playwright.demo.config.js: two browser journeys passed in 8.8 seconds, with no backend API requests and no page errors in the workflow journey. Tested Region count, blank reason, return/resubmit/complete, reload persistence, reset, evidence pending versus verification, CSV download, mobile overflow. Desktop Today/Dashboard and mobile screenshots visually inspected.
- Initial test setup used an incorrect working-directory prefix; corrected before execution. First browser fixtures failed on exact icon labels and upload buffer type; corrected. A sandbox run stalled during shutdown; interrupted only that owned process, then reran outside sandbox successfully.
- All screenshot artifacts are generated under frontend/test-results/. No database reads/writes or backend tests in this run. Backend Phase 2 remains pending by the user's changed objective.


Final regression after adding the stage bottleneck chart: lint and production build passed again; both browser journeys passed in 12.9 seconds. Presentation PNGs copied to docs/screenshots/ so future test runs do not remove the delivered artifacts.


Final delivery: 11 refreshed PNGs copied from frontend/test-results to docs/screenshots. Calendar arrows/empty-day typography visually rechecked after the final browser run. No test servers intentionally left running.
