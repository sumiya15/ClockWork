"""Atomic domain + audit + outbox transaction; serialized by MongoDB head write."""
from datetime import datetime, timezone
from bson import ObjectId
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from ..modules.audit import repository
from ..modules.audit.service import digest


def mutate(db, *, actor, institution, action, resource, correlation_id, operation,
           role='system', scope=None, reason='System operation', business_at=None, jobs=()):
    """Callback must contain only MongoDB operations using the provided session.

    PyMongo may retry it on write conflict. Never perform external effects here.
    The head is written FIRST, before reading mutable authorization/domain data.
    """
    def transaction(session):
        head = repository.reserve(db, session)
        result = operation(session)
        from ..modules.notifications.repository import enqueue
        for job in jobs:
            enqueue(db, job, session)
        entry = {'_id': ObjectId(), 'kind': 'entry', 'schema_version': 1,
                 'sequence': head['sequence'], 'previous_hash': head['current_hash'],
                 'actor': actor, 'institution_id': institution, 'action': action,
                 'role': role, 'scope': scope or {}, 'reason': reason,
                 'business_at': business_at.isoformat() if business_at else None,
                 'resource': resource, 'correlation_id': correlation_id,
                 'timestamp': datetime.now(timezone.utc).isoformat(timespec='microseconds'),
                 'payload': {}}
        entry['current_hash'] = digest(entry)
        repository.append(db, session, entry)
        return result
    with db.client.start_session() as session:
        return session.with_transaction(transaction, read_concern=ReadConcern('snapshot'),
                                        write_concern=WriteConcern('majority'))


