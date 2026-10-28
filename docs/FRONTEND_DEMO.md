# ClockWork mobile presentation prototype

## Run

PowerShell:

```powershell
cd C:\Users\sumiy\Documents\ClockWork\frontend
$env:VITE_APP_MODE = "demo"
npm.cmd run dev
```

Open the URL printed by Vite, normally http://127.0.0.1:5173. Keep the terminal open; Ctrl+C stops it. If dependencies are missing, run `npm.cmd ci` first. Python activation, MongoDB and the backend are not needed for this presentation UI.

## Reset and role controls

Open the top-right workspace controls. Select Bureau officer, then Reset workspace and confirm. This resets only this browser's fictional state to 25 October 2026, 60 applications and default rules/persona/filter settings. Do not reset a database. Existing browser records are preserved during upgrades unless the user explicitly resets. Internal keys remain `clockwork.presentation.v3` and `clockwork.mobile.*`; `VITE_APP_MODE=api` still selects the separate API interface.

The top-right role controls select Regional officer/Region, Institution/institution ID, Committee/committee ID, Bureau officer or Admin. These are simulated views, not login. The shared date controls advance +1/+7/+30 days and evaluate reminders without changing the computer clock. Repeated scans do not duplicate records.

## Presentation route

Use Cedar Technical Institute, CW-2026-002 / INST-2 / South. Show scrutiny return/resubmission with preserved SLA, EVC scheduling, an isolated time advance, undertaking verification and lease renewal verification. Screens and exact manual actions are in [VIDEO_SCRIPT.md](presentation/VIDEO_SCRIPT.md). The script is for the user to record; no video was touched during this refresh.

The current UI uses forest-green actions, mint selections, neutral backgrounds, semantic amber/red statuses and compact phone cards. Primary wording is natural; technical provenance and simulation details remain accessible through About this prototype. AI Assist has a Preview indicator and information panel. Its responses are deterministic local templates, not a running model. Notifications say Not sent. File submission stores metadata, not protected file bytes.

## Checks and screenshots only

For a reproducible capture, start an isolated server from `frontend`:

```powershell
$env:VITE_APP_MODE = "demo"
node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5176 --strictPort
```

In a second terminal in `frontend`:

```powershell
npx.cmd playwright test --config playwright.final-presentation.config.js
node tests/presentation-measurements.mjs
node tests/render-architecture.mjs
npm.cmd run lint
npm.cmd run build
```

The final-presentation configuration explicitly disables video and trace and writes test artifacts to `docs/presentation/evidence/green-test-results`. It never uses the old recording configurations or video output directories. The browser tests use isolated contexts; your normal browser state is untouched. Full existing browser regressions use port 5175 (`playwright.demo.config.js`, video off).

See [readiness matrix](SIH_26262_READINESS.md), [screenshot index](presentation/SCREENSHOT_INDEX.md), [architecture exports](presentation/architecture/README.md), [slide content](presentation/PPT_CONTENT.md) and [validation](presentation/VALIDATION.md). All screenshots are 390×844; layouts also checked at 360 and 430 pixels.
