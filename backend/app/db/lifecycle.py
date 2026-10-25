"""One pooled synchronous PyMongo client; sync routes run in FastAPI's thread pool."""
from pymongo import MongoClient
from .indexes import ensure_indexes

COLLECTIONS = ('users', 'institutions', 'applications', 'obligations', 'stage_events',
               'evc_visits', 'undertakings', 'document_metadata', 'evidence_submissions',
               'rule_sets', 'communication_templates', 'notification_jobs', 'audit_events',
               'magic_links', 'sessions', 'checkpoints')


def connect(settings):
    return MongoClient(settings.mongo_uri.get_secret_value(), tz_aware=True,
                       serverSelectionTimeoutMS=2000, connectTimeoutMS=2000)


def initialize(db):
    hello = db.client.admin.command('hello')
    if not hello.get('setName') or not hello.get('isWritablePrimary'):
        raise RuntimeError('A writable replica set is required')
    existing = db.list_collection_names()
    for name in COLLECTIONS:
        if name not in existing:
            try:
                db.create_collection(name)
            except Exception:
                if name not in db.list_collection_names():
                    raise
    ensure_indexes(db)
