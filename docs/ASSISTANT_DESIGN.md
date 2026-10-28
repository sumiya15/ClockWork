# AI Assist: implemented preview and future model integration

## Implemented now

`frontend/src/demo/assistant.js` exports the replaceable async `askCase(data, caseId, question)` boundary. It validates question length and persona scope before selecting a case. It reads that case's state, route, owner, target date, paused clock, pinned rule version and linked registers. Responses contain case ID/version, business date and navigable record references. Suggestions and drafts are deterministic; no model inference, external request, API key, AI framework or vector store exists.

`AssistantPanel.jsx` provides suggested questions, input, loading, errors/retry, copy with manual-selection fallback, and supporting-record links. Case selection/scope/date/revision changes remount the view to prevent stale responses; unmount invalidates pending requests. Unknown questions return unavailable information. No approval, inspection finding or official policy is invented. Reminder and deficiency drafts are read-only review copies; absent deficiencies remain officer placeholders, not allegations. No message sending or domain mutation is performed.

Responses are intentionally ephemeral, not saved in localStorage; reload regenerates from current records. Existing shared case mutations persist as before. Reset clears the case state and assistant view through navigation. Clipboard is browser-controlled; if unavailable, manual copying is offered.

## Production path: not implemented

React client -> authenticated FastAPI `/api/v1/assistant` endpoint -> authorized case retrieval and verified policy excerpts -> model provider -> validated response with citations -> user review.

Enforce role, Region, institution and committee scope on the backend **before** fetching records; never trust client-selected IDs or supplied facts. Keep model credentials exclusively in backend settings/secret storage. Minimize/redact confidential content; use an approved provider agreement and retention policy. Retrieve only the selected authorized case and genuinely applicable, versioned policy documents. Return record versions, policy source/page/version and uncertainty; reject unsupported citations. Uploaded text is untrusted content, not instructions. Do not expose tool access for approvals, sending or record modification. Validate outputs and require competent human review, including every draft.

Add bounded timeouts, rate limits, request cancellation, safe errors, consent/retention decisions and redacted access audit. Evaluate cross-scope leakage, missing evidence, conflicting dates, stale versions, malicious document instructions and fabricated findings before deployment. Start with direct authorized retrieval; introduce search only if measured corpus needs justify it. Vector search, agents and OCR are not installed for appearance. OCR-assisted date extraction is future work and requires a human to confirm every date before it becomes authoritative.

## Actual technologies

React 19.3.1, JavaScript/JSX, Tailwind CSS 4.3.3 via Vite, existing scoped CSS and original SVG icons. Existing native dialog component is retained. No TypeScript migration, shadcn/ui, Lucide, Motion, Recharts, AI SDK or new dependency was installed. The existing stack supports these isolated screens without overlapping libraries or new build tooling. Do not list unused technologies in the PPT.

EVC explanations now read the linked EVC record for committee, scheduled visit, visit completion and report status. They expose the case deadline and say the cause is unavailable unless a reason is recorded. caseGuidance.js shares navigation suggestions between cards and assistant; suggestions never mutate records. Responses include supporting facts, record links and retry controls.
