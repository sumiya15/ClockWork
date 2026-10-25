# ClockWork architecture review — 2026-10-25

Scope: current React/Mongo foundation, preserved SQL runtime, reference timing kit,
module imports, documented target architecture and the user acceptance checklist.
There is no Git repository; no baseline diff could be obtained. No dependency or
framework change, data migration or broad rewrite was made.

## Prioritized findings

### 1. Fixed: authentication audit attribution could use stale identity/scope

`backend/app/modules/auth/service.py` assembled audit arguments from the first user
read, before entering `db/transactions.py:mutate`. Login checked the password hash
again inside the transaction but not account identity/role/scope; logout re-read the
session user but discarded that returned identity. If account permissions changed
between reads, a successful session mutation could be logged under old permissions.
Replacing an account under the same username/hash could also mismatch actor IDs.

This is an audit-integrity defect under concurrent account maintenance, not a
demonstrated cross-institution read bypass: reads independently load current scopes.
Account maintenance is not exposed by this phase's public API; external privileged
maintenance can still trigger the interleaving.

Bounded fix: compare `_id`, role, institution, Region and committee from the initial
read with the transaction's fresh user before any session insertion/revocation.
A mismatch returns 409 and rolls back the audit-head reservation as well. Login
does not set a new cookie; logout does not falsely report revocation or clear the
cookie. Retrying resolves against fresh permissions. Existing client error handling
already retains login state on a non-401 logout error and displays the retry message.
The check binds audit metadata to the transaction snapshot; it does not claim to
lock all external privileged user edits after that snapshot.

Two deterministic interleaving regressions failed before the fix (200 instead of
409), then passed on a real replica set. The checks verify no new session/audit/head
commit on conflict, and correct attribution after retry. Three existing auth/scope/
audit-failure checks also passed: five focused tests total, 7.1 seconds.

### 2. Open: malformed audit records can crash verification

`backend/app/modules/audit/service.py:verify` indexes required fields directly.
Deleting `previous_hash` or `current_hash` raises KeyError instead of producing a
failed verification result; non-JSON payload types may fail canonical serialization.
Current tests cover edited values and missing whole entries, not missing fields.
Before exposing verification to operators, return an explicit invalid-chain result
for malformed entries while still surfacing DB availability failures distinctly.
Do not broaden this patch into audit format changes.

### 3. Open: timing is split and paused-record ordering uses a different due value

`backend/app/engine/timing.py:baseline_due` computes end-of-local-calendar-day due
dates. `modules/obligations/service.py:view` separately projects ongoing pauses and
computes severity with a hardcoded seven-day display window. Its repository sorts
and paginates using the stored `active_due_at` BEFORE that projection. A paused item
with a saved earlier due can appear before an unpaused item whose effective deadline
is sooner. The current UI accurately says saved-deadline order; this is not yet the
target time-to-breach-ranked Today view. It matters before pause workflows are enabled.

The preserved SQL `backend/workflow.py:new_obligation` uses start instant + N days,
and its workflow response adds completed pause seconds. The separate reference kit
`clockwork-data-starter/scripts/reference_engine.py` has another instant-based
deadline/escalation calculation. These three implementations are not interchangeable:
SQL/reference instant boundaries differ from the Mongo local-date convention.

No second Mongo workflow transition engine was found: actual transitions currently
exist only in the legacy SQL module. Keep that compatibility code isolated. Before
Phase 2/3, centralize effective-deadline calculations in the existing engine and
define how paused ordering is computed before pagination. Preserve explicitly tested
migration semantics rather than silently importing the reference evaluator.

### 4. Permission review: current read scopes hold; deployment/auth gaps remain

`auth/guards.py:obligation_scope` enforces institution, Region, and committee+assigned
owner constraints. Repositories AND these scopes with allowlisted filters. Mongo
admin is denied operational reads; bureau is oversight-only because no workflow
write endpoints exist. Focused role-isolation tests passed again. No current
cross-institution read bypass was identified in the inspected paths.

`auth/routes.py`/`service.py` have no login attempt limiting; every password request
can incur Argon2 work. This is a known public-deployment prerequisite, not solved by
CSRF or CORS (non-browser clients can send those headers). Keep local-demo deployment
limits until a bounded throttling design exists. Phase 2 action-level permissions
remain absent because those endpoints are absent; do not equate read guards with
approval authority. Legacy `backend/read_api.py` permits administrator oversight,
unlike Mongo admin: do not merge its scope function into the new runtime unchanged.

### 5. No current import cycle; concrete ownership tensions remain

A static AST traversal of 44 local Python modules under `backend/app` found no
local import cycle, including imports inside functions. This is static import
evidence, not a claim about arbitrary future dynamic imports.

* `engine/rules.py` imports `Kind` from `modules/obligations/schemas.py`. The shared
  engine depends on a domain API schema module. If that schema later imports the
  engine, it will create a cycle. Move only the shared obligation-kind contract
  when that reverse dependency becomes necessary; no generic framework is needed.
* `db/transactions.py` coordinates domain audit/outbox implementations, so it is
  an application transaction coordinator rather than generic Mongo infrastructure.
  Its responsibility is documented; a future audit service importing that same
  coordinator would create a cycle. Keep canonical hashing/repositories below it.
* `engine/clock.py:DemoClock` reads checkpoints directly, and `audit/service.py:verify`
  queries Mongo directly. These are concrete exceptions to the stated repository
  boundary. Narrow repository extraction can accompany the next relevant change.
* `institutions/repository.py:assigned_institutions` queries obligations. Its purpose
  is authorization, but ownership crosses domains and materializes an unbounded
  distinct-ID list before paging institutions. Keep the scope restriction; consider
  a scoped aggregation when committee assignments grow.

The main ownership ambiguity is intentional migration coexistence: root `backend/*.py`
vs `backend/app`, and `backend/config` vs root `config`. README/MIGRATION_PLAN name
the active entry points. Existing SQL tests sit directly under backend/tests, while
new unit/integration directories are invoked explicitly; root discovery runs only
the 38 legacy checks. No unexplained empty feature folders were found. Do not remove
the legacy folders until behavioral/data migration acceptance passes.

## Real request trace: scoped obligation page

1. `frontend/src/app/App.jsx` restores the cookie-backed session and selects Today.
2. `frontend/src/features/today/Today.jsx` invokes
   `api('/obligations?limit=10&offset=0')` in its loading effect.
3. `frontend/src/lib/client.js` performs a credentialed GET; `frontend/vite.config.js`
   proxies `/api` to FastAPI on 8002. No Mongo credentials enter the client.
4. `backend/app/main.py` attaches correlation/no-cache headers and uses
   `backend/app/api/router.py` to reach `modules/obligations/routes.py`.
5. `modules/auth/guards.py:current_user` obtains the HttpOnly cookie;
   `auth/service.py:authenticate` calls `auth/repository.py:session_user` to check
   unrevoked real-UTC expiry and the active user's current role/scope in Mongo.
6. `modules/obligations/routes.py` validates pagination/filter types and rejects
   unknown filters. `obligations/service.py:page` obtains the trusted scope;
   `obligations/repository.py:page` ANDs it with filters, queries Mongo and counts rows.
7. `engine/clock.py` supplies business time. `obligations/service.py:view` builds
   validated `ObligationView` objects; `obligations/schemas.py:ObligationPage` is the
   response contract. FastAPI serializes dates and safe fields.
8. The API client resolves JSON; Today stores it via `setPage`, renders scoped cards,
   and renders details from the returned item on selection. The client never grants
   permission or queries Mongo directly.

This browser path passed in the preceding layout verification. This review reran
real Mongo auth/scope regressions, not the browser suite, because the client code
and read API contract did not change.

## Next smallest task

Make audit verification robust to missing/malformed entry fields with focused real
Mongo tamper tests. Then address shared effective-deadline semantics before enabling
Mongo workflow pauses. Neither requires a new framework or broad folder rewrite.
