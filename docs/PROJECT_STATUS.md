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
