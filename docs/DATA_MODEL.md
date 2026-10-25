# MongoDB data model

Phase 1 uses stable lowercase 24-character ObjectId-shaped strings as domain `_id`
values and references. Boundary conversion validates with BSON ObjectId and returns
the canonical string. This deliberate storage convention avoids mixing ObjectIds
and strings. System keys (rule version, audit head, session digest) use explicit
natural keys. Audit `_id` values are native BSON ObjectIds, never client-controlled.

| Collection | Phase 1 content / later responsibility |
|---|---|
| users | Argon2 hash, active flag, five-role identity, region/institution/committee scope |
| institutions | Name, region, new-institution flag |
| applications | Four synthetic route-entry fixtures, pinned rule, stage, human-workflow state |
| obligations | Shared validated model: kind, owner, scope, baseline/active due, independent lifecycle/evidence states, pause summary, completion, version |
| stage_events | Reserved append-only movements, pause interval pairs, attempts and escalation events; unique idempotency key |
| evc_visits | Reserved separate scheduling/visit/report data |
| undertakings | Reserved conditions linked to human decisions and obligations |
| document_metadata | Reserved issue/expiry, accepted lineage, encrypted storage references/checksums |
| evidence_submissions | Reserved separate submitted and officer-verified evidence |
| rule_sets | Immutable complete published rule/version documents |
| communication_templates | Reserved versioned deterministic text templates |
| notification_jobs | Transactional outbox: facts/why/rule/recipient/template, pending status, bounded attempt fields |
| audit_events | Ordered database-wide SHA-256 chain |
| magic_links | Reserved hashed, scoped bounded-use credentials; no endpoint yet |
| sessions | SHA-256 token digest, user reference, real expiry/revocation |
| checkpoints | Atomic audit sequence/head and isolated demo business clock |

Histories are referenced collections, not ever-growing arrays inside cases.
Small bounded routes/threshold lists are embedded in immutable rules. Current
obligation scope is denormalized for indexed reads; later assignment/institution
changes must update it transactionally and audit the change. A committee must match
both the obligation's committee and assigned owner; membership alone gives no case.

Obligations carry schema_version=1 and optimistic version fields. UTC instants use
timezone-aware Python values and Mongo millisecond precision. Future document
date-only issue/expiry values will be ISO YYYY-MM-DD, not UTC midnight guesses.
The configured business timezone is Asia/Kolkata. No financial/deposit model exists.

Implemented indexes: username uniqueness; session expiry TTL (cleanup only);
institution region/ID; obligation region/institution/owner with due/ID, application/ID,
unique creation_key; application institution/ID; unique rule ID/version; unique stage
event and notification idempotency keys; notification status/next attempt; unique
audit sequence. `_id` indexes cover individual resources and checkpoints. Remaining
collection indexes must be added with the actual Phase 4/5 query implementations.

Seed creates four cases (one per route), four institutions/Regions, twelve separate
accounts, four obligations, one rule version and one clock. This is a Phase 1
fixture, not the final 40–60-case demo or a SQL migration. Re-running seed uses
set-on-insert, preserves passwords/edits/time, rejects changed published rule content,
and appends a seed audit event. MongoDB validation currently relies on service-side
Pydantic and indexes; no claim is made that direct privileged DB writes are safe.

## Browser-only presentation model (not MongoDB collections)
clockwork.presentation.v2 stores applications, EVC visits, evidence registers with pending submissions and verified renewal history, immutable rule versions, simulated clock/persona, milestones, messages and activity. v1 saved data is upgraded additively while retaining its original key. See FRONTEND_DEMO.md for exact ownership, reset and single-tab limitations. No server schemas or MongoDB collections changed.

