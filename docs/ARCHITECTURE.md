# ClockWork architecture

## Runtime boundaries

ClockWork is a modular monolith: one React application, one FastAPI process and one
MongoDB database. PyMongo's synchronous client is pooled once per process; FastAPI
runs synchronous handlers in its thread pool. This keeps transaction control flow
readable. Motor is not used. MongoDB must be a replica set for atomic mutations.

`frontend/src/features/` contains auth, today and rules components.
`app/App.jsx` assembles the views and `app/Layout.jsx` owns the shared top bar.
`components/ui/Badge.jsx` is shared presentation; `lib/client.js` is the HTTP client;
`styles/index.css` owns styling. React hooks hold transient view
state; no global state library is needed for this slice. Vite/Tailwind is new because
the original frontend directory was empty. No browser code accesses MongoDB.

`backend/app/modules/` owns the implemented auth, institutions, obligations, audit,
notifications and rules domains. Routes delegate to services and repositories.
`core/` holds settings, errors and repository path resolution. `db/` owns lifecycle,
indexes and the atomic transaction boundary. `engine/{clock,rules,timing}.py` owns
business time, the validated rule contract and date calculations. The rules domain
uses that same contract rather than duplicating schemas. `api/router.py` registers
the routes; `api/health.py` exposes health. `main.py` constructs the app and lifecycle.

`backend/scripts/seed.py` is the explicit development command. `config/demo_rules.json`
is the new runtime's seed definition. `backend/config/demo_rules.json` remains separate
legacy SQL configuration until its cutover; these are different contracts, not two
copies of the new rules. `infra/` owns local MongoDB replica-set setup.

`backend/tests/unit/` contains DB-independent settings/readiness checks;
`backend/tests/integration/` contains real MongoDB and browser integration checks.
Existing SQL tests retain their paths directly under `backend/tests/` so the original
discovery command still runs its 38-test compatibility suite. New test directories
are namespace packages, invoked explicitly by the documented command.

The user-supplied target tree is the growth plan. Applications/EVC/undertakings/
documents/communications/dashboard/reports/demo modules, integrations and workers
will be created when their implementations land. Frontend dashboard/cases/registers/
reports/evidence-upload features are similarly deferred. No reset script or scheduler
placeholder implies those features already work. No provider/router library is
introduced just to fill a folder while the current slice has only session-selected views.

`backend/main.py` and existing flat SQL modules remain a temporary compatibility
runtime. They are not mounted into the new API, and there are no dual writes. Their
removal is gated on workflow parity and a separately reviewed data cutover.
The interrupted FDR source was snapshotted to ignored `.local/superseded-fdr-source.zip`
and its generic foundation refactored into `backend/app/`; no active deposit code remains.

## One real request

1. `frontend/src/features/today/Today.jsx` requests a page after login.
2. `frontend/src/lib/client.js` sends `GET /api/v1/obligations?limit=10&offset=0`
   with browser credentials. Vite proxies `/api` to FastAPI on port 8002.
3. `backend/app/modules/obligations/routes.py` validates allowlisted filters and pagination.
4. `auth/guards.py` and `auth/service.py` load the real session/user through
   `auth/repository.py`; expiry uses actual UTC and scope comes from persisted identity.
5. `obligations/service.py` obtains the role scope and delegates the Mongo query to
   `obligations/repository.py`. The repository ANDs scope with filters, orders and pages.
6. The service uses the injected clock, calculates calendar-date severity, and builds
   `ObligationView`/`ObligationPage` from `obligations/schemas.py`.
7. FastAPI validates/serializes the response. React stores it in component state and
   renders the obligation cards and selected record. It does not decide authority.

Login follows the same layering. Session creation/revocation and the corresponding
audit entry commit together; a failed audit insert produces no successful login/logout.

## Transaction and audit contract

`backend/app/db/transactions.py:mutate` starts a snapshot/majority replica-set transaction. Its
first operation increments the singleton `checkpoints/audit_head`. Competing
transactions conflict on that write, including callers in different processes.
PyMongo retries transient transaction conflicts. Domain operations, notification
jobs and the audit append/head update all use the same session and commit together.
There is no process-local-lock correctness assumption. Retry callbacks must be
deterministic database-only operations; external side effects are forbidden inside.
Later sensitive services must recheck authorization/version inside this callback.

`notification_jobs` is the durable outbox, not a duplicate `outbox` collection.
Its unique idempotency key makes repeated enqueue calls harmless. Phase 1 supplies
the transactional enqueue boundary only; there is no delivering worker or scan.
Phase 3 must implement atomic job claims, lease/recovery, bounded attempts, redacted
errors, and distinguish in-app/simulated channels from actual configured SMTP.

The audit chain scope is the entire database. Canonical bytes are UTF-8 JSON, sorted
keys, compact separators, no NaN, Unicode retained. All fields except Mongo `_id`
and `current_hash` are hashed, including `previous_hash`. UTC timestamps are ISO
strings with microseconds; hashes are SHA-256 hex. Payload is currently empty and
redacted; actor, role/scope, target, reason and correlation ID are explicit fields.
The verifier reads a snapshot and checks hashes, sequence continuity and head.

This detects some edits and omissions. It does not establish source authenticity,
prevent privileged full-chain rewriting, or detect tail deletion if the head is also
rewritten without an independently trusted checkpoint. No public tampering endpoint
exists. Tests only tamper with newly generated disposable test databases.

## Dependency decisions

Checked 2026-10-25 against official documentation/package metadata:

* [MongoDB driver guidance](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/reference/migration/)
  supports synchronous PyMongo for straightforward serial logic; Motor is deprecated.
* [PyMongo 4.19.0](https://pypi.org/project/pymongo/4.19.0/) supports the selected MongoDB 8.0 line;
  [transactions](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/transactions/)
  define retry and atomicity behavior.
* [FastAPI password guidance](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
  uses pwdlib/Argon2; this app uses opaque revocable cookies instead of JWTs.
* [Starlette TestClient](https://www.starlette.io/testclient/) recommends HTTPX2;
  the initial HTTPX deprecation warning was resolved by pinning HTTPX2 2.14.0.
* [Vite](https://vite.dev/guide/) and [Tailwind's Vite plugin](https://tailwindcss.com/docs/installation/using-vite)
  were checked. Node 22.19.0 satisfies the pinned package engines. React 19.3.1,
  Vite 8.3.5, Tailwind 4.3.3 and exact tooling versions are in package.json/lockfile.

Python direct pins are in `backend/requirements-mongo.txt`; the resolved Mongo
runtime/test closure is in `requirements-mongo-lock.txt`. Legacy pins remain separate.
`backend/pyproject.toml` records matching application/test dependency metadata and
Python >=3.14 (the tested runtime). This is a repository-run application, not a
standalone wheel; continue installing with the lockfile. Backend environment
documentation is now `backend/.env.example`; the root template retains legacy SQL
variables only. Environment files are still not automatically loaded.

## Standalone presentation extension
The frontend demo is isolated under frontend/src/demo. model.js owns date/scoping calculations; service.js owns local mutations/scans; reports.js owns shared filters and six projections; screens/ owns individual views. DemoApp commits one serialized localStorage snapshot before updating React state. This is a local demo data path, not a new backend architecture. No API/database call occurs in demo mode. FRONTEND_DEMO.md traces the actual local request and describes limits.

