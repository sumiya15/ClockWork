"""Validate and insert canonical synthetic fixtures; never update existing rows."""
import json
from collections import defaultdict

from sqlalchemy import Boolean, Integer, String, func, select
from sqlalchemy.orm import Session

from .database import CONFIG_PATH, PROJECT_ROOT, initialize, write_lock
from .models import MODELS, Application, DemoClock, UTCInstant, utc
from .passwords import DEMO_PASSWORD, hash_password

BUNDLE_PATH = PROJECT_ROOT / "clockwork-data-starter/data/demo/demo_bundle.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_bundle(bundle):
    """Reject the entire malformed batch before writing, with an explicit reason."""
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    meta = bundle["metadata"]
    require(meta["source_type"] == "synthetic" and meta["real_operational_records"] == 0,
            "Only explicitly synthetic operational fixtures are accepted")
    now = utc(meta["as_of"])
    require(bundle["routes"] == config["routes"], "Routes differ from reviewed demo configuration")
    require(bundle["rules"] == config["rules"], "Rules differ from versioned demo configuration")
    lookup = {}
    for model in MODELS:
        table = model.__tablename__
        rows = bundle[table]
        require(isinstance(rows, list), f"{table}: expected a list")
        keys = {}
        for row in rows:
            require(isinstance(row, dict), f"{table}: expected an object")
            columns = model.__table__.columns
            require(not set(row) - set(columns.keys()), f"{table}: unexpected fields")
            require("password_hash" not in row, "Credentials must not come from fixture JSON")
            for col in columns:
                value = row.get(col.name)
                if col.name == "password_hash":
                    continue
                require(value is not None or col.nullable, f"{table}: missing {col.name}")
                if value is None:
                    continue
                if isinstance(col.type, UTCInstant):
                    utc(value)
                elif isinstance(col.type, Boolean):
                    require(type(value) is bool, f"{table}: {col.name} must be boolean")
                elif isinstance(col.type, Integer):
                    require(type(value) is int, f"{table}: {col.name} must be integer")
                elif isinstance(col.type, String):
                    require(isinstance(value, str) and bool(value.strip()), f"{table}: invalid {col.name}")
            require(row['id'].startswith('DEMO-') and row['source_type'] == 'synthetic', f"{table}: invalid provenance")
            key = (row['id'], row['version']) if table == 'rules' else row['id']
            require(key not in keys, f"{table}: duplicate identity {key}")
            keys[key] = row
        lookup[table] = keys
    institutions, users, apps, obligations, rules = (lookup[k] for k in ('institutions','users','applications','obligations','rules'))
    regions = {r['region'] for r in institutions.values()}
    usernames, submissions = set(), set()
    for row in users.values():
        role = row['role']
        require(role in {'administrator','bureau_officer','regional_officer','committee','institution'}, 'Unknown role')
        require(row['username'] not in usernames, 'Duplicate username')
        usernames.add(row['username'])
        require(row['institution_id'] is None or row['institution_id'] in institutions, 'Unknown user institution')
        require(row['region'] is None or row['region'] in regions, 'Unknown user region')
        require(role != 'regional_officer' or row['region'] is not None, 'Missing regional scope')
        require(role != 'committee' or row['committee'] is not None, 'Missing committee scope')
        require(role != 'institution' or row['institution_id'] is not None, 'Missing institution scope')
        if row['institution_id'] and row['region']:
            require(institutions[row['institution_id']]['region'] == row['region'], 'User institution/region mismatch')
    for row in apps.values():
        require(row['institution_id'] in institutions, 'Unknown application institution')
        require(row['current_stage'] in config['routes'].get(row['route_code'], []), 'Invalid route/stage')
        require(row['submission_key'] not in submissions, 'Duplicate submission key needs manual review')
        submissions.add(row['submission_key'])
        require(utc(row['submitted_at']) <= now, 'Future submission')
        require(row['status'] in {'in_progress','returned_for_deficiency','awaiting_authorised_decision'}, 'Unknown fixture application state')
    for row in obligations.values():
        require(row['application_id'] in apps and row['owner_user_id'] in users, 'Broken obligation reference')
        rule = rules.get((row['rule_id'], row['rule_version']))
        require(rule is not None and rule['obligation_type'] == row['type'], 'Unknown/mismatched rule version')
        require(row['status'] in {'open','completed'} and row['paused_seconds'] >= 0, 'Invalid obligation state/pause')
        require(row['evidence_status'] in {'not_required','not_submitted','submitted','verified','rejected'}, 'Invalid evidence status')
        require(row['status'] != 'completed' or row['closed_at'] is not None, 'Completion needs timestamp')
        require(row['closed_at'] is None or utc(row['closed_at']) <= now, 'Future completion')
        require(rule['pausable'] or (row['paused_seconds'] == 0 and row['paused_at'] is None), 'Fixed deadline cannot pause')
    intervals = defaultdict(list)
    for row in lookup['pause_intervals'].values():
        require(row['obligation_id'] in obligations, 'Unknown paused obligation')
        start, end = utc(row['started_at']), utc(row['ended_at']) if row['ended_at'] else None
        require(start <= now and (end is None or start <= end <= now), 'Invalid pause chronology')
        intervals[row['obligation_id']].append((start, end))
    for oid, row in obligations.items():
        spans = sorted(intervals[oid])
        total, active, previous_end = 0, None, None
        for index, (start, end) in enumerate(spans):
            require(index == 0 or (previous_end is not None and start >= previous_end), 'Overlapping pauses')
            if end is None:
                active = start
            else:
                total += (end-start).total_seconds()
            previous_end = end
        require(total == row['paused_seconds'], 'Pause total does not match intervals')
        require(active == (utc(row['paused_at']) if row['paused_at'] else None), 'Active pause does not match intervals')
    for row in lookup['documents'].values():
        app, obligation = apps.get(row['application_id']), obligations.get(row['obligation_id'])
        require(app is not None and app['institution_id'] == row['institution_id'], 'Document institution mismatch')
        require(obligation is not None and obligation['application_id'] == row['application_id'] and obligation['type'] == 'document', 'Document obligation mismatch')
        require(utc(row['issued_at']) <= utc(row['expires_at']), 'Expiry precedes issue')
        require(row['verification_status'] == obligation['evidence_status'], 'Document evidence state mismatch')
        require(utc(row['expires_at']) == utc(obligation['base_due_at']), 'Document expiry mismatch')
    require(not bundle['notifications'], 'Initial fixtures cannot claim notifications were delivered')
    for row in lookup['audit_events'].values():
        require(row['application_id'] in apps, 'Unknown audit application')
        require(row['actor_user_id'] is None or row['actor_user_id'] in users, 'Unknown audit actor')
        require(utc(row['occurred_at']) <= now, 'Future audit event')


def seed(engine, bundle):
    try:
        validate_bundle(bundle)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Rejected synthetic batch: {exc}; no seed rows written") from exc
    initialize(engine)
    report = {'inserted': {}, 'skipped_existing': {}, 'preserved_differences': []}
    with Session(engine) as session, session.begin():
        # A write lock makes check-and-insert safe against concurrent seed commands.
        write_lock(session)
        for model in MODELS:
            table = model.__tablename__
            inserted = skipped = 0
            for row in bundle[table]:
                key = (row['id'], row['version']) if table == 'rules' else row['id']
                existing = session.get(model, key)
                if existing is not None:
                    differences = [k for k, v in row.items() if getattr(existing, k) !=
                                   (utc(v) if isinstance(model.__table__.columns[k].type, UTCInstant) and v is not None else v)]
                    if differences:
                        report['preserved_differences'].append({'table': table, 'id': row['id'], 'fields': differences})
                    skipped += 1
                    continue
                if model is Application:
                    conflict = session.scalar(select(Application).where(Application.submission_key == row['submission_key']))
                    require(conflict is None, 'Submission key conflicts with a different application; manual review required')
                values = dict(row)
                if table == 'users':
                    values['password_hash'] = hash_password(DEMO_PASSWORD)
                session.add(model(**values))
                inserted += 1
            session.flush()
            report['inserted'][table] = inserted
            report['skipped_existing'][table] = skipped
        if engine.dialect.name == 'sqlite':
            require(not session.connection().exec_driver_sql('PRAGMA foreign_key_check').all(), 'Foreign key check failed')
        report['counts'] = {m.__tablename__: session.scalar(select(func.count()).select_from(m)) for m in MODELS}
        report['demo_clock'] = session.get(DemoClock, 1).now_at.isoformat()
    return report
