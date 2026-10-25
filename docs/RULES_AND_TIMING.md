# Rules and timing

All values in `config/demo_rules.json` are synthetic demo assumptions, not
official AICTE policy. No policy quotation is invented. Pydantic validates route
stages, complete supported stage mappings, duration/unit/start-event fields and
unique increasing threshold offsets. The seed publishes version 1 atomically;
changing its contents under the same version is rejected. Cases and obligations
retain rule_id/version. A new route using existing stages is configuration; new
stage behavior needs a reviewed handler. Handlers themselves are Phase 2.

Four configured routes: SCRUTINY_ONLY, SCRUTINY_EVC, EVC_SAC_SHC, EVC_ONLY.
EVC expands into evc_scheduling, evc_completion and evc_report. Their configured
start events are stage entry, visit scheduled and visit completed respectively.
SAC/SHC assignment is an explicit committee reference in fixtures, not a silent
choice of statutory authority. Scrutiny/SAC-SHC pauses are enabled; EVC and expiry
obligations are not paused by these demo settings.

Business timezone: Asia/Kolkata. N calendar days means the local start-event date
plus N, valid through 23:59:59.999 that date. Overdue begins at the next local
midnight. Days remaining uses local calendar-date subtraction, not rounded UTC
seconds. Due today = 0; overdue <0; due soon 1–7; active >7 in the Phase 1 read view.
Lifecycle and evidence verification remain separate. Submitted evidence never
changes overdue to completed. The seven-day view window is a foundation display
convention, not the published notification ladder; Phase 3 will use rule thresholds.

Paused seconds preserve elapsed active time; completed pause time extends active
due, and the read view projects an ongoing pause to current business time. Baseline
due never changes. Phase 2 must persist start/end pause events and version-guarded
resubmission, retaining the same allowance and incrementing re-scrutiny attempts.
The existing SQL tests provide behavioral examples; new Mongo transition tests are
required before enabling these actions. No pause endpoint exists in Phase 1.

`RealClock.now()` uses actual UTC. `DemoClock.now()` loads a persisted clock only
from clockwork_demo_* or generated clockwork_test_* databases. Mode validation
prevents demo clocks against clockwork_live_*. Authentication always uses real time.
No advance/reset endpoint or external delivery adapter exists yet.

Phase 3 contract: scheduler and manual/slider actions call ONE evaluator. A forward
jump records every newly crossed milestone with a unique obligation/rule-version/
threshold/event key; coalesce external notification into the highest newly reached
level per obligation/recipient/channel per scan while preserving all milestone
events. Backward movement is rejected. Corrections append reasoned events; no history
deletion. These are planned semantics, not tested implemented scans.

## Browser-only timing implementation
The frontend demo now uses shared date-only calendar arithmetic, due-day-inclusive boundaries, configured pause intervals, remaining-SLA resumption, pinned rule versions and explicit previewed migration. Its +1/+7/+30-day evaluator records every crossed milestone and coalesces unsent messages to the latest new threshold per target/channel/scan. Repeated scans are idempotent. These are local simulation semantics, not a server scheduler implementation. See FRONTEND_DEMO.md for formulas and examples.

