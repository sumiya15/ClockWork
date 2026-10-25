"""Explicit non-overwriting synthetic seed; never runs at API startup."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from backend.app.db.transactions import mutate
from backend.app.modules.auth.service import passwords
from backend.app.db.lifecycle import connect, initialize
from backend.app.core.settings import Settings
from backend.app.modules.obligations.schemas import Obligation
from backend.app.modules.rules.service import load_seed, publish_seed
from backend.app.engine.timing import baseline_due

DEMO_PASSWORD = 'ClockWork-Demo-Only-2026!'


def identifier(number):
    return f'{number:024x}'


def seed(db):
    if not db.name.startswith(('clockwork_demo_', 'clockwork_test_')):
        raise ValueError('Seed is limited to isolated demo/test databases')
    rule = load_seed()
    now = datetime.now(timezone.utc)
    business_at = datetime(2026, 10, 25, tzinfo=timezone.utc)
    common = {'schema_version': 1, 'version': 1, 'demo': True, 'created_at': now, 'updated_at': now}
    users, institutions, applications, obligations = [], [], [], []
    roles = [('bureau.demo', 'bureau_officer', None, None, None, 200),
             ('admin.demo', 'admin', None, None, None, 201),
             ('committee_1.demo', 'committee', None, None, 'DEMO-EVC', 202),
             ('committee_2.demo', 'committee', None, None, 'DEMO-SAC-SHC', 203)]
    for i, route in enumerate(rule.routes, 1):
        iid, aid, oid = identifier(i), identifier(1000 + i), identifier(2000 + i)
        region = f'DEMO-REGION-{chr(64+i)}'
        institutions.append({'_id': iid, 'name': f'Demo Institute {i}', 'region': region,
                             'is_new': i % 2 == 1, **common})
        roles.extend([(f'institution_{i}.demo', 'institution', None, iid, None, 100+i),
                      (f'regional_{i}.demo', 'regional_officer', region, None, None, 110+i)])
        stage = rule.routes[route][0]
        kind = rule.stage_obligations[stage][0]
        committee_id = 'DEMO-EVC' if stage == 'EVC' else None
        owner = identifier(202 if committee_id else 110+i)
        started = business_at - timedelta(days=rule.timings[kind].duration_days + 2 - i * 3)
        due = baseline_due(started, rule.timings[kind].duration_days, rule.timezone)
        applications.append({'_id': aid, 'institution_id': iid, 'region': region,
                             'route_code': route, 'rule_id': rule.rule_id, 'rule_version': rule.version,
                             'current_stage': stage, 'state': 'in_progress',
                             'submitted_at': started, 'sac_shc_committee_id': 'DEMO-SAC-SHC', **common})
        model = Obligation(id=oid, application_id=aid, institution_id=iid, region=region,
                           owner_user_id=owner, committee_id=committee_id, kind=kind, state='open',
                           evidence_state='not_required', rule_id=rule.rule_id, rule_version=rule.version,
                           baseline_due_at=due, active_due_at=due, started_at=started,
                           creation_key=f'seed:{aid}:{kind}:1', **common)
        obligations.append({'_id': oid, **model.model_dump(exclude={'id'})})
    for username, role, region, institution_id, committee_id, number in roles:
        users.append({'_id': identifier(number), 'username': username, 'role': role, 'region': region,
                      'institution_id': institution_id, 'committee_id': committee_id,
                      'active': True, 'password_hash': passwords.hash(DEMO_PASSWORD), **common})

    def operation(session):
        publish_seed(db, rule, session)
        for name, records in [('institutions', institutions), ('users', users),
                              ('applications', applications), ('obligations', obligations)]:
            for record in records:
                db[name].update_one({'_id': record['_id']}, {'$setOnInsert': record}, upsert=True, session=session)
        db.checkpoints.update_one({'_id': 'demo_clock'}, {'$setOnInsert': {
            'business_at': business_at, 'version': 1, 'schema_version': 1}}, upsert=True, session=session)
    mutate(db, actor='development-seed', institution=None, action='demo.seed', resource='seed-v1',
           correlation_id=str(uuid4()), reason='Explicit non-overwriting development seed',
           business_at=business_at, operation=operation)


def main():
    settings = Settings()
    if settings.mode != 'demo':
        raise SystemExit('Seed requires demo mode')
    with connect(settings) as client:
        db = client[settings.mongo_database]
        initialize(db)
        seed(db)
    print('Synthetic seed completed; existing records and passwords were preserved.')


if __name__ == '__main__':
    main()
