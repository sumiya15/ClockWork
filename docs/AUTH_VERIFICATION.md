# Authentication milestone verification

Verified on Windows with Python 3.14.4 on 25 October 2026. This report covers the
ClockWork application, not a claim of validated AICTE policy. The final Word
blueprint, README, prior verification report and current code were inspected.
No applicable AGENTS.md was found in the project or checked ancestors.

## Implemented

- `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`.
- Authenticated institution/application lists and details, obligation list, nested
  institution applications and nested application obligations.
- Eight-hour persisted sessions using actual UTC, random 256-bit cookie tokens,
  SHA-256 stored token digests, expiry, login rotation and logout revocation.
- HttpOnly, SameSite=Strict, host-only `/api` cookies. Secure can be enabled for
  HTTPS; it is disabled only for this local HTTP demonstration configuration.
- Existing salted scrypt password hashing reused unchanged.
- Login and logout require an allowlisted exact Origin, JSON content type and
  `X-ClockWork-CSRF: 1`. Cross-site Fetch Metadata is rejected. No CORS grants.
  The header is a non-simple-request CSRF defence, not a secret token. See
  [OWASP's custom-header and origin guidance](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).
- Explicit response models omit password hashes, session tokens/digests and
  internal evidence/storage paths. Validation errors do not echo submitted values.
- Roles/scopes come from the current database user on every request. SQL scope
  predicates apply before filters, ordering, pagination and total calculation.

## Proposed demonstration access matrix

| Role | Institution/application access | Obligation access |
|---|---|---|
| Regional officer | Assigned region only | Tasks in those applications |
| Institution | Own institution and its applications | Own applications' tasks |
| Committee | Only applications containing a task assigned to that user; associated institution summary | Only tasks assigned to that user |
| Bureau officer | All regions for oversight | All regions |
| Administrator | All regions for administration/read support | All regions |

Committee assignment means `obligations.owner_user_id == current_user.id`, with a
nonblank committee scope also required. A committee name does not infer shared
assignments. Access to an institution summary never grants all its applications.
Missing/blank scope grants nothing. Administrator reads do not imply workflow
mutation or user-management APIs. These rules remain unvalidated demo settings.

Direct/nested IDs outside scope return 404, same as absent IDs. Anonymous requests
return 401. List filters outside scope yield zero results. Unknown parameters and
attempted role fields are rejected. Explicit client identity/scope headers are
rejected. Nested parent IDs cannot be overridden through query parameters.

Observed scoped counts from the unchanged demonstration assignments:

| Synthetic account | Institutions | Applications | Obligations |
|---|---:|---:|---:|
| admin.demo | 8 | 40 | 56 |
| bureau.demo | 8 | 40 | 56 |
| regional_1.demo | 2 | 10 | 14 |
| institution_1.demo | 1 | 5 | 7 |
| committee_1.demo | 3 | 8 | 8 |
| committee_2.demo | 4 | 20 | 20 |

## Application checks actually observed

**23 tests passed** in the final complete run: 13 new authentication HTTP tests
and 10 existing data-foundation tests. The latter were updated only where this
milestone intentionally changes public route inventory or anonymous status codes,
and to shut their test server down reliably on Windows.

The auth tests launch real Uvicorn subprocesses with temporary databases and use
Python's HTTP client/cookie jar. They verify:

- Correct login; wrong password and unknown username return identical 401 messages.
- Anonymous denial for all protected list/detail/nested routes and `/me`.
- Cross-institution and cross-region direct ID and filter denial.
- Committee assigned-case access, sibling-case denial within the same institution,
  and exclusion of other owners' tasks from nested records and totals.
- Bureau/admin cross-region oversight and explicit safe output fields.
- Missing/blank scopes deny access. Database role/assignment changes take effect
  in existing sessions without trusting client roles.
- Scoped pagination, totals and filters; invalid limits, offsets, unknown role
  query parameters, client role headers and nested parent overrides rejected.
- Cookie flags, random token rotation, stored digest equality and absence of raw
  cookie tokens from SQLite. Login rotation revokes the previous session.
- Logout clears cookies and revokes server-side sessions; replay returns 401.
- Real UTC creation/expiry, eight-hour lifetime, and expired-session rejection.
- Moving the demo clock to 1990 or 2099 does not change authentication. Rewinding
  it does not revive expired sessions.
- Session remains valid after fully stopping and restarting the server on the
  same temporary database. Session timestamps/digests remain unchanged.
- Missing/untrusted/null/spoofed origins, missing custom header, text/plain and
  cross-site requests fail CSRF checks on login and logout. A failed logout does
  not revoke the valid session. Cross-origin preflight gets no CORS permission.
- HTTPS configuration sets Secure on the cookie.
- Version 1 migration preserves all rows and password hashes, creates one backup,
  upgrades once to version 2 and remains idempotent.

The final restart/expiry HTTP check used `http://127.0.0.1:59462`. The existing
endpoint regression HTTP check used `http://127.0.0.1:58255`. These temporary
servers were stopped; these are evidence URLs, not currently running services.
Cookies, authenticated reads and logout were exercised by the real HTTP suite.
No browser UI rendering or production deployment is claimed.

Initial full test runs failed in Windows cleanup: terminating the venv launcher
left a child server holding SQLite files. A taskkill attempt was unavailable in
the sandbox. Replaced the harness with a test-only stdin shutdown signal that
lets Uvicorn exit normally; this adds no shutdown HTTP endpoint. Stale test-only
processes were identified and cleaned up separately. A final process inventory
confirmed only the original port-8000 server remained. The final full test run
completed with no errors. An initial diagnostic also assumed every FastAPI router
entry had `.path`; checking generated OpenAPI correctly verified the route list.

## Normal database preservation

Before migration, recorded row counts and SHA-256 digests of every existing
table's ordered data. Then ran `data_cli init` twice. The normal database is:

`C:\Users\sumiy\Documents\ClockWork\data\clockwork.sqlite3`

Its schema marker is now version 2 and `auth_sessions` exists, empty. Every
pre-existing operational row, user password hash and saved demo clock is unchanged,
verified against the before-migration digests. No normal database login, reseed,
reset or test edit was performed. Foreign-key check returned no violations.

Backup created before migration:

`data\clockwork.pre-auth-20261025T081828893678Z.sqlite3`

Counts remain 8 institutions, 16 users, 40 applications, 56 obligations, 8 document
metadata records, 3 rules, 44 synthetic audit events, 2 pause intervals,
0 notifications and 1 demo clock. No dependencies were installed or upgraded;
FastAPI 0.162.0, Uvicorn 0.54.0 and SQLAlchemy 2.1.6 remain installed.
`pip check` passed and `pip freeze` matched the existing pinned versions.

## Separate starter-kit checks

- 17/17 starter unit tests passed.
- 25/25 offline rule examples passed, including eight unknown cases.
- 12/12 import-quality expectations passed: 3 accepted, 1 duplicate skipped,
  8 quarantined.

These are independent fixture/reference checks. They do not prove application
login, permissions, workflow, scheduling or notification delivery. Application
authentication evidence comes from the separate HTTP suite described above.

## Exact Windows commands

Commands actually run included:

```powershell
Set-Location 'C:\Users\sumiy\Documents\ClockWork'
.\.venv\Scripts\python.exe -m pip list
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pip freeze
.\.venv\Scripts\python.exe -m unittest discover -s backend\tests -v
.\.venv\Scripts\python.exe -m unittest backend.tests.test_auth.AuthHTTPTests.test_session_survives_process_restart_demo_clock_not_auth_clock_and_expiry -v
.\.venv\Scripts\python.exe -m unittest discover -s clockwork-data-starter\tests -v
.\.venv\Scripts\python.exe clockwork-data-starter\scripts\evaluate.py
.\.venv\Scripts\python.exe clockwork-data-starter\scripts\import_quality.py
.\.venv\Scripts\python.exe -m backend.data_cli init
.\.venv\Scripts\python.exe -m backend.data_cli init
```

Also used `Get-Content`, `rg`, ancestor instruction checks and Python DOCX XML
extraction to inspect source files; inline Python SQLite scripts recorded/compared
table digests and inspected scoped counts. Process inspection and targeted cleanup
used Windows CIM for only identified test servers. Early diagnostic/test commands
were rerun after fixes. No install command was needed.

To start the updated application (the old 8000 process was preserved):

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

Open `http://127.0.0.1:8001/docs`. Follow the complete login/read/logout PowerShell
example in the root README. All synthetic usernames listed there retain the
demo-only password `ClockWork-Demo-Only-2026!`. The shared demo credential is not
suitable for real use. For a different port configure `CLOCKWORK_ALLOWED_ORIGINS`
to its exact origin. Use `CLOCKWORK_COOKIE_SECURE=true` with HTTPS.

## Files changed and remaining scope

Added `backend/auth.py`, `backend/read_api.py`, `backend/schemas.py`,
`backend/tests/test_auth.py`, `backend/tests/http_server.py` and this report.
Updated `backend/models.py`, `backend/database.py`, `backend/main.py`,
`backend/tests/test_data_foundation.py`, `.env.example`, and README.
`backend/passwords.py` received a docstring update only; hashing is unchanged.
The normal database gained only the session table and schema marker update;
the backup and digest evidence are local ignored artifacts. Requirements and
lockfile did not change. Kit quality output was regenerated by its own command.

Completed: backend login/logout/me and role-scoped read APIs. Pending: approval
state machine, mutations, scheduler/deadline engine, notifications/delivery,
uploads/encryption, frontend and live AICTE integration. The audit chain and
comprehensive authenticated-access audit service remain pending. Production auth
hardening such as rate limiting, password reset, MFA and deployment security is
not part of this local demo milestone. No regulatory decisions are automated.
