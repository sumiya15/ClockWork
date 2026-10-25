# Supabase database setup

ClockWork supports Supabase PostgreSQL using SQLAlchemy and psycopg 3.3.6.
Existing FastAPI authentication, password hashes, session cookies, scopes and
workflow endpoints are retained. This is a database migration, not a switch to
Supabase Auth or browser access to database tables.

## Connection and private schema

In your Supabase project's **Connect** panel, copy the PostgreSQL **Session pooler**
connection URL (port 5432). A direct connection also works where IPv6 is available.
Use the database password, not a publishable/anon key. URL-encode special password
characters. Keep the URL local and secret. TLS is required by the backend.

Official references: [Supabase connections](https://supabase.com/docs/guides/database/connecting-to-postgres)
and [SQLAlchemy PostgreSQL](https://docs.sqlalchemy.org/en/21/dialects/postgresql.html).

Tables are created in the private `clockwork` schema, leaving `public`, `auth` and
`storage` alone. Creation revokes schema access from PUBLIC and Supabase's anon and
authenticated roles and enables RLS on each table with no client policies. Use the
schema-owning backend database account; it must be able to create tables and bypass
their RLS as owner. Do not add this schema to Supabase's exposed Data API schemas.
All client access continues through the scoped FastAPI APIs.

## Preserve existing data and switch on port 8001

First configure `CLOCKWORK_DATABASE_URL` in the PowerShell session that will run
the migration and server. The following reads it without displaying or saving the
secret in command history:

```powershell
Set-Location 'C:\Users\sumiy\Documents\ClockWork'
$cwSecret = Read-Host 'Supabase PostgreSQL connection URL' -AsSecureString
$env:CLOCKWORK_DATABASE_URL = [System.Net.NetworkCredential]::new('', $cwSecret).Password
Remove-Variable cwSecret
```

Stop only the ClockWork server on port 8001 before the final copy, so no further
SQLite writes can occur between snapshot and cutover. Leave unrelated servers
alone. Do not initialize or seed the destination first.

```powershell
.\.venv\Scripts\python.exe -m backend.migrate_supabase --source data/clockwork.sqlite3
.\.venv\Scripts\python.exe -m backend.data_cli inspect
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

The migration reads SQLite in read-only mode inside a consistent snapshot and
copies every table, including password hashes, sessions, workflow receipts, audit
history, pauses and the saved demonstration clock. It requires source schema 3
and an empty destination `clockwork` schema. It compares all copied row values
before committing. PostgreSQL DDL and inserts occur in one transaction; a failure
rolls back the destination changes. Existing destination tables cause a refusal,
including on reruns, rather than an overwrite. No source records are modified.

The URL must be present in every new server/CLI PowerShell session. `.env` is not
automatically loaded. An explicit `--db PATH` targets SQLite for local tools;
otherwise `CLOCKWORK_DATABASE_URL` takes precedence over `CLOCKWORK_DB_PATH`.
A configured but invalid/unreachable URL fails rather than falling back to SQLite.

For a new empty demonstration project only, `data_cli init` followed by `data_cli
seed` can initialize PostgreSQL instead of copying the old database. Do not use
that path to preserve existing records or sessions.

## Concurrency and verification limits

SQLite retains its existing writer lock. PostgreSQL uses a transaction-scoped
advisory lock shared by workflow actions, seeding and migration. This serializes
workflow writes so version checks and persisted idempotency receipts retain their
existing semantics. It favors demonstration correctness over high write throughput.
Authentication expiry still uses actual UTC. Stored date values retain their
existing UTC string representation to preserve compatibility.

Tests force isolated SQLite database targets even when a Supabase URL is configured.
Run `.\.venv\Scripts\python.exe -m unittest discover -s backend\tests -v`.
Offline checks cover URL selection, TLS enforcement, PostgreSQL DDL compilation,
transaction-lock selection and read-only migration snapshots. They do not prove
live PostgreSQL connectivity, permissions, migration or HTTP behaviour. Those
checks require the project connection and must be completed before claiming a
successful live cutover. The original SQLite file remains available; do not switch
back to it after remote writes without reconciling those newer records.

## Observed verification, 25 October 2026

- `python -m unittest discover -s backend\tests -v`: 38/38 passed in 79.391 seconds,
  including 34 existing authentication/data/workflow checks and four offline
  PostgreSQL compatibility checks. Test databases and HTTP servers were isolated.
- `python -m pip check`: passed. Existing dependency versions were preserved;
  added psycopg 3.3.6, psycopg-binary 3.3.6 and tzdata 2026.5, recorded in the lockfile.
- Read-only snapshot extraction found all 15 existing application tables.
- Normal SQLite SHA-256 unchanged; existing port-8001 health returned HTTP 200.
- No Supabase connection URL was configured in this session. No remote schema was
  created, no data was sent to Supabase and no running server was switched.
  Live PostgreSQL migration, permissions and HTTP verification remain pending.
