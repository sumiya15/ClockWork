# Standalone SIH frontend demo

The default React/Tailwind application is a complete browser-local presentation
workspace. FastAPI and MongoDB are preserved but not required or contacted by demo
mode. This work does **not** implement backend Phase 2.

## Start and reset

PowerShell or bash, from the repository root:

```text
cd frontend
npm ci
npm run dev
```

Open http://127.0.0.1:5173. Installed dependencies were reused in this run; `npm ci`
is a reproduction instruction, not a claimed check. No packages were added.
`npm run build` produces the static bundle; `npm run preview` serves it locally.
Do not open index.html directly as a file. Initial dependency installation needs
network access; the running demo requires no external fonts, images or services.

**Reset Demo** asks for confirmation and restores all 50 applications, 25 evidence
records, EVC records, clock, notifications, milestones, history, rules and persona
settings. The starting date is **25 October 2026**; persona is **Bureau officer**.
Regional scope defaults to South, institution to Cedar Technical Institute
(INST-2), and committee to South EVC Committee.

The original API-backed interface remains selectable:

- PowerShell: `$env:VITE_APP_MODE='api'; npm run dev`
- bash: `VITE_APP_MODE=api npm run dev`

It still requires the original backend setup. Unset the environment variable, or
set it to `demo`, to return to standalone mode. API-mode backend/browser checks
were not rerun for this frontend-only change.

## Requirements reconciled against the previous demo

| Area | Previously observed gap | Current behavior |
|---|---|---|
| Case | Returns only changed status; no ladder/communications | Configured pause/resume, remaining SLA, repeated history, pinned route, owner, factual summary, milestone ladder and local communications |
| EVC | Filtered list only | Unique queue item, explicit committee assignment and visit date dialog, separate visit/report states, officer report verification, month grid and list |
| Evidence | Filename submission and accept only | Required submission/decision reasons, rejection and retry, issue/expiry validation, pending renewal, old verified validity and renewal/submission history |
| Rules | Read-only text | Admin editing of timelines, pauses, offsets, escalation thresholds and known-stage routes; validation, preview and versioned publication |
| Reports | One portfolio CSV | Six reports using shared persona, Region/stage/institution/owner and inclusive submission-date filters |
| Access | One review persona | Five clearly simulated roles, scope-limited records/exports and service-level action checks |
| Clock/messages | Fixed date, no scanner | +1/+7/+30 days, shared calculations, idempotent milestone scan, three explicitly unsent channels and readable why lines |
| Institution page | None | Target-only local reminder page; submission updates its register, Today verification queue and activity |

## Exact five-minute walkthrough

Use a fresh **Reset Demo**, a desktop viewport around 1440x1000, and a small fictional
PDF/PNG/JPG (nonempty, at most 5 MB). No real institution or personal files.
The main case throughout is **CW-2026-002 / Cedar Technical Institute / South**.

| Time | Presenter steps | Expected result / narration |
|---|---|---|
| 0:00–0:35 | Open **Dashboard** as Bureau. Choose South, then Clear filters. | 50 applications across 4 Regions; South has 13. Charts and KPIs derive from the same scoped cohort. |
| 0:35–1:15 | Choose **Regional officer** (South). Open Applications, search `CW-2026-002`, open Cedar. Enter `Clarify laboratory equipment capacity.` and **Return with reason**. Switch to Bureau and click **+7 days**. Reload. | Date is 1 Nov 2026. Scrutiny is paused; the original **5 days remaining** stays unchanged. Reload retains state. |
| 1:15–1:40 | Switch to **Institution**, default Cedar. Enter `Equipment capacity clarified.` and **Resubmit application**. Switch to Regional officer. Enter `Scrutiny checklist reviewed.` and **Complete stage**. | Resume retains five days, shifts the scrutiny due date to 6 Nov and records one resubmission. Completing scrutiny creates exactly one EVC queue item. |
| 1:40–2:10 | Click **Open EVC actions**. In Cedar's highlighted card, **Schedule visit**. Choose **South EVC Committee**, date **2026-11-02**, reason `Committee availability confirmed.` Confirm. Select Calendar and 2 Nov. | One assigned visit appears on the month grid. Scheduling is Scheduled, visit Pending, report Pending. |
| 2:10–2:40 | Switch to Bureau. Click **+30 days**, then **Run reminder scan** once more. Open Cedar case. | Date is **1 Dec 2026**. Visit is 29 days overdue. All 1/7/14-day escalation milestones are recorded; repeating scan does not increase message count. Each message explains its rule, due date, observed date and threshold; none was sent. |
| 2:40–3:05 | Switch to **Committee** (South EVC Committee), open EVC actions. **Complete visit** with reason, then **Submit report** with reason. Switch to Bureau and **Verify report** with reason. | Separate visit, report submission and officer verification actions. Cedar reaches **Human decision**, never automatic approval. |
| 3:05–3:40 | Open Notifications, channel email. In **Cedar laboratory equipment undertaking**, click **Open simulated reminder link**. Select fictional file, enter submission reason, Submit evidence. Use browser Back or open `/#today`. Open the Cedar undertaking action. As Bureau, enter `Evidence matches the undertaking.` and **Verify evidence**. | Focused page exposes only its target. Submission immediately enters the officer verification queue. Verification makes the undertaking Compliant. |
| 3:40–4:20 | Open `/#upload/REG-DEMO-L` (also available through Cedar's lease message/register link). Submit fictional file with issue **2026-12-01**, expiry **2027-12-01**, and reason. Return to `/#registers/REG-DEMO-L`. | Lease still shows **Expired**, verified expiry 23 Oct 2026, and pending proposed expiry. As Bureau, enter a verification reason and **Verify evidence**. Only now does validity become Valid; history retains the old dates. |
| 4:20–5:00 | Reload to show persisted verification. Open **Rules & reports**, select **Document validity**, download CSV. Open Cedar case timeline or Notifications → Demo activity history. | Reports, registers and timeline reflect the same changes. Point out explicit simulated access and unsent messages. Finish on Dashboard or Case for screenshots. |

Optional short extension: as Admin, change Scrutiny days to 21. Select explicit
migration, Validate & preview, inspect all proposed targets, enter a publication
reason, and Publish previewed demo version. Invalid values fail validation; editing
again invalidates the preview. Changes to time/data require a fresh preview. Reset
before repeating the scripted journey.

## Calculation and workflow conventions

- Business time is one date-only value, starting 2026-10-25. It represents demo
  calendar dates in Asia/Kolkata; no business-day/holiday adjustments. UTC parsing
  is only an implementation technique to avoid browser timezone/DST differences.
- The due day is allowed: `remaining = due date - today`. Zero is Due today;
  negative is Overdue. Leases remain valid through their expiry date. 0–30 days
  to expiry is Expiring; more than 30 is Valid; negative is Expired.
- A stage starts at its preceding human action. The rule's duration sets its next
  due date. EVC scheduling creates a distinct visit stage due on the explicitly
  chosen visit date. Completing the visit starts the configured report allowance.
  A submitted report remains pending until officer verification advances the route.
- Default scrutiny and SAC/SHC stages pause on return; EVC does not. A paused
  stage's effective target moves by elapsed pause dates, so its remaining SLA is
  frozen. Resubmission adds exactly that pause duration to the stored target.
  Repeated cycles preserve remaining allowance, completed intervals and attempts.
  Returning an already overdue item does not grant it extra active time.
- Active stage days exclude pause intervals. `pausedDays` is for the **current**
  stage; historical intervals remain separately visible after stage completion.
  Initial seeded in-flight stages use the supplied submission date as their
  illustrative stage-start baseline; no historical completion metrics are invented.
- Every application holds a published rule version. Editing/publishing without
  migration does not retroactively change it. An explicit, reasoned migration
  updates case rule references, calculated targets and register reminder versions.
  The preview lists all 50 affected targets, preserves scheduled visit dates, and
  rejects removal of current/traversed stages or an ongoing pause's pause setting.
- Human decision is the terminal workflow destination, not automatic approval.
  This demo provides no statutory approve/reject action.

## Notifications and history

Bureau/admin can advance time and run the **same** evaluator manually. There is
no wall-clock scheduler, background worker or delivery adapter in standalone mode.
Initial messages are empty until a scan or time advance.

A milestone key contains target ID, stage/validity revision, rule version and
threshold. The first scan catches up all already-reached thresholds. A multi-day
jump records **every** newly crossed threshold, then emits only the latest newly
crossed threshold per target per channel for that scan. Email, SMS and WhatsApp
all say **Simulated — not sent**. Repeated scans at the same date add nothing.
Paused application stages are not scanned; independent leases/undertakings still
are. Pending or rejected evidence never clears a deadline. Accepted undertaking
and renewed-lease messages become historical/resolved without deleting history.

Each why line states DEMO-CW version, target, due date, current simulated date,
observed elapsed days and threshold. Case communications show the latest nine
messages; the notification panel provides the full history in batches of 30,
channel filters and current-only filtering. Milestones and local action events
are stored separately, including actor label, business date and real UTC time.
This is **not** an authenticated, tamper-evident audit log. No policy quotations
or authenticity claims are fabricated.

## Simulated access matrix

| Persona | Visible scope | Local actions |
|---|---|---|
| Regional officer | Selected Region | Scrutiny return/complete, EVC scheduling and report verification, evidence verify/reject |
| Bureau officer | All Regions | Same officer actions across Regions; clock and scan |
| Committee | Explicitly assigned EVC cases or current SAC committee stage | Return/complete its assigned stage, complete due visits and submit reports; no report/evidence verification |
| Institution | Selected institution only | Resubmit returned application, submit its evidence; no officer decisions |
| Admin | All demo records and settings | Validate/preview/publish/migrate demo rules; clock/scan; no workflow or evidence decisions |

Visible controls and mutation functions both apply this matrix. Exports use the
same read scope. This remains an intentionally selectable presentation persona,
**not authentication**. All source/data is in the browser, so it is not a security
boundary. The focused reminder URL is deliberately a **public simulated link**,
not a token, login, secure magic link, revocable credential or real delivery.
It permits only target evidence submission in that page; events identify the
simulated institution link even if opened from an officer's presentation persona.

## Evidence rules

A file selection stores only filename, size, dates and reasons. It does not read,
retain, upload, encrypt, scan, hash or download bytes. Extension/size checks are
presentation input validation, not file content validation. Use fictional files.

Evidence submission, officer verification and rejection are separate actions.
Blank reasons are rejected. Pending submissions cannot be overwritten; rejected
submissions may be retried. A renewal's issue date must be on/before today, and
its expiry after issue, today and the existing expiry. Until acceptance, the old
verified dates govern the red/amber/green validity state. Acceptance appends the
old verified record to renewal history and records the evidence decision; rejection
leaves the old verified validity unchanged. Submission/decision history is retained.

## Six reports and metric definitions

All filters apply before aggregation: persona read scope, Region, current stage,
institution, current officer/committee and inclusive **application submission**
date range. Date filters use the same basis even for linked registers.

1. Application pendency: open case, current stage/state/owner, active target,
   remaining days and active elapsed stage days.
2. EVC status: scoped visit rows, assigned committee/date, scheduling, visit and
   report statuses. Concluded EVCs are explicitly labeled.
3. Undertaking compliance: due date, evidence/verification state and computed
   pending/overdue/compliant status.
4. Document validity: verified issue/expiry, pending proposed expiry, current
   validity and count of historical validity versions.
5. Overdue cases: overdue application stages and independent overdue register
   targets; pending evidence is not excluded, verified undertakings are excluded.
6. Region-wise processing performance: **Region + stage** cohorts, open sample n,
   overdue n, mean open active stage days, separate completed-stage sample n and
   mean completed active days. No completed observations means Insufficient data.

Dashboard ageing is calendar time since submission (including clarification);
stage workload is open assigned applications; bottlenecks are overdue counts,
not causal diagnoses or officer ratings. No ungrounded “AI prediction” is used.
CSV output quotes cells and neutralizes formula-like prefixes, including leading
whitespace. All six reports are previewable and downloadable even for an empty
cohort (headers only). Invalid date ranges disable export.

## Code ownership and persistence

- `frontend/src/demo/model.js`: deterministic seed, stage/route vocabulary, shared
  date calculations, pinned rule lookup and simulated persona/action scope.
- `service.js`: additive v1 upgrade, v2 persistence, workflow/EVC/evidence mutations,
  notifications, rule validation/preview/publication and local activity events.
- `reports.js`: one filter pipeline, six report projections and CSV generation.
- `ui.jsx`: shared presentation primitives, filters, metrics and application table.
- `DemoApp.jsx`: shell, navigation, snapshot commit, persona/clock/reset controls,
  Today and Dashboard. No backend calls.
- `screens/`: CaseDetail, EvcRegister, Evidence/UploadPage, RulesReports and
  Notifications. Screens call the shared service rather than their own timing rules.
- `demo.css`: preserves the existing presentation design and adds workflow views.

A real local path is CaseDetail → `changeCase` → `nextStage`/`enqueueEvc` → one
snapshot save through DemoApp → React state → case, EVC, Today and report selectors.
There is no API or MongoDB step in this presentation path. It reuses the existing
React entry, Tailwind build and Badge component; API mode still uses the old App.

Storage is **clockwork.presentation.v2**. On first load, a valid v1 snapshot is
upgraded additively: IDs, names, due dates, prior actions and reasons are retained.
Its original v1 key is untouched. Save/reset replaces only the v2 snapshot.
A quota/blocked-storage error displays an error and does not claim or render a
successful mutation. Reset clears the local in-memory filters/tab too. No shared
multi-tab conflict handling or cross-device persistence is claimed; use one tab
for presentation. Browser data can be edited or deleted, and activity is unbounded
until reset. Keep no confidential data here.

## Verification and presentation assets

From the repository root:

```text
node --test frontend/tests/demo-service.test.js
npm --prefix frontend run lint
npm --prefix frontend run build
```

From frontend:

```text
npx playwright test --config playwright.demo.config.js
```

The demo tests use installed Microsoft Edge and start/stop their own Vite server.
The default Playwright config still selects API foundation tests separately.
Verified checks are recorded in PROJECT_STATUS.md. Browser checks cover the full
script, reloads, all six downloads, rule preview/migration, role isolation,
rejection/resubmission, migration preservation, failed storage writes and reset.
The full journey asserts zero API requests and zero page errors.

Refreshed PNGs are copied to `docs/screenshots/` after final checks: Today,
Dashboard, Case, EVC calendar/list, Registers, focused Upload, Reports, Rules,
Notifications and Mobile. The walkthrough is reproducible and browser-checked;
**no narrated video recording has been produced**. Next useful task: rehearse and
record this exact five-minute script. Production backend work remains separately
scoped and was not restarted.

Final recorded results: **7 service tests passed; 3 Edge browser journeys passed in 13.8 seconds; lint passed; production build passed (33 modules).** Eleven refreshed PNGs are delivered under docs/screenshots/. API/backend tests were not run.
