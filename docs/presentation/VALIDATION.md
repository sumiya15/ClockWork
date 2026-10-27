# Final UI and presentation validation

Executed 26 October 2026 on Windows using installed Node, Playwright and Edge. No new dependencies were installed. No video was created or modified; both browser configurations disable video and trace capture.

## Executed results

| Check | Actual result |
|---|---|
| npm.cmd run lint | Final run passed, zero errors. |
| npm.cmd run build | Final run passed, 42 modules transformed. |
| node --test tests/*.test.js | 17 passed, zero failed. |
| node tests/presentation-measurements.mjs | All assertions passed; evidence/measurements.json contains results. |
| playwright.demo.config.js | Final full run: 8 passed. Personas, all individual filter choices, workflow, reload/reset, keyboard sheets, image loading, AI drafts/fallback. |
| playwright.final-presentation.config.js | 2 passed. Complete screenshot journey and mobile/semantic-color checks. |
| node tests/render-architecture.mjs | Both diagrams rendered to 3840 x 2160; no text outside canvas. |

An intermediate unused-import lint failure was fixed before the final passing lint/build. Earlier visual review caught header contrast, encoding artifacts and internal register IDs; fixes were included in refreshed screenshots. The final full browser suite passed all eight tests.

## Measured fictional dataset

60 applications, 60 institutions, four Regions, 36 EVC records, 60 undertakings and 60 leases; 52 open and eight seeded completed applications.

| Independent clock scenario | Active targets | Overdue | Due today | Upcoming within 7 days | Overdue open applications |
|---|---:|---:|---:|---:|---:|
| Baseline 25 October | 152 | 63 | 1 | 35 | 25 |
| +1 day | 152 | 64 | 0 | 35 | 26 |
| +7 days | 152 | 98 | 1 | 6 | 44 |
| +30 days | 152 | 129 | 0 | 0 | 50 |

- All four route sequences reached Human decision without issuing approval. Direct functional scenarios reset one seed case per route; the browser journey covers Scrutiny + EVC.
- Independent +30 days: 669 channel records; five repeated fixed-date scans added zero records, with zero duplicate IDs. Eligible deadline targets had alerts and recipients matched the configured escalation ladder.
- Two seven-day pauses retained five remaining days and nine active days, with 14 paused days and two resubmissions.
- Undertaking submission remained pending until verification. Lease submission retained expired validity of 23 October 2026; verification changed expiry to 25 October 2027 and retained one prior validity record. The separate screenshot journey uses 1 December 2027.
- Six baseline report row counts: pendency 52, EVC 36, undertakings 60, documents 60, overdue compliance 65, performance 24. The overdue report includes paused cases; the active target count excludes them.

These are synthetic functional results, not production accuracy, time savings or impact measurements. Rule thresholds and calendar-day policies require authoritative APH validation.

## Journey and visual review

The browser journey returned CW-2026-002, advanced seven days, resubmitted, completed scrutiny, scheduled EVC, advanced 30 more days, inspected escalation, submitted and verified undertaking/lease evidence, downloaded all six reports and opened history/alert explanations. Final date: 1 December 2026. There were 900 simulated channel records; repeat scan added zero. The journey captured zero page/console errors and zero /api/ requests. Evidence: evidence/green-journey.json.

All 23 selected screenshots are distinct 390 x 844 PNGs. Every image was visually inspected, including replacement evidence/report/history images after ID cleanup. Long screens continue vertically; AI response areas scroll internally, and the reminder screenshot shows the opening draft. The About sheet is an intentional overlay. No accidental dialog obscures a primary capture.

Today, Dashboard, Cases, Registers, Reports, Notifications, Case, Institution and AI Assist were exercised at 360, 390 and 430 pixels. No horizontal overflow was detected. Computed color checks found no blue UI accents on tested routes and confirmed overdue red. Pending and verified EVC colors were visually inspected. The institution photo loaded successfully and remains labelled illustrative.

Both architecture diagrams were visually inspected. Editable SVGs and 16:9 PNGs are accompanied by Mermaid logical representations; Mermaid does not promise identical visual positioning.

## Preservation

Disk space was checked before asset writing: 7,773,085,696 bytes free. Hash comparison of 82 existing backend, data and video files found zero changed and zero missing files (cached Python bytecode excluded). See evidence/preservation-check.json. No source, database or presentation asset was deleted. Browser tests used isolated contexts, not the user's existing state. Environment variables, application modes and storage keys remain unchanged.

Screenshot hashes and dimensions: evidence/screenshot-manifest.json. Older video-derived evidence is historical and was not regenerated. Use [FRONTEND_DEMO.md](../FRONTEND_DEMO.md) for startup/reset and screenshot-only commands, and [VIDEO_SCRIPT.md](VIDEO_SCRIPT.md) for manual recording.

## Limits and verdict

No production backend end-to-end test, security audit, real delivery, secure document-byte persistence, AI model evaluation or authorised integration was performed. Backend code was inspected and preserved. Local persona selection and editable browser history are not authentication or protected audit storage.

The official SIH page returned HTTP 403. User-supplied requirements and the repository blueprint remain primary; a full third-party PS transcription was inspected but not authenticated against the official source. No official PPT template or reference-diagram attachment was available. These did not block the UI/assets; applicable APH and integration specifications remain prerequisites for operational readiness.

Ready for screenshots and an honestly presented fictional prototype demonstration. Not ready for secure operational approval processing. See [the requirement matrix](../SIH_26262_READINESS.md) for code evidence and prioritized gaps.
