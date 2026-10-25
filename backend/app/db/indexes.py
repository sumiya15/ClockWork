"""Indexes for implemented query and uniqueness contracts."""


def ensure_indexes(db):
    db.users.create_index('username', unique=True)
    db.sessions.create_index('expires_at', expireAfterSeconds=0)
    db.institutions.create_index([('region', 1), ('_id', 1)])
    for scope in ('region', 'institution_id', 'owner_user_id'):
        db.obligations.create_index([(scope, 1), ('active_due_at', 1), ('_id', 1)])
    db.obligations.create_index([('application_id', 1), ('_id', 1)])
    db.obligations.create_index('creation_key', unique=True)
    db.applications.create_index([('institution_id', 1), ('_id', 1)])
    db.rule_sets.create_index([('rule_id', 1), ('version', 1)], unique=True)
    db.stage_events.create_index('idempotency_key', unique=True)
    db.notification_jobs.create_index('idempotency_key', unique=True)
    db.notification_jobs.create_index([('status', 1), ('next_attempt_at', 1)])
    db.audit_events.create_index('sequence', unique=True)
    if not db.checkpoints.find_one({'_id': 'audit_head'}) and db.audit_events.count_documents({}):
        raise RuntimeError('Audit head is missing; explicit recovery required')
    db.checkpoints.update_one({'_id': 'audit_head'}, {'$setOnInsert': {
        'kind': 'head', 'sequence': 0, 'current_hash': '0' * 64, 'schema_version': 1}}, upsert=True)
