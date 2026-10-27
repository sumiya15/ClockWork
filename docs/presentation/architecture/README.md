# ClockWork architecture assets

Two original diagrams use grouped components and labelled arrows, editable SVG text/shapes, a green palette and a 1920×1080 canvas. PNG exports are **3840×2160**, suitable for a 16:9 slide. Mermaid expresses the same logical nodes/edges; its automatic layout may differ from the manually arranged SVG.

| Diagram | Editable SVG | High-resolution PNG | Mermaid |
|---|---|---|---|
| Current prototype | [SVG](current-prototype.svg) | [PNG](current-prototype.png) | [Source](current-prototype.mmd) |
| Target system | [SVG](target-system.svg) | [PNG](target-system.png) | [Source](target-system.mmd) |

Current diagram: solid local components are implemented simulations. React `DemoApp` passes current state to operations; returned state is persisted through `saveDemo` and set into React. Local storage restores records, session storage restores views. `service.js` and `model.js` handle transitions/timing; `assistant.js` reads scoped records without a model. Notifications have no real delivery. The dashed separate foundation is not connected to these operational screens.

Target diagram: solid auth/scoped-read and Mongo/audit foundations exist in source. Dashed domain services, shared operational engine, worker, protected storage, adapters and AI endpoint require implementation or integration. Existing rule/date helpers and audit/outbox helpers do not establish the complete target. Human decisions enter through the interface and pass authorised verification gates. The worker invokes deadline evaluation; notification jobs go to providers, and result/audit records go to storage. API-mediated evidence operations reference protected files.

Sources: `frontend/src/main.jsx`, `demo/DemoApp.jsx`, `demo/service.js`, `demo/model.js`, `demo/assistant.js`, `backend/app/api/router.py`, `api/health.py`, `modules/auth`, `modules/audit`, `modules/notifications` and `db/transactions.py`. Blueprint SQL wording is superseded by the repository's current Mongo target; the legacy SQL runtime remains separate.

Reproduce from repository root: `.\.venv\Scripts\python.exe scripts/build_architecture.py`, then from `frontend`: `node tests/render-architecture.mjs`. Rendering uses installed Edge/Playwright, no new dependencies. No bitmap generator or video capture is used. No attached visual reference was available, so the user's requested grouped layout was followed.
