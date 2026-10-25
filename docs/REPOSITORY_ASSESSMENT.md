# ClockWork repository assessment

Inspection: 2026-10-25, before this run's application changes.

The paths below record the original inspection. The subsequent user-approved
folder layout is implemented for existing features; see ARCHITECTURE and
PROJECT_STATUS for current paths and verification. Legacy SQL paths remain intact.

## Sources and precedence

The current task is authoritative. The corrected supplied file was found at
`C:/Users/sumiy/Downloads/AICTE Hackathon Verdict and Merged Blueprint.docx` and its
complete paragraph/table text inspected. It describes the obligation-based
ClockWork platform and React/Tailwind, with SQL as its original database proposal.
The current instruction explicitly replaces SQL with MongoDB and strengthens
security/audit semantics. `docs/reference/ClockWork_Codex_Prompt_and_Roadmap.md`
was not present; its location has been requested. No claims are made to have read it.
The earlier `docs/ClockWork_Final_Blueprint.docx` describes similar approval flows.
The interrupted FDR guide is superseded; no deposit features belong in this build.

## Existing stack and evidence

* `backend/main.py`: FastAPI assembly, SQL auth/read/workflow routers, `/api/*`.
* `backend/requirements.txt` and `requirements-lock.txt`: FastAPI 0.162.0,
  Uvicorn 0.54.0, SQLAlchemy 2.1.6, psycopg 3.3.6; Python 3.14 in `.venv`.
* `backend/database.py`: SQLite by default; optional private Supabase/PostgreSQL
  schema. Explicit initialization and transactional, preserving migrations.
* `data/clockwork.sqlite3`: existing application data and timestamped backups.
  No user database is modified in this run.
* `frontend/`: empty, no React/Flutter manifest, components, API calls or UI to preserve.
* `backend/auth.py`: persisted expiring cookie sessions, scrypt, CSRF/origin guards.
* `backend/read_api.py`: scoped, paginated institution/application/obligation reads.
* `backend/workflow.py`: four routes, explicit assignments, return/resubmit/complete,
  optimistic versions, idempotency receipts and transactional event recording.
* `backend/config/demo_rules.json`: proposed demo routes/timings/assignments.
* `backend/tests/`: authentication, migration, data and workflow regression tests.
* `clockwork-data-starter/`: separate synthetic reference/evaluation kit; not runtime.
* `backend/fdr/`: unfinished untested modules from the interrupted request. Not
  registered by the working app. Two-role bearer auth and deposit indexes do not fit.

There is no Git repository (`git status` reports not a repository) and no applicable
AGENTS.md was found. Existing files cannot be compared with a Git baseline. The
previous README's running-port claims are historical, not verified running services.
Dependency consistency passed at inspection. Runtime test evidence is recorded
in PROJECT_STATUS after tests, rather than inferred from filenames.

## Concrete structural issues

`workflow.py` combines routing, persistence, schemas and business logic; changes
are harder to isolate. Flat SQL modules are understandable but not domain layered.
Legacy rule definitions are partly read from mutable source config, while pinned
rule rows do not contain the full route/assignment snapshot. The SQL obligation
type collapses stage behavior; separate EVC scheduling/reporting is missing.
Audit previous_hash is reserved, not computed. No frontend exists. The interrupted
FDR subtree introduces incompatible roles and indexes. None of these means the
working SQL workflows should be discarded before parity tests pass.

## Blueprint coverage before this run

| Feature | Evidence/status |
|---|---|
| Five-role authentication and scoped reads | Implemented in SQL auth/read modules |
| Four routes, returns, remaining SLA, version/idempotency guards | Implemented SQL workflow, regression tests |
| Human final decision safeguard | Processing ends awaiting authorised decision |
| Immutable complete rules and simulation/publication | Partial rules; publication UI missing |
| Persisted demo time | SQL clock exists; shared real/demo injection missing |
| Shared obligation engine, scans/why/escalations/outbox | Reference kit only, runtime missing |
| EVC scheduling vs completion/reporting | Missing distinct actions/obligations |
| Undertakings/document validity | Fixture rows only; no verification/renewal workflow |
| Encrypted files/magic links | Missing; evidence paths are fixture metadata |
| Today/dashboard/registers/case/rules/reports | UI missing |
| Communications/reports/integration adapters | Missing runtime features |
| Audit chain/verification | Missing in working SQL application |
| MongoDB persistence | Interrupted foundation only, not verified or seeded |

## Keep/refactor/replace map

| Paths | Decision and reason |
|---|---|
| `backend/main.py`, SQL modules/tests/config | Keep unchanged during Phase 1; working compatibility baseline |
| `data/`, starter kit | Keep; no reseed/reset/import into existing DB |
| `backend/fdr/` | Archive snapshot locally, repurpose generic foundation as `backend/app/`; replace FDR assumptions |
| `frontend/` | Add React/Vite/Tailwind; no existing toolchain to replace |
| `backend/app/*` | Domain routes/schemas/services/repositories for new MongoDB runtime |
| Existing README | Preserve historical instructions; prepend current entry point |
| Existing `.env.example` | Preserve SQL variables; append separate MongoDB settings |

See MIGRATION_PLAN for review gates, compatibility and rollback.
