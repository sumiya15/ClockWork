# Setup and foundation demonstration

## Prerequisites and isolation

Verified host: Windows, Python 3.14.4, Node 22.19.0, npm 10.9.3, MongoDB 8.0.28.
Dependencies are pinned. Bash commands below are provided but not executed here.
The demo uses `clockwork_demo_local` at loopback port 27018. It does not read the
existing SQL database or contact AICTE, SMTP, SMS or WhatsApp services.

The local MongoDB archive was downloaded from the official distribution and its
executables extracted under ignored `.local/tools/mongodb/`. This is not committed.
For a fresh Windows machine, download
`https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-8.0.28.zip` and extract
under `.local/tools/mongodb/`, or pass another executable path to start_mongo.ps1.
See [official Windows ZIP instructions](https://www.mongodb.com/docs/v8.0/tutorial/install-mongodb-on-windows-zip/).
The server binds loopback only and has no authentication; do not expose its port.

## PowerShell

From repository root (skip venv creation for the existing environment):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements-mongo-lock.txt
powershell -NoProfile -ExecutionPolicy Bypass -File infra/start_mongo.ps1
.\.venv\Scripts\python.exe infra/init_replica.py
$env:CW_MONGO_DATABASE = 'clockwork_demo_local'
$env:CW_MODE = 'demo'
.\.venv\Scripts\python.exe -m backend.scripts.seed
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8002 --no-access-log
```

Separate terminal: `cd frontend`, `npm.cmd ci`, `npm.cmd run dev`.
Use http://127.0.0.1:5173 consistently; do not mix localhost and 127.0.0.1 cookies.

## Docker alternative and bash

Docker was installed but its daemon was unavailable on this host; Compose execution
is unverified. Do not start Compose while the archive-based server occupies 27018.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements-mongo-lock.txt
docker compose -f infra/compose.yaml up -d
python infra/init_replica.py
export CW_MONGO_DATABASE=clockwork_demo_local
export CW_MODE=demo
python -m backend.scripts.seed
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8002 --no-access-log
# In another terminal:
cd frontend
npm ci
npm run dev
```

The Compose replica advertises loopback:27018, suitable for host-run Python here.
A containerized API or multi-host deployment requires different member hostnames,
authentication/TLS and a reviewed deployment configuration. It is not provided.

## Environment

`backend/.env.example` documents new CW_* settings; root `.env.example` preserves
legacy CLOCKWORK_* variables. Shell variables are used; `.env` is not implicitly loaded. New defaults:
URI `mongodb://127.0.0.1:27018/?replicaSet=rs0`, DB `clockwork_demo_local`, mode demo,
60-minute session, loopback origins 5173, Asia/Kolkata, insecure cookie only for local
HTTP. Real mode requires Secure cookies and a `clockwork_live_*` database; this is
a configuration safeguard, not a claim of production readiness.

`frontend/.env.example` documents VITE_API_BASE_URL (default `/api/v1`). Vite proxies
to port 8002. Change the proxy target if using another API port. For production use
an HTTPS same-origin reverse proxy; never embed DB credentials or private keys in VITE_.

## Short Phase 1 walkthrough

All accounts use the public demo-only password `ClockWork-Demo-Only-2026!`:

* `institution_1.demo` through `institution_4.demo`: one institution each.
* `regional_1.demo` through `regional_4.demo`: one Region each.
* `committee_1.demo`: assigned EVC cases; `committee_2.demo`: SAC/SHC, no active
  assignment in the four-case entry fixture, so an empty operational list is correct.
* `bureau.demo`: all-Region oversight; `admin.demo`: published rules only.

Sign in as institution_1, inspect its single scrutiny obligation and rule/version,
reload to verify the cookie session, then sign out. Sign in as bureau to inspect
four scoped cases. Sign in as admin to read the published four-route configuration.
No role dropdown changes permissions. Today is a read-only foundation preview;
no notification delivery, slider, processing action or statutory decision is faked.

Seed preserves existing edits, hashes and clock. It does not import SQL data.
The final five-minute workflow/fast-forward/verification/export rehearsal is Phase 6.

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest backend.tests.integration.test_foundation backend.tests.unit.test_settings -v
.\.venv\Scripts\python.exe -m backend.tests.integration.browser_runner
.\.venv\Scripts\python.exe -m pip check
# With legacy dependencies also installed:
.\.venv\Scripts\python.exe -m unittest discover -s backend/tests -v
Set-Location frontend
npm.cmd run lint
npm.cmd run build
```

Bash equivalents replace `.\.venv\Scripts\python.exe` with `.venv/bin/python`
and `npm.cmd` with `npm`. Browser tests default to installed Microsoft Edge; adjust
the Playwright channel explicitly if testing another installed browser. Runner
refuses an occupied API port and Playwright refuses an occupied client port.

## Shutdown, backups and storage limits

Stop foreground API/client with Ctrl+C. For the archive server, run
`.\.venv\Scripts\python.exe infra/stop_mongo.py`; it validates the exact workspace
dbpath before graceful shutdown. It retains `.local/mongo-demo-data`. For Compose,
`docker compose -f infra/compose.yaml stop` retains the volume; do not use `down -v`.

Take database backups before any later migration; no automatic backup/retention
service exists. The existing SQLite file/backups were preserved. Mongo transactions
are not backups. Phase 1 has no file bytes or upload endpoints. Phase 4 must add an
encrypted private store, externally supplied keys, authorized access/checksum
recomputation and coordinated DB/file/key backup and retention. Do not mistake a
checksum or a private directory alone for encryption.

## Current SIH frontend presentation
See FRONTEND_DEMO.md for the standalone browser-only demo, its five-minute walkthrough and screenshot checks. The existing backend demonstration instructions below/above are historical and apply only with VITE_APP_MODE=api.

