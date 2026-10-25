# Incremental migration plan

Written before this run's application changes. Routine additive work is authorized;
there is no production cutover or deletion in this plan.

## Phase 0 / 1 in this run

1. Preserve the corrected Word source under `docs/reference/` and record the missing
   roadmap as an unresolved source. Keep the existing SQL runtime/tests/data intact.
2. Snapshot the interrupted FDR subtree under ignored `.local/`, then rename its
   generic foundation to `backend/app/`. Remove deposit-specific configuration by
   replacing it with ClockWork roles, collection names and cookie authentication.
   This is source refactoring only; no FDR database was configured or seeded.
3. Add MongoDB replica-set lifecycle/indexes, five-role scope enforcement, secure
   sessions, injected real/demo clock, validated immutable rule versions and common
   obligation schemas. Domain mutation + audit + optional notification job share
   one transaction. Do not expose later-phase workflow writes prematurely.
4. Seed a separate synthetic MongoDB database; build a React login and authorized
   obligations read path. Keep the client honest about unimplemented actions.
5. Run legacy regressions, disposable MongoDB integration tests and client checks.
   Record actual outcomes and blockers.

## Next bounded phases

### Approved folder-layout alignment

Before further features, align implemented code with the user's supplied tree:
move domain code under `backend/app/modules`, business time/rule definitions under
`engine`, Mongo lifecycle/indexes/transaction boundary under `db`, API registration
under `api`, development seed under `backend/scripts`, and new tests under
`backend/tests/{unit,integration}`. Move React code into `app`, `features`, `lib`
and `styles`, extracting the existing top bar as shared layout. Preserve the SQL
runtime and its existing test paths during this source-only migration. Move the
new seed JSON to root `config`; leave the separate legacy config unchanged.

Update imports, path resolution, dependency metadata and commands; compare OpenAPI
before/after and rerun real Mongo/browser checks. No database schema, data, routes,
permissions or feature scope changes are intended. Unimplemented modules/workers/
adapters stay documented rather than adding empty placeholder folders.

2: Port filing/transition/return/resubmit behavior using existing SQL tests as a
contract. Expand EVC into configured scheduling/completion/reporting handlers;
require explicit SAC/SHC assignment. No live cutover until parity is demonstrated.

3: One evaluation service for manual scan, worker and isolated demo advance;
idempotent events/jobs, why facts, override history and deadline-ranked Today UI.

4: Encrypted storage, bounded magic links and verification; EVC/undertaking/document
registers and accepted renewal lineage. Upload is never verification.

5: Scoped metrics/reports, communications/case summaries, full audit/access coverage,
typed labeled integration adapters. 6: 40â€“60-case rehearsal and UI polish.

## Data migration and rollback

No SQL-to-Mongo conversion is performed in Phase 1. New MongoDB demo records are
independent fixtures, not a migration of user data. Before cutover, take a consistent
SQLite backup (SQLite backup API) or PostgreSQL snapshot, checksum it and restore
into an isolated copy. Build an explicit mapping for IDs, administrator->admin,
route versions, timestamps, assignments, pause histories and synthetic old audit
events. Never claim old events were hash chained at original creation time.

Reject/quarantine ambiguous records with counts and reasons. Preserve source IDs
as unique import references. Dry-run conversion must compare counts, relationships,
pause durations, pinned rules and representative API results. Re-run must be
idempotent. Seed must not precede import into that destination.

At a later approved cutover, quiesce writes, repeat snapshot/conversion/verification,
then change API routing. Keep the original SQL database and server available for
rollback. Returning to SQL after new Mongo writes requires reviewed delta replay;
simply switching URLs would lose new work. No dual writes are introduced.

Phase 1 rollback: stop only the new API/frontend processes and use unchanged
`backend.main:app`. Restore the FDR source snapshot only for forensic comparison,
not as an active product. Do not remove any database to roll back this phase.

## Standalone presentation demo — 2026-10-25
User replaced the immediate Phase 2 goal with a frontend-only presentation. Add a separate local demo service and screens; default frontend to demo, preserve the existing API application via VITE_APP_MODE=api. No backend edits or database migration. Demo localStorage is versioned and reset affects only its own key. Remaining truncated screen requirements are pending; use the previously defined ClockWork screens for a coherent walkthrough.


## Completed frontend continuation
The untruncated frontend requirements now use a version-2 local snapshot. The v1 snapshot is retained and upgraded additively; no backend schema or data migration. Explicit Reset Demo initializes the deterministic new presentation. Use VITE_APP_MODE=api for the preserved backend interface. Full behavior and rollback-by-mode-switch are documented in FRONTEND_DEMO.md. Do not infer production Phase 2 completion from the local workflow.

