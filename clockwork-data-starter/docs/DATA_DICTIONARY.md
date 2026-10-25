# ClockWork data dictionary and preparation rules

## Source and identity

The core entities follow the uploaded ClockWork blueprint. `pause_intervals` and `demo_clock` are supporting implementation records, not new regulatory requirements. This kit's schema is a reference fixture; the local agent should map it to SQLAlchemy models in the existing application rather than creating a second production database.

| Entity | Important fields | Meaning and relationships |
|---|---|---|
| Institution | id, name, normalized_name, region, is_new, public_reference_id | Stable fictional institution ID. Names are for display/search, never identity matching. Public reference ID is null in this kit. |
| User profile | id, username, role, region, institution_id, committee | Five proposed role types. Scope supports later permission checks. No credentials or login functionality included. |
| Application | id, institution_id, route_code, current_stage, status, submitted_at, submission_key | Belongs to an institution. Route determines allowed stages. Submission key makes repeat ingestion idempotent. |
| Obligation | id, application_id, type, owner_user_id, rule_id, rule_version, base_due_at, status | One accountable action owned by one user. Composite rule reference pins the applied version. All due dates are timezone-aware instants. |
| Obligation clock fields | paused_seconds, paused_at | Completed paused time is supported by interval rows. Active pause freezes processing time for pausable stage tasks only. It must not erase an existing breach. |
| Evidence fields | evidence_status, renewal_due_at, closed_at | Upload/submission is separate from verification. A pending renewal never changes active expiry. Completion requires a completion timestamp. |
| Document metadata | id, application_id, institution_id, obligation_id, document_type, issued_at, expires_at, verification_status, renewal_expires_at, evidence_file | Links a document to its application and validity obligation. The example text file is fictional, not a legal document or encrypted storage service. |
| Rule | id, version, obligation_type, label, reminder_days, warning_days, escalation_days, pausable, default_duration_days, validation_status | Versioned demo settings. Current rules are explicitly unvalidated. Routes are also recorded in the bundle's configuration. |
| Notification | id, obligation_id, recipient_user_id, channel, delivery_status, why, deduplication_key | Schema only; zero messages are seeded. Later delivery needs an outbox, uniqueness constraint and recipient-scope checks. |
| Audit event | id, application_id, actor_user_id, actor_label, action, occurred_at, reason, previous_state, resulting_state | Synthetic setup/history only. The live application must add real actor checks, actual record time and a protected append path. |
| Pause interval | id, obligation_id, started_at, ended_at, reason | Records why the proposed stage timer paused. A null end means still paused. Completed intervals sum to paused_seconds. |
| Demo clock | id=1, now_at | Persistent simulated time. Separate from the operating system clock and from actual audit-record time. |

Every operational fixture row also carries `source_type`, `source_record_id`, `scenario_group`, and `generator_version`. All operational source types are `synthetic`. Evaluation inputs use `synthetic_evaluation`; their labels separately identify `manual_specification` or assistant-authored specification. Public URLs and access observations live in `source_catalog.json`, not in operational failure records.

In a later authorized public-reference import, use a separate namespace/table and `source_type=public_reference`, with URL, retrieval date, licence/access note and source snapshot hash. Do not equate an AISHE code with an AICTE identifier or attach fictional non-compliance to a real institution. The current fixture loader intentionally accepts synthetic operational data only.

## Validation and normalization

1. IDs use explicit `DEMO-` namespaces. Institution names can be similar; identifiers must still differ. Missing IDs go to manual correction, not fuzzy auto-linking.
2. Trim surrounding whitespace, collapse repeated name spaces and normalize identifier casing. Preserve human-readable names for display.
3. In JSON, missing values use null. CSV blank fields become null during import. Do not turn missing owners, due dates or rules into invented defaults.
4. Required links use foreign keys. Enforce them on every SQLite connection. A document's institution must agree with its application.
5. All timestamps require an offset and normalize to UTC. Display in Asia/Kolkata in the future interface. The demo uses calendar days, not a verified working-day/holiday calendar.
6. Date-only expiry must have a documented local cutoff. One evaluation example explicitly converts India end-of-day to UTC. The code does not silently guess that cutoff.
7. Expiry cannot precede issue date. A pause cannot have negative duration; active pause start must not be in the future. The completed-pause summary must match its supporting intervals.
8. A stage must belong to its route. `SAC_SHC` is a demo grouping label from the Word plan; it is not evidence that SAC and SHC are legally interchangeable. An authorized configuration must select the applicable committee and sequence before real use.
9. Same submission key plus identical normalized content is a repeat to skip. The same key with conflicting content needs review. Different submissions by the same institution remain separate requests.
10. The importer writes accepted, skipped or quarantined outcomes with reasons. It never overwrites a conflicting application, merges records or guesses an owner.

## Explicit demonstration clock semantics

- Reminder at 15 calendar days remaining; warning at seven days remaining.
- The exact due instant is `due_now`. It becomes overdue strictly after that instant. At seven days overdue it is escalated. This boundary choice is an explicit demo clarification, not a verified official SLA.
- Stage tasks can pause under the proposed return rule. Effective due equals original due plus completed pause duration; while paused, evaluate at the pause-start instant. A breach already present before the pause remains visible.
- Undertaking and document rules are fixed-deadline examples. A processing return does not extend a lease. A pending evidence upload does not close a requirement.
- A later expiry is applied only when renewal evidence is explicitly marked verified. Preserve original evidence and expiry history in the application integration.
- Missing owner, due date, known rule version or valid timestamp produces `unknown` and manual correction. It does not authorize a notification or statutory decision.
- Rule changes must not silently modify obligations already pinned to an earlier version. The application will need a separately audited migration/override action.

These semantics are supported by offline specification checks only. They do not validate the underlying administrative policy.
