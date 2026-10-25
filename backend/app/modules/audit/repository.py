"""The head write serializes ALL audited transactions across processes."""
from pymongo import ReturnDocument


def reserve(db, session):
    head = db.checkpoints.find_one_and_update(
        {'_id': 'audit_head'}, {'$inc': {'sequence': 1}},
        return_document=ReturnDocument.AFTER, session=session)
    if head is None:
        raise RuntimeError('Audit head is missing; refusing mutation')
    return head


def append(db, session, entry):
    db.audit_events.insert_one(entry, session=session)
    db.checkpoints.update_one({'_id': 'audit_head'}, {'$set': {'current_hash': entry['current_hash']}}, session=session)
