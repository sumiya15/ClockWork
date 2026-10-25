from datetime import datetime, timezone


def get(db, rule_id, version, session=None):
    return db.rule_sets.find_one({'rule_id': rule_id, 'version': version}, session=session)


def insert(db, rule, session):
    db.rule_sets.insert_one({'_id': f'{rule.rule_id}:{rule.version}', **rule.model_dump(),
                             'schema_version': 1, 'status': 'published',
                             'published_at': datetime.now(timezone.utc)}, session=session)


def published(db):
    return list(db.rule_sets.find({'status': 'published'}).sort([('rule_id', 1), ('version', 1)]).limit(100))
