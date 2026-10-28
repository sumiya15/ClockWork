## Mobile presentation acceptance (not production readiness)

- [x] 390x844 phone UI with 360px/430px verification; no decorative device frame.
- [x] Navy/blue shared header, five bottom tabs, More tools and isolated demo controls.
- [x] Mobile cards/filter sheets replace wide tables; bottom nav has reserved space.
- [x] Complete workflow, SLA, EVC, evidence, rules, reports and notifications preserved.
- [x] 60 linked fictional cases; all Regions/routes/personas/individual filters populated.
- [x] Fixed seed date, v3 storage, old-data preservation/reset offer, view-state persistence.
- [x] Mobile browser walkthrough and service tests pass; lint/build pass.
- [x] Actual screenshots and blueprint-to-screen review documented.
- [ ] Official SIH problem statement and PPT/PDF deck reconciled (files unavailable).

## Standalone frontend demo acceptance (separate from production phases)

- [x] 60 fictional applications across 4 Regions, one shared data/calculation layer.
- [x] Case details, factual summary, timeline, communications, escalation ladder and activity.
- [x] Configured return pause and repeated resubmission preserve remaining active SLA.
- [x] EVC queue once, explicit assignment, scheduling dialog, visit/report/verification states, month calendar/list.
- [x] Reasoned evidence submission/verification/rejection, renewal history; unverified renewal never changes verified validity.
- [x] Validated editable rules, preview, versioned publication and explicit case migration.
- [x] Six scoped, filtered downloadable reports and defined metric cohorts.
- [x] Five clearly simulated personas; records and actions follow role/scope.
- [x] +1/+7/+30-day shared clock, idempotent scans, milestone history, why lines and unsent channel panel.
- [x] Focused simulated institution reminder page updates register and officer queue.
- [x] Persistence, additive legacy upgrade, failed-write handling and full reset checked.
- [x] Deterministic walkthrough, browser journey, lint and production build verified.
- [x] Presentation screenshots regenerated and documentation updated.

Evidence: seven service checks and three browser journeys; see PROJECT_STATUS.md.
These checks do not complete any backend/security acceptance items below.

## Presentation scope notice

The current standalone frontend demo is separate from the production phase checklist below. Local simulations do not satisfy backend workflow, authorization, audit, file security or database acceptance. See FRONTEND_DEMO.md and PROJECT_STATUS.md for actual scope and checks.

# ClockWork acceptance checklist

User-supplied checklist, reconciled with implementation evidence on 2026-10-25.
Checked means implemented and supported by recorded checks, not necessarily rerun
in the latest review. See PROJECT_STATUS for commands and dates. Legacy SQL behavior
does not satisfy acceptance of the new MongoDB workflows. Missing reference roadmap
reconciliation remains open even though the foundation below is implemented.

## Phase 0 and 1 — Structure and foundation

- [x] Assessment references actual files, dependencies, and observed behavior.
- [x] Migration map preserves useful code and user edits.
- [x] React and FastAPI run with documented commands.
- [x] MongoDB is the application database; credentials stay on the backend.
- [x] Liveness/readiness and a protected client-to-API request work.
- [x] Five roles and scope checks are present from the start.
- [x] Clock abstraction separates real security time from simulated business time.
- [x] Rule schema/versioning and the obligation model are implemented.
- [x] Project status records what was actually tested.

Evidence: REPOSITORY_ASSESSMENT/MIGRATION_PLAN; 13 foundation checks (11 real Mongo
plus 2 DB-independent) and two real browser journeys passed during the folder-layout
verification. The new runtime uses MongoDB; the preserved SQL runtime remains a
separate compatibility application, not a migrated dataset. Rules are immutable
seed-published versions; an admin editing/preview/publication UI is not yet implemented.

## Phase 2 — Workflow

- [ ] Every configured route reaches the intended human decision stage.
- [ ] Completion creates the next stage once, including retries/concurrent actions.
- [ ] Return requires a reason and pauses only configured clocks.
- [ ] Repeated return/resubmit cycles preserve remaining active SLA.
- [ ] Committee/Region/ownership authorization is checked server-side.

Read scopes exist, but Mongo workflow mutation/assignment checks and transitions do
not. The SQL workflow tests are a useful porting contract, not evidence of Mongo parity.

## Phase 3 — Timing and communication engine

- [x] Due-day convention and timezone are documented and tested.
- [ ] Repeated scans are idempotent.
- [ ] Large time jumps have defined milestone behavior.
- [ ] Notifications show truthful channel/delivery status and why lines.
- [ ] Overrides require an authorized actor and reason.
- [ ] Demo controls cannot send real messages or alter real datasets.

The checked item covers the foundation calendar-date calculation and due-day boundary.
Large-jump semantics are documented as a plan, not implemented. No scan/slider exists.
An idempotent outbox enqueue and isolated clock alone do not satisfy these full items.

## Phase 4 — Registers and uploads

- [ ] EVC scheduling and completion/report deadlines are distinct.
- [ ] Undertaking upload waits for officer verification.
- [ ] Unverified renewal does not replace verified validity.
- [ ] Magic links enforce expiry, scope, revocation, and replay policy.
- [ ] Private file storage is encrypted and downloads are authorized.

EVC kinds/start events exist in rules/models, but scheduling/visit/report actions
are not implemented. Evidence and deadline states are separate, but uploads and
officer verification workflows are not implemented. These remain unchecked.

## Phase 5 and 6 — Complete experience

- [ ] Dashboard metrics state definitions and sample sizes.
- [ ] All six reports apply server-side filters and access scope.
- [ ] Summaries contain only stored facts.
- [ ] Audit coverage, failure handling, and integrity limitations are documented.
- [ ] Mock integrations and simulated channels are visibly labeled.
- [ ] Seeded data covers 40-60 applications and 4 Regions.
- [ ] The five-minute demonstration works from a reproducible reset.

Authentication/seed audit and failure semantics are documented/tested, but full
workflow/access audit coverage does not exist yet. There are four application
fixtures across four Regions. No reset command, mock integration UI or full demo
rehearsal is claimed.
