# SIH mobile demo review

## Judgment and scope

ClockWork now presents the available ClockWork blueprint's main workflow and
deadline-monitoring story as a working phone-first React demo. It is ready for
**prototype screenshots and a rehearsed video**, subject to the remaining source
uncertainties below. It is **not production-ready**, and it does not prove official
SIH problem-statement compliance, regulatory compliance, or selection likelihood.

The reviewed implementation uses one browser-local dataset and rule/timing layer.
No real institutional data, government records, personal contact details, live
AICTE connections or external communications were used for this redesign.

## Sources actually inspected

| Source path | Location used | What it establishes |
|---|---|---|
| `docs/reference/AICTE Hackathon Verdict and Merged Blueprint.docx` | Full nonempty paragraph/table text, paragraphs 1–195; sections A–F, Key requirements, Screens, Seed data and Five-minute demo | Primary user-supplied blueprint for the review |
| `docs/ClockWork_Final_Blueprint.docx` | Same full paragraph/table text | Duplicate blueprint, not an independent official source |
| `clockwork-data-starter/docs/ClockWork_Final_Blueprint.docx` | Same full paragraph/table text | Duplicate blueprint in the older starter package |
| `clockwork-data-starter/docs/blueprint_provenance.json` | Entire metadata file | Records the original filename and duplicate provenance; all three Word files independently matched SHA-256 `e0c4037001d37ad5940db5daeb9107adc18ef0d04480fc7d56b6d1c64f8c7d50` in this run |
| `clockwork-data-starter/docs/DEMO_VIDEO_PLAN.md` | Provisional scope, scenario, narration and recording/rehearsal sections | Internal presentation plan; explicitly says no official format/duration rule was supplied |
| `docs/reference/README.md` | Requirements sources | Correct blueprint supersedes the earlier FDR brief; MongoDB selected by the user |
| `docs/FRONTEND_DEMO.md` | Existing implementation, limitations and walkthrough, then updated mobile guide | Previous behavior to preserve and actual current demo instructions |
| `frontend/src/demo/` and `frontend/tests/` | Model/service, mobile shell/screens, report selectors and tests | Implementation and browser verification evidence, not policy authority |

**Reference numbering:** Word page numbers depend on layout/rendering. These files
were inspected read-only through their OOXML paragraph and table content, not
rendered into stable page images. Therefore references below use the exact source
section and **nonempty paragraph ordinal**, including paragraphs inside tables.
No page or slide number has been invented. No presentation slide was available to
inspect. A paginated PDF/PPT or the original problem statement is needed for exact
page/slide cross-references.

## Workspace search and missing references

A recursive workspace file search found exactly the three Word files above and
**no PPT, PPTX or PDF reference presentations** outside dependency/runtime folders.
Filename and text searches of the project/starter documentation found no standalone
official SIH problem statement, problem ID or official slide template. References
to “problem statement” inside the blueprint are not the statement itself.

Requested while continuing implementation, still needed for a fuller review:

1. The exact official SIH problem-statement file/path, problem ID, organizer and
   edition/year. A PDF or saved official text is suitable.
2. The exact reference/submission PPT or PPTX and any PDF slide exports, with the
   intended version identified.
3. The official submission template and video duration/size/format instructions,
   if separate. The five-minute plan here is internal, not a verified SIH rule.
4. The applicable Approval Process Handbook extract if official timelines or
   terminology must be demonstrated. Demo rule values have not been validated
   against an official handbook.

No web search or unavailable deck has been represented as an inspected source.

## Requirement-to-screen mapping

| Available blueprint reference | Requirement | Mobile location | Actual status |
|---|---|---|---|
| A, paragraphs 22–35 | Four routes, authorized progression, reasoned return, pause/resume | Cases → Overview / Timeline | Implemented locally; all four routes tested. Human decision remains terminal; no automatic statutory approval |
| A, paragraphs 37–38 | Standard communications and factual case summary | Case → Communications / Overview | Template-based acknowledgement, deficiency and resubmission messages plus alert history; stored-data summary. Formal generated letter/PDF packaging remains partial |
| B, paragraphs 40–53 | Region/stage/institution/officer filters, workload, ageing and role views | Dashboard filter sheet, cards/charts, drill-downs | Implemented; all individual options have a nonempty seeded cohort. Combined empty selections show Clear filters |
| B, paragraph 53; paragraph 115 | Stage/Region bottlenecks and unusual-ageing recommendation | Dashboard mean active stage days and Reports → Region-wise performance | Mean active ageing and comparable stage/Region report cohorts implemented. No 1.8× heuristic recommendation flag is implemented |
| C, paragraphs 55–58 | EVC queue, new-institution focus, schedule/complete/report deadlines, calendar and escalation | Registers → EVC list/calendar; Case → Escalation | Implemented locally, including new/existing filter, explicit committee assignment and separate report verification |
| D, paragraphs 60–63 | Undertaking condition, due date, evidence, officer verification and escalation | Registers → Undertakings; focused upload page; Today | Implemented for seeded linked undertakings. Automatic undertaking creation from a newly granted conditional approval is not implemented |
| E, paragraphs 65–69 | Issue/expiry, advance alerts, renewal verification and validity colours | Registers → Documents | Implemented locally. Unverified renewal never changes the prior verified expiry. Current rule offsets are editable demo values, not official 90/60/30/15 policy |
| F, paragraphs 72–89 | Configurable reminders, why lines, channels and six exports | More → Rules / Notifications / Reports; Demo controls | Implemented simulated channels, time advancement and idempotent scan. No real delivery |
| F, paragraph 90; paragraphs 98–105 | Secure files, access controls, audit and integration | Simulated personas, metadata upload and local activity history | Intentionally simulated/partial. No encrypted file bytes, authenticated access, confidential download, tamper-evident frontend chain or connected AICTE adapter |
| Paragraphs 106–108 | Human oversight and reasoned override/correction | Explicit workflow/evidence decisions | Human action boundaries preserved. General automated-action override with reason is not implemented |
| Screens, paragraphs 117–122 | Today, dashboard, registers, case, rules/reports and upload page | Five phone tabs + More | Implemented; responsive cards and sheets replace desktop tables/sidebar |
| Paragraphs 111, 118, 152 | Fast-forward, 30-day view and realistic 40–60-case seed | Today, Demo controls, 60-case seed | Implemented with +1/+7/+30-day buttons instead of a slider; fixed 25 Oct 2026 date |
| Five-minute demo, paragraphs 155–160 | Filing through reports/audit narrative | Documented Cedar walkthrough | Existing case journey implemented and tested. New application filing and hash-chain demonstration are absent in the standalone frontend |

## Mobile and data evidence

- 390×844 target; 360px and 430px widths checked. Desktop centers the same restrained
  app canvas. Actual mobile images contain no decorative device frame.
- Shared compact header and five-tab bottom navigation; normal content scrolls in
  its own area above navigation. More contains rules, reports, notifications and
  demo settings. Upload remains focused without broad application navigation.
- Record cards replace wide application/report tables. Filters use a modal sheet.
  Case views, report choice, EVC view, filters and register tab survive navigation;
  relevant session view state survives reload. Reset restores those defaults too.
- 60 fictional institutions/applications, 15 per Region, all four routes in each
  Region, all eight EVC/SAC committee scopes populated. Each institution has one
  undertaking and one lease record (120 evidence/validity rows total).
- Seed contains returned, resubmitted, pending and completed cases; scheduled visits,
  pending/submitted reports; pending/rejected/verified evidence; valid, expiring,
  expired and renewal-pending leases; seeded communications and calculated alerts.
- Seeded completed decisions are explicitly fictional; the user interface does not
  make or imply a real statutory decision. Safe contacts use `example.org`.
- Dashboard and report values are computed from the same state. No display counts
  are hardcoded. Completed cases are not ranked/scanned as pending applications;
  their independent lease/undertaking obligations can still be pending.
- Version-3 localStorage preserves earlier snapshots and offers an explicit reset
  to the improved seed. No backend data or services were migrated or modified.

## Presentation-critical gap ranking

1. **High — missing official source pack.** Obtain the actual problem statement,
   submission template and reference slides before describing the demo as fully
   matching official SIH criteria. This does not block presenting the working app.
2. **High — avoid production claims.** Simulated personas, metadata-only uploads,
   public local reminder links and unsent messages must remain visibly labeled.
   No secure government workflow, real integration or full audit guarantee is proven.
3. **Medium — filing/conditional approval/overrides.** The available blueprint's
   full filing-to-decision narrative exceeds the seeded-case presentation path.
   Show the actual tested path; do not demonstrate imaginary buttons or decisions.
4. **Medium — advanced analytics and formal letters.** Mean stage ageing and stored
   factual messages work, but an unusual-ageing heuristic, formal letter exports,
   and production template administration are partial/missing.
5. **Low for this presentation — OCR.** Explicit optional stretch in paragraph 70;
   intentionally excluded. No AI or OCR accuracy claim is made.

The mobile navigation, data population, record consistency and screenshot-readiness
gaps identified in the earlier presentation interface were fixed in this run.
Production security, audit consistency, real storage and integration remain a
separate engineering phase. No backend work was restarted.


## Latest verified enhancement: institutions and simulated assistant

The final mobile frontend is ready for **prototype PPT screenshots and a rehearsed recording**, within the stated simulation boundaries. The official problem statement and submission deck remain unavailable, so this is not certification against official SIH requirements or a production-readiness claim.

### New requirement-to-evidence mapping

| Requirement | Implemented action/screen | Actual evidence |
|---|---|---|
| Institution imagery and relationships | More > Institutions; case thumbnail and overview; linked application/requirements | Local images load, failure fallback works, correct Cedar record opens; 360/390/430 layout tests pass |
| Case-aware assistant | More > AI Assist and Case Overview | Six-case deterministic unit comparison; cross-scope refusal; browser case switch changes facts and clears stale output |
| Summary, pending and next steps | Suggested questions | Current case fields/register references; no invented results; missing dates/stages return unavailable |
| Reminder/deficiency drafts | Assistant response and Copy | Review-only wording; missing deficiency remains an officer placeholder; clipboard and manual fallback tested; no sending/approval action |
| Unknown/input/error states | Question input, loading, Retry | Invalid/oversized questions tested; blank question retry and loading verified in browser |
| Modern mobile layout | Existing navy/blue/emerald React UI and SVG system | All five browser journeys pass, including three widths, keyboard sheet/focus, no console/runtime errors or API requests |
| Presentation captures | Five new images 11-15 and refreshed workflow images 01-10 | Real 390x844 browser captures, inspected after tests; no generated fake screenshots or device frames |

Implemented: scoped institution/profile navigation, small original local campus illustrations, deterministic assistant adapter, record citations, review-only drafts, loading/error/retry/copy, all existing workflows and exports. Simulated: personas, local uploads/messages/approvals and AI preview. Future: a real provider through FastAPI, backend authorization before record retrieval, verified versioned policy excerpts, backend-only secrets, human confirmation and evaluations. ASSISTANT_DESIGN.md details this separate path. No vector search, agents, OCR, model SDK or extra UI framework was installed.

The current asset exception is explicit: Wikimedia Commons source/licensing pages were reviewed and CC0 candidates identified, but download attempts returned HTTP 429. No photograph was included or hotlinked. The original SVG placeholders are labeled fictional/illustrative; IMAGE_ATTRIBUTION.md records the reviewed URLs, authors/licenses, failed retrieval and actual included asset provenance. The institution screenshot is therefore an illustration rather than a campus photograph.

Disk recovery required no archive or database deletion in this run: about 277 MB was available at start. ui.jsx was intact. Fixed a favicon 404, modal keyboard-focus restoration, missing-date assistant output, and screenshot positioning so the simulated-preview label remains visible. Lint/build and 13 unit tests pass. The final full browser suite passes with a separately managed local Vite server; the former Windows managed-server teardown hang is documented with reproducible commands. No new backend work was performed.

Remaining gaps are the earlier ranked blueprint gaps and missing official reference pack. The assistant is an additional presentation capability, not a newly asserted official SIH criterion. Real campus photos remain optional replacement work once a licensed download succeeds. No real model is running, no messages leave the browser, and no statutory approval is issued.

Final recorded results: 13 service/unit tests passed; full browser suite 5 passed in 41.0s with a clean exit; focused month-label and actual image-decoding fallback checks passed; final sequential capture 2 passed in 16.4s. All 15 PNG dimensions were verified and images visually inspected; new requested captures are 11-dashboard-assist.png through 15-ai-reminder-draft.png under docs/screenshots/mobile. No console/runtime error or unexpected backend request was reported. Edge emulation covered 360/390/430px; physical-device testing and a narrated recording remain outside these completed checks.

## Photographic layer update (supersedes the earlier photo-retrieval limitation)

The focused update successfully obtained four real photographs from Pexels, under its license, without retrying the blocked Wikimedia source. Local optimized JPEGs cover campus, laboratory equipment, classroom and library; attribution, original pages, license URL, byte sizes and SHA-256 values are in IMAGE_ATTRIBUTION.md. Today has a compact photo banner; institution cards and covers show campus photographs; selected EVC details show the facilities gallery. Every photo context is marked illustrative/fictional, and the gallery explicitly is not verified inspection evidence. These are presentation assets, not new claims about an institution's actual facilities. Existing SVG fallback, workflows, simulated assistant and backend are preserved. No dependency, model or inspection-evidence storage was introduced.

A dedicated browser check loads all four local images, blocks all external HTTP requests, checks three widths, navigates from institution cards into profiles, and exercises an actual corrupt-image fallback. Updated screenshot locations are recorded in FRONTEND_DEMO.md and final results in PROJECT_STATUS.md. Official SIH references remain unavailable; photography changes do not alter the prior implemented/simulated/future boundaries.

Final photo-update evidence: six browser tests passed in 37.3s with no console/runtime errors or backend requests; external-network-blocked image test passed, as did 360/390/430 layouts and corrupted-image fallback. Lint/build passed. The four real JPEGs are present in both public/photos and the production build, verified by checksum. All 18 refreshed 390x844 PNGs are delivered; photo-specific screenshots are 16, 17, 12, 13 and 18. The photographic presentation layer is ready within the existing prototype/simulation boundaries.

## Compact cards and visible AI Assist (2026-10-25)

Today, Cases and Institutions now use stable institution-ID colors and initials, case/Region/stage, deadline, owner and next-step labels. Photos remain only on the featured INST-2 profile and the EVC facilities gallery; other profiles have initials covers. These changes do not migrate or reset saved data.

Recording sequence: reset workspace, open Today, select the AI Assist card. It selects an overdue EVC case with a recorded committee in the current scope (falling back to another visible case). Choose **Summarize this case**, then **What is blocking progress?**. Read the recorded deadline and assigned committee; the cause of delay is explicitly unavailable unless recorded. Choose **Draft a reminder**, review the text, Copy draft, and use the suggested action to open the linked EVC entry. No message is sent. Changing the selected case clears the prior response and links. Retry response regenerates from that case's current records. Case Details exposes AI Assist across every section; More also retains its entry.

The assistant remains a **Simulated AI preview**, using deterministic local record responses with supporting facts, scoped clickable references and navigation-only suggestions. No model, API key, backend call, policy invention or automated decision was added. Real integration remains future work as documented in ASSISTANT_DESIGN.md.

Current screenshots: 19-today-compact-cards.png, 20-compact-institution-cards.png, 12-institution-profile.png, 21-ai-evc-summary.png, 22-ai-evc-blockers.png and 23-ai-evc-reminder.png under docs/screenshots/mobile/. Earlier 16/17 photo-list captures are superseded, retained as historical artifacts.

## Presentation wording polish (2026-10-25)

Primary alert content now shows a readable deadline status, overdue/remaining days and next action. Historical alerts use their recorded deadline and scan date, not today's current record. Full rule/threshold references remain in expandable **Why this alert?** details. Recipient labels use Institution document coordinator; timeline update counts use singular/plural correctly. Case elapsed time no longer leads with a rule version. Communications, activity, reports and assistant dates use readable dates; encoded spaces are normalized at presentation boundaries without rewriting stored records.

AI Assist has a compact **AI preview** label and an **About AI preview** information button. Its keyboard-accessible dialog explains sample-record responses, no live model, draft review and simulated messages/approvals. A small shared **Demo** badge remains visible. More > **About this demo** collects imagery, rule, local-storage and simulation explanations. Photos retain short not-inspection-evidence captions; uploads still explicitly say files are not uploaded. Copy uses the same polished text shown on screen.

Verified: lint/build passed; 8 assistant/wording unit tests passed; all 8 Playwright browser checks passed in 46.1 seconds (workflows, persona/filter scopes, persistence/reset, 360/390/430 layouts, clipboard/fallback, image fallback, information dialog and detailed alert explanations). Console/API diagnostics passed. Refreshed 390x844 captures in docs/screenshots/mobile/, including 09-notifications, 12-institution-profile, 14/15 AI responses and 19-23 compact cards/EVC assistant. Notification and AI summary captures visually inspected. No backend, dependency, workflow or stored-data migration changes.
