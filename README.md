# Current presentation entry

The frontend now defaults to a standalone local SIH demo. Start with `cd frontend` then `npm run dev`; no backend or database is required. See [frontend demo guide](docs/FRONTEND_DEMO.md) for walkthrough, reset, screenshots and the preserved API-mode switch. Backend instructions below remain applicable to API mode.

The standalone demo now includes scoped personas, paused/resumed workflows, EVC scheduling and calendar, evidence verification, simulated time/messages, editable demo rules, and six reports. Its exact five-minute walkthrough and browser-local limitations are in the guide above.

# ClockWork — current MongoDB + React foundation

ClockWork is an AICTE approval workflow and deadline-monitoring demonstration.
The current target is React/Tailwind + FastAPI + MongoDB, in one modular monolith.
The corrected blueprint is in `docs/reference/AICTE Hackathon Verdict and Merged Blueprint.docx`.
No FDR/security-deposit or Flutter functionality is included.

The new Phase 1 runtime is `backend.app.main:app` (port 8002); the React client uses
5173. It supports separate development accounts, secure cookie login/logout,
server-scoped obligation/institution reads, immutable demo rules and transactional
audit/outbox foundations. It does not yet expose workflow writes or send notifications.
The original SQL application remains unchanged at `backend.main:app`; its historical
setup follows below. Existing SQL data has NOT been migrated or modified.

## Start the current application (PowerShell)

From this repository root, with Python 3.14 and Node 22.19+:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements-mongo-lock.txt
# Start MongoDB using ONE option in docs/DEMO.md; local archive option:
powershell -NoProfile -ExecutionPolicy Bypass -File infra/start_mongo.ps1
.\.venv\Scripts\python.exe infra/init_replica.py
.\.venv\Scripts\python.exe -m backend.scripts.seed
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8002 --no-access-log
```

Skip venv creation when using the existing `.venv`. In a second terminal:

```powershell
Set-Location frontend
npm.cmd ci
npm.cmd run dev
```

Open http://127.0.0.1:5173. Demo username: `institution_1.demo`; public demo-only
password: `ClockWork-Demo-Only-2026!`. `bureau.demo` sees all four fixture Regions;
`admin.demo` sees published rules and has no operational read authority.
See [DEMO.md](docs/DEMO.md) for all accounts, bash, database installation, clean
shutdown, and the distinction between this four-case fixture and the final demo.

## Checks and handoff

```powershell
.\.venv\Scripts\python.exe -m unittest backend.tests.integration.test_foundation backend.tests.unit.test_settings -v
.\.venv\Scripts\python.exe -m backend.tests.integration.browser_runner
.\.venv\Scripts\python.exe -m unittest discover -s backend/tests -v
Set-Location frontend
npm.cmd run lint
npm.cmd run build
```

Mongo/browser tests require the local replica set; they use generated disposable
databases only. Browser tests require Edge and free ports 8002/5173; stop your own
development API/client first. Legacy tests need the preserved SQL requirements.

Read [PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for actual results/remaining work,
[REPOSITORY_ASSESSMENT.md](docs/REPOSITORY_ASSESSMENT.md),
[MIGRATION_PLAN.md](docs/MIGRATION_PLAN.md), [ARCHITECTURE.md](docs/ARCHITECTURE.md),
[DATA_MODEL.md](docs/DATA_MODEL.md), [API_CONTRACT.md](docs/API_CONTRACT.md),
[AUTHORIZATION.md](docs/AUTHORIZATION.md), and [RULES_AND_TIMING.md](docs/RULES_AND_TIMING.md).

The requested `docs/reference/ClockWork_Codex_Prompt_and_Roadmap.md` was not supplied
in this workspace; reconcile it before extending Phase 2.

## GitHub automatic sync

This project is connected to `https://github.com/sumiya15/ClockWork`. In VS Code,
the **ClockWork: Auto-push to GitHub** task starts when this folder opens (VS Code
may first ask permission to run automatic tasks). After a change has been quiet for
five seconds, the task stages and commits it, then pushes it to GitHub. Keep VS Code
open and connected to the internet for sync to run. If automatic tasks are disabled,
start it from **Terminal → Run Task → ClockWork: Auto-push to GitHub**.

To pause syncing, stop that task in VS Code or press `Ctrl+C` in its terminal. To
turn off startup, remove `runOptions` from `.vscode/tasks.json`. The task refuses
to commit files with names that look like environment files, secrets, keys, or
database files. Git ignores local databases and environment files; the synthetic
reference fixture in `clockwork-data-starter/example` is intentionally included.
The GitHub repository is public: never put real passwords, tokens, private data,
or user records in this project. Review files before adding new kinds of local data.

# Legacy SQL runtime — preserved historical documentation

The following describes the earlier SQL implementation. Running-port statements and
milestone counts below are historical; use PROJECT_STATUS for this run's evidence.

ClockWork is a student demonstration for AICTE approval workflows, deadlines,
EVC activities, undertakings and document validity. The agreed source is
`docs/ClockWork_Final_Blueprint.docx`, copied byte-for-byte from the supplied kit.
All operational data is fictional. Routes, access scopes, pause semantics and
example timelines are unvalidated demonstration settings, not AICTE policy.

## Supabase database

The backend now supports Supabase PostgreSQL through `CLOCKWORK_DATABASE_URL`.
The live cutover requires your project's connection URL; until configured, the
existing port-8001 process continues using its SQLite database. Existing login,
session cookies, scopes and workflow APIs remain the application interface.
Supabase Auth is not used. See [SUPABASE_SETUP.md](docs/SUPABASE_SETUP.md) for the
preserving migration and Windows startup instructions. Do not run `seed` or `init`
on the destination before copying existing data: the migration requires an empty
private `clockwork` schema. Never put the database password in frontend code.

## Windows setup and database commands

Run in PowerShell. No virtual environment activation is required.

```powershell
Set-Location 'C:\Users\sumiy\Documents\ClockWork'
.\.venv\Scripts\python.exe -m backend.data_cli init
.\.venv\Scripts\python.exe -m backend.data_cli seed
.\.venv\Scripts\python.exe -m backend.data_cli inspect
```

`init` creates the application schema and initializes the demonstration clock
once. `seed` uses the canonical `clockwork-data-starter/data/demo/demo_bundle.json`.
It inserts missing identifiers in one transaction, skips existing rows, and
reports differing fields without overwriting edits or password hashes. The clock
is never reset on reruns. Malformed batches are rejected with a reason; no seed
rows are written. A database constraint failure rolls back all seed inserts.
No reset/delete command exists. Existing unrelated/reference databases are refused.
Schema version 3 adds processing workflow state, audit metadata and idempotency receipts.
Version 2 introduced database-backed sessions. Running `init` upgrades version 1
and version 2 transactionally after making timestamped `.pre-auth-*.sqlite3` or
`.pre-workflow-*.sqlite3` backups beside the
database. Existing operational rows, hashes and clock are preserved. Future schema
changes still need explicit migrations.

The application database is:
`C:\Users\sumiy\Documents\ClockWork\data\clockwork.sqlite3`.
It is separate from `clockwork-data-starter/example/clockwork_fixture.sqlite3`.
Never run the kit reference loader against the application database.

Database paths resolve relative to the project root, regardless of the current
working directory. Optional override: `$env:CLOCKWORK_DB_PATH = 'data/other.sqlite3'`
or use `--db 'C:\absolute\path\demo.sqlite3'` on any data command. `.env.example`
documents the variable; `.env` files are not automatically loaded.

From a different directory, use `Set-Location` above, or make the package available
with `$env:PYTHONPATH = 'C:\Users\sumiy\Documents\ClockWork'` and call the virtual
environment Python by its absolute path.

## Inspect safely

`inspect` opens SQLite in read-only mode and prints counts, usernames/scopes,
application summaries, the saved clock and foreign-key violations. It excludes
password hashes and never updates records. For more detail, open a COPY of the
SQLite file in a SQLite viewer in read-only mode. Document entries are metadata;
`evidence_file` is a fixture reference, not a functioning upload or download.

Observed seed counts: 8 institutions (2 per fictional region), 16 users,
40 applications, 56 obligations, 8 document metadata rows, 3 versioned rules,
44 synthetic audit events, 2 pause intervals, 0 notifications. There is one clock
row, initially `2026-10-25T00:00:00Z` (05:30 India time).

Roles: 1 administrator, 1 bureau officer, 4 regional officers, 2 committee users,
and 8 institution users. These store the proposed region/institution/committee
scopes. The authenticated read APIs now enforce the access matrix below.

## Demo credentials and rules

All seeded users have the **demo-only** password `ClockWork-Demo-Only-2026!`.
Example username: `admin.demo`; `inspect` lists the others. This is a public
fictional demo value, never a production credential. Each user gets a random
16-byte salt and a scrypt hash (N=16384, r=8, p=1). Plaintext passwords are not
stored in the database or operational CSV/JSON. Re-seeding does not reset hashes.
**Login, logout and scoped reads are now implemented and HTTP-tested.**
These shared demo passwords remain unsuitable for real operational deployment.

`backend/config/demo_rules.json` stores the four example routes, three versioned
rules, proposed escalation recipients, initial clock and disabled delivery flag.
It must agree with the canonical bundle for initial seeding. Changing a rule is a
future versioned/audited operation, not a reason to overwrite existing rules.
`backend.database.demo_now(session)` reads persisted simulation time without
changing the computer clock. Filing/stage movement now stores a configured due date;
return/resubmission records processing pauses. No scheduled deadline evaluation runs yet.

## Start the API

```powershell
Set-Location 'C:\Users\sumiy\Documents\ClockWork'
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

Open http://127.0.0.1:8001/docs or http://127.0.0.1:8001/.
The updated application is running on port 8001. Use it directly; do not start a
second copy on the same port. Stop a server you started in the foreground with
Ctrl+C. Leave unrelated processes, including the original port-8000 server, alone.

Public `/` and `/api/health` still work. `/docs` and `/openapi.json` also describe
authentication, protected reads and processing workflow routes. No business records
are exposed anonymously. Use the updated application on port 8001.
Health checks server liveness, not database readiness. API startup does not
create, seed or query the database. Swagger browser assets still require internet;
browser rendering/offline Swagger assets have not been tested.

## Verification commands

Application tests use separate temporary databases and a fresh HTTP server on a
free port, then stop only that test process. They never reset the normal demo DB.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend\tests -v
.\.venv\Scripts\python.exe -m pip check
```

Independent starter-kit checks (these do NOT test application workflow logic):

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s clockwork-data-starter\tests -v
.\.venv\Scripts\python.exe clockwork-data-starter\scripts\evaluate.py
.\.venv\Scripts\python.exe clockwork-data-starter\scripts\import_quality.py
```

Observed on Windows/Python 3.14.4: 34 application tests passed (11 workflow HTTP
tests, 13 authentication tests and 10 data-foundation regressions); 17 kit tests passed;
25/25 offline rule specification examples and 12/12 import-quality examples passed.
Quality outcomes: 3 accepted, 1 skipped duplicate, 8 quarantined. These are crafted
synthetic examples, not measurements of real-world or AICTE policy accuracy.
See `docs/WORKFLOW_VERIFICATION.md` for current workflow results and commands.
`docs/AUTH_VERIFICATION.md` records the preceding authentication milestone.
`docs/DATA_FOUNDATION_VERIFICATION.md` is the historical prior-milestone report.

## Dependencies

FastAPI 0.162.0 and Uvicorn 0.54.0 were preserved. Only SQLAlchemy 2.1.6 was added.
Its official [PyPI release metadata](https://pypi.org/project/SQLAlchemy/2.1.6/)
includes a CPython 3.14 Windows x64 wheel, which installed successfully.
`backend/requirements-lock.txt` records the installed environment; `pip check`
passed. For a future clean setup (not needed for the existing working .venv):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-lock.txt
```

`.gitignore` excludes virtual environments, database/journal files, local logs,
secrets and runtime output. No Git repository has been initialized.

## Pending

Implemented: authenticated filing, processing-stage completion, returns, resubmission
and protected workflow history. Next milestone: the deadline engine. Scheduler, actual
notifications/delivery, file uploads, encryption, protected audit append/hash
chaining, React/Tailwind frontend and live AICTE integration remain pending.
Synthetic history is not tamper-proof. Public sources remain a separate research
catalog; application startup makes no AICTE/public-service requests. Human
scrutiny, verification and statutory decisions must remain with authorized users.


## Authentication and read API milestone

Start the updated API in a PowerShell terminal (leave this terminal running):

```powershell
Set-Location 'C:\Users\sumiy\Documents\ClockWork'
.\.venv\Scripts\python.exe -m backend.data_cli init
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

Open http://127.0.0.1:8001/docs to inspect schemas. The protected routes need a
session cookie. Use this exact example in a second PowerShell terminal:

```powershell
$base = 'http://127.0.0.1:8001'
$headers = @{ Origin = $base; 'X-ClockWork-CSRF' = '1' }
$login = @{ username = 'institution_1.demo'; password = 'ClockWork-Demo-Only-2026!' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$base/api/auth/login" -Headers $headers -ContentType 'application/json' -Body $login -SessionVariable cwSession
Invoke-RestMethod -Uri "$base/api/auth/me" -WebSession $cwSession
Invoke-RestMethod -Uri "$base/api/institutions" -WebSession $cwSession
Invoke-RestMethod -Uri "$base/api/applications?limit=2&offset=0" -WebSession $cwSession
Invoke-RestMethod -Uri "$base/api/applications/DEMO-APP-001/obligations" -WebSession $cwSession
Invoke-RestMethod -Method Post -Uri "$base/api/auth/logout" -Headers $headers -ContentType 'application/json' -Body '{}' -WebSession $cwSession
# This request must now fail with HTTP 401:
Invoke-RestMethod -Uri "$base/api/auth/me" -WebSession $cwSession
```

Other synthetic usernames: `regional_1.demo` through `regional_4.demo`,
`institution_1.demo` through `institution_8.demo`, `committee_1.demo`,
`committee_2.demo`, `bureau.demo`, `admin.demo`. All use the existing demo-only
password above; seeding has not changed any hashes. `data_cli inspect` lists scopes.
No role dropdown, header or query parameter can change the database user's role.

### Proposed demonstration access matrix

| Role | Institution and application reads | Obligation reads |
|---|---|---|
| Regional officer | Institutions and applications in the assigned region | Tasks for those applications |
| Institution | Own institution and its applications | Tasks for own applications |
| Committee | Applications with at least one task whose `owner_user_id` is this user; associated institution summary only | Only tasks assigned to this user |
| Bureau officer | All regions for oversight | All regions for oversight |
| Administrator | All regions for prototype administration/read support | All regions; no workflow mutation permission implemented |

A committee name alone grants no case access. Membership sharing is deliberately
not inferred: assignments belong to individual committee users in the current
schema. An assigned case never grants access to its institution's other cases.
Missing/blank scope denies access. These are demo rules, not validated AICTE policy.

Routes:

- `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`.
- `GET /api/institutions`, `GET /api/institutions/{id}`.
- `GET /api/applications`, `GET /api/applications/{id}`.
- `GET /api/obligations`.
- `GET /api/institutions/{id}/applications`.
- `GET /api/applications/{id}/obligations`.

Lists return `items`, scoped `total`, `limit` (1-100, default 50) and `offset`
(nonnegative). Ordering is stable by ID. Institution filters: `region`.
Application filters: `institution_id`, `region`, `stage`, `status`. Obligation
filters: `application_id`, `institution_id`, `status`, `owner_user_id`.
Nested routes fix the parent ID; a query cannot override it. Filters only narrow
scope; forbidden direct/nested parents return 404, and lists outside scope return
zero results. Anonymous protected requests return 401. Unknown filters return 422.

### Session and CSRF behaviour

Sessions last eight hours from **real UTC** login time. Advancing or rewinding the
demo clock does not affect them. A fresh cryptographically random 256-bit token
is stored only in an HttpOnly, SameSite=Strict, host-only cookie scoped to `/api`.
Only its SHA-256 digest is persisted. Tokens are never returned in JSON. Login
rotates/revokes an existing cookie session; logout revokes it in SQLite and clears
the cookie. Database roles/scopes are read anew on each request. API responses use
`Cache-Control: no-store`. Password hashing reuses the existing scrypt code.

Login AND logout require an exact allowed `Origin`, `X-ClockWork-CSRF: 1`, and
`Content-Type: application/json`. Missing/null/untrusted origins and cross-site
Fetch Metadata are rejected. This uses custom-header CSRF protection with origin
checking, not a secret CSRF token. No cross-origin CORS permissions are enabled.
The PowerShell example intentionally sends these headers; Swagger's default
Try-it-out does not supply the custom header automatically.

For a different local port, configure its exact origin before starting the server:

```powershell
$env:CLOCKWORK_ALLOWED_ORIGINS = 'http://127.0.0.1:8002'
```

Defaults allow localhost/127.0.0.1 ports 8000 and 8001. Origin values are explicit,
not derived from untrusted Host/forwarded headers. `.env.example` is documentation,
not an automatically loaded file. Cookies omit Secure only for loopback HTTP demo
use. Set `$env:CLOCKWORK_COOKIE_SECURE = 'true'` when using HTTPS. Keep this demo
bound to loopback. Production hardening (rate limiting, password reset, MFA,
transport deployment and auth/audit operations) is outside this milestone.


## Processing workflow milestone

The four configured routes now support institution filing and assigned-owner
processing. Final-stage completion produces `awaiting_authorised_decision`, never
regulatory approval. Bureau/admin read access grants no processing authority.
Rules, calendar-day durations, assignment mapping and the combined `SAC_SHC` label
are demonstration assumptions, not verified AICTE procedures.

- `POST /api/applications`: body `{"route_code":"SCRUTINY_EVC"}`; institution is
  derived from the logged-in user. App ID and submission key are server-generated.
- `GET /api/applications/{id}/workflow`: current stage, version, accountable owner,
  pending action, original due date, completed pause seconds and adjusted due date.
- `POST /api/applications/{id}/actions/return`, `/resubmit`, `/complete`: body
  `{"expected_version":1,"reason":"A meaningful processing explanation"}`.
- `GET /api/applications/{id}/history`: scoped, paginated history, actor, reason,
  previous/resulting state and stage, simulated business time and actual UTC
  record time. Committee history includes only events tied to its assigned tasks.

Every mutation needs the existing Origin/JSON/CSRF headers plus
`Idempotency-Key: <unique request UUID>`. Save and reuse the SAME key and payload
when retrying a request or double-click; a new key intentionally represents a new
request. Keys are persisted per actor. Reusing a key with different content gives
409. Successful retries return `replayed: true` and the original receipt, which
may describe an earlier state; GET `/workflow` for current state. A stale
`expected_version` also gives 409; reload instead of overwriting another action.

Explicit assignments in `backend/config/demo_rules.json`: scrutiny uses the
region's named regional officer, EVC uses committee_1.demo, and SAC_SHC uses
committee_2.demo. Missing, duplicated or invalid assignments cause a conflict
without partial changes. Existing obligations retain their recorded owner.

Returns pause only the current stage. Only its institution can resubmit, with an
explanation. Re-scrutiny means re-examining the SAME stage obligation: its original
due date stays unchanged and completed pause duration accumulates. It gets no new
full processing period. Document/lease expiry and unrelated obligations do not
change. No supporting-file upload is implemented.

New workflow audit entries use `generator_version=clockwork-workflow-1` while
retaining synthetic provenance; seed history retains its original generator.
Actual UTC record time is additional metadata, not invented for historical seed
events. Audit storage is not tamper-proof. The saved demo clock drives business
events; real UTC still drives authentication expiry.

See [WORKFLOW_VERIFICATION.md](docs/WORKFLOW_VERIFICATION.md) for transition and
permission tables, the full reproducible API walkthrough and observed checks.
The focused HTTP journey is repeatable without changing the normal database:

```powershell
.\.venv\Scripts\python.exe -m unittest backend.tests.test_workflow.WorkflowHTTPTests.test_full_journey_pause_dates_audit_history_restart -v
```

Workflow tests use free temporary ports by default, leaving the updated application
on **port 8001** running. They create isolated temporary database copies, start/stop
their own server via private stdin, and remove their temporary databases. Optional
`$env:CLOCKWORK_TEST_PORT = '8001'` reserves that port for a test only when it is
free; an occupied port is refused. Remove that variable afterward with
`Remove-Item Env:CLOCKWORK_TEST_PORT`. Application startup never seeds or resets a
database. Run `data_cli init` explicitly for the safe migration.
