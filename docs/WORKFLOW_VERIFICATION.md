# Approval workflow, returns and resubmission

## Latest reverification: 25 October 2026

The workflow implementation already existed when this request was inspected.
Reviewed the final Word blueprint, README, prior verification reports, models,
schema migrations, authentication, scopes, assignment configuration and tests.
No application behaviour or dependency versions needed changing in this pass.

Executed these Windows commands from the project root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend\tests -v
.\.venv\Scripts\python.exe -m unittest backend.tests.test_workflow -v
.\.venv\Scripts\python.exe -m pip check
```

The first command passed all 13 authentication and 10 data-foundation tests, but
the 11 workflow tests could not bind their hard-coded port 8001 because the normal
application was running there (WinError 10048). No running server was stopped.
Changed the workflow harness to select free temporary ports by default, with an
optional `CLOCKWORK_TEST_PORT` override, and reran the affected workflow suite:
**11/11 passed in 57.308 seconds**. Across these runs, all 34 application tests
passed their assertions; the initial combined command itself exited with errors
from the port collision. Dependency consistency check passed.

The actual HTTP login/file/return/resubmit/complete/history journey ran at
`http://127.0.0.1:53404` against its isolated database and survived server restart.
It verified a three-day pause and final awaiting-authorised-decision state,
with 41 applications, 58 obligations and 49 audit events in that temporary DB.
The test server stopped afterward; this URL is evidence, not a live service.

Read-only HTTP checks confirmed the existing normal application on port 8001
returned healthy status and exposed workflow/action/history routes in OpenAPI.
Before/after SHA-256 checks confirmed the normal SQLite file was byte-for-byte
unchanged. It remains schema 3 with 40 applications, 56 obligations, zero sessions
and zero newly recorded workflow events; foreign-key check returned no violations.
No normal database login, mutation, migration, reseed or reset was performed.
Unrelated servers were untouched. This pass changed only the test harness, README
and this report. Earlier implementation and verification details follow.

ClockWork student demonstration, Windows/Python 3.14.4, 25 October 2026.
The final Word blueprint, repository instructions, actual backend, README and
prior data/authentication verification reports were inspected before editing.
No AGENTS.md was found in the workspace or checked ancestors. Routes, durations,
pause rules and assignments below are unvalidated demonstration settings.

## Implemented behaviour

Institutions can file synthetic applications for their own institution. The server
generates an application ID and submission key, creates one first-stage obligation,
pins its rule version and assigns its explicitly configured owner. An assigned
processing owner can complete or return a stage. Only the owning institution can
resubmit it. Final processing ends at `awaiting_authorised_decision`; there is no
approve, reject or appeal action in this milestone.

Protected workflow responses contain the current stage, version, accountable
owner, pending action, submitted date, current obligation, original due date,
completed pause duration and adjusted due date. Committee users cannot read
another owner's current task merely because they previously handled the case.

## Transition table

| Current state | Action | Permitted actor | Result | Prerequisites/reason |
|---|---|---|---|---|
| No application | file | Institution account with an existing synthetic institution | First configured stage, `in_progress`, version 1 | Supported route, exactly one valid configured owner, valid pinned stage rule, idempotency key |
| `in_progress` | return | Current obligation owner, with the stage's processing role and scoped case access | Same stage, `returned_for_deficiency` | Matching version, meaningful reason, pausable pinned rule, no active pause |
| `returned_for_deficiency` | resubmit | Owning institution only | Same stage and obligation, `in_progress` | Matching version, explanation, exactly one consistent active pause, nondecreasing business time |
| `in_progress`, nonfinal stage | complete | Current obligation owner with the stage's processing role | Correct next stage, `in_progress` | Matching version, reason, no active pause, valid next owner/rule; close current task and create next exactly once |
| `in_progress`, final stage | complete | Current obligation owner with the stage's processing role | `awaiting_authorised_decision` | Matching version, reason, no active pause; no automatic approval |
| Returned or awaiting decision | complete (or any invalid/skipped action) | Nobody | Rejected; no changes | 409 for an invalid state; unknown actions such as approve return 422 |

Every successful action increments the application's workflow version once.
All processing reasons are normalized and must contain at least 10 characters
and eight alphanumeric characters. This is an input-quality check, not proof of
the substantive adequacy of an officer's explanation.

## Action permissions

| Role | File | Complete/return | Resubmit | Read history/workflow |
|---|---|---|---|---|
| Institution | Own institution | Never | Own returned application | Own applications |
| Regional officer | Never | Only owned SCRUTINY task in assigned region | Never | Assigned region |
| Committee | Never | Only explicitly owned EVC/SAC_SHC task | Never | Assigned applications; task metadata/history further restricted to owned tasks |
| Bureau officer | Never | Never from oversight visibility | Never | Cross-region oversight |
| Administrator | Never | Never from administration visibility | Never | Cross-region administration/read support |

The actor is derived from the authenticated cookie session inside the write
transaction, after acquiring the writer lock. User role, scope and assignments are
read from SQLite. Requests cannot supply actor, role, current stage, next stage,
next owner or institution authorization. Extra input fields are rejected. Existing
Origin/JSON/custom-header CSRF protections apply to every workflow mutation.
Hidden direct identifiers return 404; visible but unauthorized actions return 403.

## Routing, assignment and pause assumptions

| Route code | Processing sequence |
|---|---|
| SCRUTINY_ONLY | SCRUTINY |
| SCRUTINY_EVC | SCRUTINY → EVC |
| EVC_SAC_SHC | EVC → SAC_SHC |
| EVC_ONLY | EVC |

The existing `backend/config/demo_rules.json` now includes explicit workflow
assignments. Region A/B/C/D scrutiny uses regional_1/2/3/4.demo respectively.
EVC uses committee_1.demo (DEMO-COMMITTEE-1); SAC_SHC uses committee_2.demo
(DEMO-COMMITTEE-2). Each entry names one actual database user. Duplicate entries,
missing users, wrong roles, wrong regions/committees and unknown rule versions
produce a conflict, not a first-available-user fallback.

`SAC_SHC` remains one unresolved demonstration processing label. This does not
assert SAC and SHC are interchangeable statutory bodies or infer an appeal route.
Authorized policy review must settle the real distinction before operational use.

New stage tasks pin DEMO-RULE-STAGE version 1 with its stored 30-calendar-day
duration. Routes are snapshotted when workflow state is first created; changing
an active route requires an explicit future migration. Existing tasks retain their
stored owner and rule version. Configuration changes only affect creation of a
future task; they never silently reassign the existing task or reset its clock.

Re-scrutiny is re-examination of the SAME obligation after resubmission. Return
records a pause interval; resubmission closes it and accumulates elapsed whole
seconds. The original `base_due_at` does not change. Adjusted due date shown is
base due plus completed pause seconds; while paused, `paused_at` remains visible
and the still-open interval is not yet included in that displayed total. Same-clock
return/resubmission legitimately accumulates zero seconds. Business timestamps
are normalized to whole seconds. Backward demo-clock movement during an action,
inconsistent pause summaries or ambiguous open stage tasks are rejected.

Document/lease expiry, undertaking clocks and unrelated obligations are never
paused or extended by these actions. This records resubmission explanations only;
there is no supporting-file upload. EVC enters an assigned processing task; visit
calendar scheduling and visit/report sub-deadlines are still pending.

Existing illustrative cases get workflow state lazily on their first valid action:
their one open stage obligation is interpreted as the stored current stage. Their
starting workflow version is 0. Inconsistent legacy cases require manual review;
the migration does not fabricate past transitions or rewrite illustrative history.

## Atomicity, concurrency and audit

SQLite `BEGIN IMMEDIATE` serializes competing writers. Each action checks the
submitted `expected_version`, and commits the application, obligations, pause,
audit entry, workflow state and idempotency receipt in one transaction. Failure
rolls them all back. A uniqueness constraint allows only one workflow event per
application version. Generated next-stage obligation IDs are stable per app/stage.

Every mutation requires `Idempotency-Key` (8–128 characters; use a request UUID).
Keys are persisted per actor. Retry/double-click with the SAME key and identical
payload to get the saved receipt with `replayed: true`; this performs no second
transition. Reuse with different content returns 409. An intentionally new key
represents a new request, so filing with a different key creates a new submission.
Clients must retain request keys across retries. A replay returns the original
receipt even if the case has moved later; GET `/workflow` for current state.
Stale versions return 409 instead of applying an old action to a later stage.

New records remain explicitly synthetic. New audit rows use
`generator_version=clockwork-workflow-1` and real session actor IDs/usernames;
seeded illustrative events retain their original labels. `AuditEvent.occurred_at`
is simulated business-event time. Linked `WorkflowEvent.recorded_at` is actual UTC,
and stores the prior/resulting stages and application version. Seed history has
no invented real record timestamp. History includes actor, reason and state changes.
Committee history excludes seed events lacking task linkage and events belonging
to other owners. History totals and pagination use that same scope.

Authentication still uses actual UTC; the demo clock cannot extend a session.
Audit history is ordinary persisted database data, not tamper-proof or hash-chained.

## Reproduce on Windows

Normal application startup (port 8001):

```powershell
Set-Location 'C:\Users\sumiy\Documents\ClockWork'
.\.venv\Scripts\python.exe -m backend.data_cli init
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

Open http://127.0.0.1:8001/docs. No activation or new packages are needed.
`init` performs a backup and migration to schema 3; it does not reset/seed data.
If the updated server is already running on 8001, use it instead of starting a
duplicate. Leave unrelated servers untouched.

Repeat the fully automated isolated HTTP journey, including a three-day simulated
pause and a server restart, while leaving the normal server on port 8001 running:

```powershell
.\.venv\Scripts\python.exe -m unittest backend.tests.test_workflow.WorkflowHTTPTests.test_full_journey_pause_dates_audit_history_restart -v
```

The test owns a temporary DB and its server on a free temporary port only. It never
replaces the server on 8001 or resets the normal database. To explicitly test on
8001 when it is free, set `$env:CLOCKWORK_TEST_PORT = '8001'` before the command and
use `Remove-Item Env:CLOCKWORK_TEST_PORT` afterward. An occupied explicit port is
refused. Earlier results below used the original fixed-port harness; the latest
reverification uses temporary ports to preserve the running application.

## Reproducible manual API walkthrough

This walkthrough creates one synthetic application in the database used by your
running server. For a disposable rehearsal, initialize and seed a separate file,
then start the server with that environment variable (in its terminal):

```powershell
$env:CLOCKWORK_DB_PATH = '.local/workflow-rehearsal.sqlite3'
.\.venv\Scripts\python.exe -m backend.data_cli init
.\.venv\Scripts\python.exe -m backend.data_cli seed
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
# After stopping that server, restore the default for future starts:
# Remove-Item Env:CLOCKWORK_DB_PATH
```

In a second PowerShell terminal, run:

```powershell
$base = 'http://127.0.0.1:8001'
$headers = @{ Origin = $base; 'X-ClockWork-CSRF' = '1' }
$institutionLogin = @{ username = 'institution_1.demo'; password = 'ClockWork-Demo-Only-2026!' } | ConvertTo-Json
$officerLogin = @{ username = 'regional_1.demo'; password = 'ClockWork-Demo-Only-2026!' } | ConvertTo-Json
$committeeLogin = @{ username = 'committee_1.demo'; password = 'ClockWork-Demo-Only-2026!' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$base/api/auth/login" -Headers $headers -ContentType 'application/json' -Body $institutionLogin -SessionVariable institutionSession
Invoke-RestMethod -Method Post -Uri "$base/api/auth/login" -Headers $headers -ContentType 'application/json' -Body $officerLogin -SessionVariable officerSession
Invoke-RestMethod -Method Post -Uri "$base/api/auth/login" -Headers $headers -ContentType 'application/json' -Body $committeeLogin -SessionVariable committeeSession

$headers['Idempotency-Key'] = [guid]::NewGuid().ToString()
$fileBody = @{ route_code = 'SCRUTINY_EVC' } | ConvertTo-Json
$filed = Invoke-RestMethod -Method Post -Uri "$base/api/applications" -Headers $headers -ContentType 'application/json' -Body $fileBody -WebSession $institutionSession
$appId = $filed.application_id
Invoke-RestMethod -Uri "$base/api/applications/$appId/workflow" -WebSession $institutionSession
# Retrying the exact filing with the SAME headers/key/body yields replayed=true.

$headers['Idempotency-Key'] = [guid]::NewGuid().ToString()
$body = @{ expected_version = 1; reason = 'Please clarify the synthetic laboratory details' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$base/api/applications/$appId/actions/return" -Headers $headers -ContentType 'application/json' -Body $body -WebSession $officerSession

$headers['Idempotency-Key'] = [guid]::NewGuid().ToString()
$body = @{ expected_version = 2; reason = 'Laboratory details clarified for this demonstration' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$base/api/applications/$appId/actions/resubmit" -Headers $headers -ContentType 'application/json' -Body $body -WebSession $institutionSession

$headers['Idempotency-Key'] = [guid]::NewGuid().ToString()
$body = @{ expected_version = 3; reason = 'Synthetic scrutiny processing completed by its owner' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$base/api/applications/$appId/actions/complete" -Headers $headers -ContentType 'application/json' -Body $body -WebSession $officerSession

$headers['Idempotency-Key'] = [guid]::NewGuid().ToString()
$body = @{ expected_version = 4; reason = 'Synthetic EVC processing completed by its owner' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$base/api/applications/$appId/actions/complete" -Headers $headers -ContentType 'application/json' -Body $body -WebSession $committeeSession
Invoke-RestMethod -Uri "$base/api/applications/$appId/workflow" -WebSession $institutionSession
Invoke-RestMethod -Uri "$base/api/applications/$appId/history" -WebSession $institutionSession
```

Expected final state: `awaiting_authorised_decision`, version 5, two completed
stage obligations, five new history events. The manual walkthrough holds the demo
clock fixed, so its pause duration is zero. The automated HTTP test advances only
its temporary DB's clock and verifies three days accumulate. No clock-control API
or file-upload feature is claimed. Account credentials remain demo-only.

## Commands executed and verification

Commands executed included `Get-Content`, `rg --files` instruction searches,
ancestor instruction checks, and Python DOCX paragraph extraction. Inline Python
recorded pre-migration table digests/counts, inspected account assignments and
checked port 8001. Application verification commands:

```powershell
.\.venv\Scripts\python.exe -m unittest backend.tests.test_workflow -v
.\.venv\Scripts\python.exe -m unittest discover -s backend\tests -v
.\.venv\Scripts\python.exe -m unittest backend.tests.test_auth.AuthHTTPTests.test_bureau_and_administrator_cross_region_reads -v
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pip freeze
```

Separate reference-kit commands:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s clockwork-data-starter\tests -v
.\.venv\Scripts\python.exe clockwork-data-starter\scripts\evaluate.py
.\.venv\Scripts\python.exe clockwork-data-starter\scripts\import_quality.py
```

Observed result details and final database preservation checks are recorded below.

## Observed application results

The final complete application suite passed **34/34 tests**: 11 workflow HTTP
tests, 13 authentication HTTP tests and 10 data-foundation regressions. Workflow
tests used port 8001 and isolated temporary database copies. Checks covered:

- Own-institution filing, generated unique identifiers, first-stage owner and due.
- All four routes, correct next owners, final awaiting-decision state; no approval.
- Invalid routes, skipped/unknown actions, missing/short/blank reasons and actor
  spoofing rejected. Institution, cross-institution, wrong-region, unassigned
  committee, bureau and administrator mutation denials verified.
- Return/resubmission with a three-day pause, original due date preservation and
  repeated pause accumulation on a seeded case. Its previous three days plus new
  two-day and one-day pauses totalled six days. Document and non-stage obligation
  rows were compared and remained exactly unchanged.
- Missing/duplicated owner mappings, invalid owner roles/committee, missing rule
  version and changed active route all returned 409 with no partial changes.
- Repeated filing/return/resubmission/completion requests produced one saved
  action, even after restart. Changed payload with the same key was rejected.
- Two concurrent filings with the same key produced one app and one replay.
  Concurrent return/completion with the same version produced one 200 and one
  409. Stale requests did not complete a later stage.
- An injected audit-insert failure rolled back the next obligation, application,
  workflow version and idempotency receipt, not merely the audit row.
- Audit actors, reasons, state/stage changes and both time meanings verified.
  Protected history totals/pagination excluded other committee tasks.
- A full login → file → owner return → institution resubmit → scrutiny complete
  → EVC complete → protected history read journey survived a genuine server
  restart on the same temporary database.
- Version-2 migration preserved existing rows and an active session, created one
  backup, and remained idempotent. Version-1 migration regression also passed.

Observed isolated journey counts: **41 applications, 58 obligations, 49 audit
events**, representing one new application, two stage obligations and five actions
in addition to the fixture. The all-route test separately observed **44
applications and 62 obligations**. These temporary records were not copied to the
normal demonstration database.

The initial focused 11-test workflow run passed. The first full regression run
then exposed intermittent Windows/Python test-server shutdown timeouts after
successful HTTP assertions. The test-only runner now bounds Uvicorn graceful
shutdown, disposes the connection pool, flushes logs and exits after `server.run`
returns, avoiding lingering interpreter finalizers. The harness waits for a zero
exit code and does not resend to a closed stdin stream. Identified stale test-only
processes were cleaned up with Windows CIM; no unrelated server was stopped.
The final complete rerun passed without failures. No unresolved check is blocked.

## Separate starter-kit results

The independent starter suite passed **17/17 tests**, rule evaluation **25/25**,
and import quality **12/12** (3 accepted, 1 duplicate skipped, 8 quarantined).
These results concern the offline reference kit. Application workflow evidence
comes from the separate 34-test application suite and real HTTP journey above.
They are not evidence of official AICTE policy accuracy or live integration.

## Normal database and running application

After the tests passed, executed twice:

```powershell
.\.venv\Scripts\python.exe -m backend.data_cli init
```

Migration backup: `data\clockwork.pre-workflow-20261025T092500275801Z.sqlite3`.
The normal DB remains `data\clockwork.sqlite3`. It is now schema version 3 with
three empty workflow support tables. Ordered-row SHA-256 digests and counts of
ALL old tables except the intentionally updated schema marker match the recorded
pre-migration values, including password hashes, sessions and demo clock.

Normal counts remain **40 applications, 56 obligations, 8 institutions, 16 users,
8 documents, 3 rules, 44 audit events, 2 pauses, 0 notifications, 1 demo clock**.
There were 0 sessions before migration and there are still 0; no test logged into
the normal database. Workflow states/events/request receipts remain 0. Foreign-key
check returned no violations. No reseed/reset or demonstration mutation occurred.

Started the updated normal API on **http://127.0.0.1:8001** using `Start-Process
-WindowStyle Hidden` with `-m uvicorn backend.main:app --host 127.0.0.1 --port 8001`.
Launcher PID 10756 is recorded in `.local/workflow-server.pid`; logs are in
`.local/workflow-server.stdout.log` and `.local/workflow-server.stderr.log`.
Actual HTTP requests returned 200 with verified contents for `/`, `/api/health`,
`/docs` and `/openapi.json`. OpenAPI contains the new mutation and history routes.
Anonymous application reads and filing returned 401. No normal DB login or mutation
was needed for these final checks. The existing port-8000 server was untouched.

`pip check` passed; `pip freeze` showed unchanged dependency versions. No package
was installed or upgraded and requirements/lockfile were not rewritten. Final
versions remain Python 3.14.4, FastAPI 0.162.0, Uvicorn 0.54.0, SQLAlchemy 2.1.6.

## Files changed and remaining work

Added `backend/workflow.py`, `backend/tests/test_workflow.py` and this report.
Updated `backend/models.py`, `backend/database.py`, `backend/main.py`,
`backend/config/demo_rules.json`, `backend/data_cli.py`,
`backend/tests/test_auth.py`, `backend/tests/http_server.py` and root README.
The test auth harness gained optional fixed-port/config support and its old
migration expectation now covers schema 3. Existing authentication/scoped-read
implementation and password hashing were preserved. Local ignored DB backup,
digest evidence and runtime logs were created. Kit quality output was regenerated
by the kit command; no fixture or reference database was used as the app DB.

Implemented and verified: human processing workflow, recorded return/resubmission,
explicit owners, pinned rules/dates, atomic history, idempotency and stale-update
protection. Pending: scheduler/deadline notifications, actual delivery, upload and
encrypted evidence storage, frontend, statutory decision actions, live AICTE
integration and tamper-evident audit infrastructure. No regulatory approval or
appeal decision is inferred. This milestone stops here.
