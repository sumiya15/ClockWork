# Observed verification and limits

Verified here on 25 October 2026 using Python 3.12.14, Linux, and Python's standard library. This is not a Windows run or a test of your local FastAPI project.

## Checks actually run

- `python -m unittest discover -s clockwork-data-starter/tests -v`: 17 tests passed.
- `python clockwork-data-starter/scripts/evaluate.py`: 25/25 synthetic rule specification examples passed, including eight expected unknown/manual-correction cases.
- Binary overdue comparison applies to 17 examples only. Naive original-date baseline: 6 true positives, 8 true negatives, 3 false positives, 0 false negatives. Reference rules: 6 true positives, 11 true negatives, 0 false positives, 0 false negatives.
- `python clockwork-data-starter/scripts/import_quality.py`: 12/12 import-quality expectations passed. Three accepted, one exact repeated submission skipped, eight quarantined for manual correction.
- Synthetic reference SQLite fixture created with 40 applications, 56 obligations, eight institutions, 16 identity profiles, eight document metadata records, three rules, 44 synthetic setup/history events and two pause intervals. Notifications: zero.
- Tests covered byte-identical regeneration with a fixed clock; repeated seeding; preserving an edited institution and demo clock; rejecting orphan foreign keys and non-synthetic input; guarding an existing non-fixture database; and persistence across two separate seeding processes.
- Original uploaded Word blueprint was copied byte-for-byte and its SHA-256 recorded in blueprint_provenance.json.

## What these results mean

The results establish consistency with the stated demonstration specification on crafted examples. Labels were authored by the assistant from explicit demo rules and need team review. This is not blind evaluation, an independent operational benchmark, official AICTE validation or measured real-world accuracy. Do not describe it as 100% accuracy. No model was trained.

The baseline is deliberately simple and fully described. Its three false positives demonstrate cases it omits, not superiority over existing government software or other teams. Real false-positive/missed-action rates remain unknown.

## Implemented in this kit

- Deterministic fictional fixture generator, CSV/JSON data, provenance and supporting pause intervals.
- Conservative offline import checks with explainable quarantine outcomes.
- Separate reference SQLite seeding with foreign keys and preservation of existing rows.
- Pure deadline snapshot function with original/adjusted due dates, type-specific pause handling, rule reference, owner and reason.
- Separate rule specification inputs/labels and a basic comparison report.
- Data dictionary, source catalog, build handoff and provisional recording plan.

## Pending in the ClockWork application

- Independent review of the actual Windows backend files.
- Application SQLAlchemy models and integration of this fixture data.
- Authentication, password hashing, sessions and server-enforced role scopes.
- Authorized workflow actions, return/resubmission and reliable live audit events.
- Scheduler, notification outbox, actual notification deduplication and delivery.
- Full event replay/rule simulation UI. The kit computes snapshots only.
- Scoped upload tokens, secure encrypted document storage, officer verification and file access.
- React screens, filtered reports, communications templates and tested browser behaviour.
- Hash-chained audit implementation or external anchoring. Synthetic plain events are not tamper-proof.
- Real AICTE integration, external email/SMS/WhatsApp and any real operational pilot.
- Validation of the example rules against applicable APH, addenda and authorized procedures.
- Final official video duration/format and a recording of working application features.
