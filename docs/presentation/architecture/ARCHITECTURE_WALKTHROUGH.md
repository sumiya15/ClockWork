# ClockWork architecture walkthrough

## Open and prepare

1. Open `docs/presentation/architecture/interactive/index.html` in Edge or Chrome. Double-click it in File Explorer, or use **Ctrl+O** in the browser. No server, installation, internet, Python environment or application login is needed.
2. Keep `index.html`, `presentation.css` and `presentation.js` together. The other files in that folder are validation evidence and are not required to present.
3. Click **Fullscreen**. Click **Exit fullscreen** to leave, or press Esc. If browser policy blocks the Fullscreen API, use **F11**. Use desktop landscape; the presentation fits a 16:9 frame automatically.
4. Click **Reset** before recording. This resets only the presentation to step 1, Current prototype, 100% diagram zoom and no pinned explanation. It does not access or reset ClockWork's application data. Fullscreen remains active.
5. Hover a box to highlight its connections. Click to pin its explanation in the right panel. Click that box again, choose **Unpin**, or press **Esc** to release it. Enter/Space also pins a keyboard-focused component.
6. **Next**, **Previous**, the numbered buttons, or arrow keys navigate the same 14 steps. Step 8 switches to Target architecture. Navigation clears a pin. Home/End select the first/last step; R resets the walkthrough.
7. Use **+ / −** for diagram zoom. Drag the diagram when zoomed; Reset restores the complete view. Keep 100% for the main recording so all connections remain visible.

No video was created or modified for this deliverable. The following is a proposed narration pace, not a measured recording duration. Practise once and leave a short pause at the current/target transition.

## 90-second explanation

Start at step 1. Hover or pin the named box; use Next or the indicated numbered button to advance. Labels below match the diagram exactly.

| Time | Cursor target | Action | Exact spoken explanation |
|---|---|---|---|
| 0:00–0:07 | Users + React interface | Step 1; hover the upper-left box. | “ClockWork connects institutions, officers and committees through a mobile interface. This prototype uses fictional records and simulated access.” |
| 0:07–0:13 | Shared browser state | Next → step 2; point along Actions. | “Shared browser state keeps the screens connected. Each action returns updated records.” |
| 0:13–0:21 | Workflow + deadlines | Next → step 3; hover and follow Calculate / Next state. | “Frontend functions handle four routes and deadlines. Permitted SLA pauses preserve elapsed processing time.” |
| 0:21–0:29 | EVC + compliance | Next → step 4; point at Human verification required. | “Visits, undertakings and renewals share this workflow. Evidence stays pending until officer verification changes compliance or validity.” |
| 0:29–0:35 | Local persistence | Next → step 5; hover the middle box. | “Browser persistence stores records and file metadata. Protected documents and secure operational audit remain incomplete.” |
| 0:35–0:41 | Alerts + escalation | Next → step 6; point along Evaluate. | “Alerts explain deadlines and responsible authorities. These communication records are simulated; nothing is delivered.” |
| 0:41–0:47 | AI Assist | Next → step 7; click to pin the preview explanation. | “AI Assist uses deterministic templates, without a live model. People review its drafts.” |
| 0:47–0:55 | FastAPI + authorization | Next → step 8 switches views; point at HTTPS. | “The target connects React through FastAPI. Authentication and scoped-read foundations exist; complete operational writes and integration remain unfinished.” |
| 0:55–1:01 | Shared workflow engine | Next → step 9; follow Actions. | “The planned server engine enforces published rules, transitions, SLA calculations and escalation across workflows.” |
| 1:01–1:07 | EVC + compliance APIs | Next → step 10; point at Officer verification gates. | “Domain APIs record visits and evidence decisions, with human verification enforced on the server.” |
| 1:07–1:14 | MongoDB + documents | Next → step 11; follow Read / write and State + audit. | “MongoDB and audit helpers exist. Complete domain persistence and protected document storage still need implementation and security validation.” |
| 1:14–1:21 | Worker + escalation | Next → step 12; point at Scan, Outbox and Results. | “A planned worker evaluates deadlines and consumes notification jobs, recording delivery results and retries in storage.” |
| 1:21–1:26 | Integration adapters | Next → step 13; point along Deliver. | “Authorised adapters connect AICTE systems and notification providers. These connections are proposed.” |
| 1:26–1:30 | AI Assist endpoint | Next → step 14; end on the dashed box. | “Future AI stays behind scoped APIs. Humans retain decision authority.” |

## 30-second short version

Use numbered buttons to jump; keep 100% zoom. Approximately 65 words, with time for a brief pause between views.

| Time | Cursor target | Action | Exact spoken explanation |
|---|---|---|---|
| 0:00–0:08 | Shared browser state | Reset, then step 2. | “ClockWork currently runs connected frontend workflows using fictional browser data. Notifications and AI Assist are simulated.” |
| 0:08–0:16 | Workflow + deadlines → EVC + compliance | Steps 3 and 4; point at verification. | “Its strongest controls preserve SLA time, explain deadline alerts, and require officer verification before compliance or lease validity changes.” |
| 0:16–0:24 | FastAPI + authorization → MongoDB + documents | Steps 8 and 11. | “The target connects React, FastAPI, a shared engine and protected storage. Backend foundations exist, but operational integration remains incomplete.” |
| 0:24–0:30 | Worker + escalation → AI Assist endpoint | Steps 12 and 14. | “Workers, external adapters and future AI remain planned. Human decision authority stays explicit.” |

## Five likely questions

**1. Is the current mobile prototype connected to FastAPI and MongoDB?**

The demonstrated workflow uses React state and browser persistence. A separate API foundation exists, including authentication and scoped reads, but it does not power these demonstrated workflow mutations.

**2. How does the shared engine differ from an ordinary dashboard?**

It demonstrates controls behind the display: route transitions, elapsed-time-preserving SLA pauses, shared deadline thresholds and idempotent milestones. These are verified local implementation behaviors, not claims of uniqueness or a deployed scheduler.

**3. Does uploading a lease renewal immediately make it valid?**

No. The current frontend keeps the previous verified expiry until an officer verifies the pending renewal. The target must enforce the same rule on the server and protect actual document bytes.

**4. Are authentication, notifications and audit production-ready?**

No. Session/CSRF/scope code, MongoDB repositories and audit/outbox helpers exist as foundations. Complete domain writes, secure document handling, scheduled delivery, protected audit coverage and deployment validation remain incomplete. A persona selector is not authentication.

**5. Is AI Assist using a live model or deciding approvals?**

No. It uses deterministic templates over scoped local facts. A future backend AI endpoint is proposed; it would require authorisation and evaluation. Humans review drafts and retain decision authority. No statutory approval is issued by this prototype.

## Status legend and static slide captions

- **Implemented:** source code exists for the stated local behavior or backend foundation. This does not mean production certification or complete integration.
- **Simulated:** preview behavior, especially AI and communications, with no model call or delivery.
- **Planned / incomplete:** operational components or connections that still need implementation or integration. Dashed target arrows are planned connections.

Current slide caption: “Working local workflows share browser state and deadline calculations; AI and communications remain simulated.”

Target slide caption: “Existing FastAPI and MongoDB foundations support a proposed operational architecture with server verification, workers and authorised adapters.”

Use [walkthrough-current.svg](walkthrough-current.svg) / [PNG](walkthrough-current.png) and [walkthrough-target.svg](walkthrough-target.svg) / [PNG](walkthrough-target.png). PNGs are 3200 × 1800; SVGs retain editable text, boxes and arrows.

## Evidence and scope

Content was checked against the existing current/target architecture assets, `frontend/src/main.jsx`, `demo/DemoApp.jsx`, `service.js`, `model.js`, `assistant.js`, and `backend/app/api/router.py`, authentication guards, scoped obligation/rule routes and audit/notification repositories. Frontend paths beginning `demo/` in the information panel are relative to `frontend/src/`; backend module paths are relative to `backend/app/`.

The existing backend notification repository explicitly states that delivery and a worker are not implemented in Phase 1. Local evidence actions retain pending state and update verified dates only in the officer-verification branch. These facts determine the status labels; screenshots alone were not used as implementation evidence.

No attached reference image was available to inspect in this workspace. The presentation follows the requested grouped boxes, labelled arrows and green visual direction, and reuses verified content from the existing architecture files.

Actual browser checks and reproducible export instructions: [interactive/README.md](interactive/README.md).
