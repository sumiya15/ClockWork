import hashlib
import json
from pymongo.read_concern import ReadConcern


def digest(entry):
    # All hashed values are JSON scalars; timestamp is a UTC ISO string.
    body = {k: v for k, v in entry.items() if k not in ('_id', 'current_hash')}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False, allow_nan=False).encode('utf-8')).hexdigest()


def verify(db):
    # A snapshot avoids false failures when a writer commits during verification.
    with db.client.start_session() as session:
        with session.start_transaction(read_concern=ReadConcern('snapshot')):
            previous, sequence = '0' * 64, 0
            for entry in db.audit_events.find({}, session=session).sort('sequence', 1):
                sequence += 1
                if entry['sequence'] != sequence or entry['previous_hash'] != previous or digest(entry) != entry['current_hash']:
                    return False
                previous = entry['current_hash']
            head = db.checkpoints.find_one({'_id': 'audit_head'}, session=session)
            return bool(head and head['sequence'] == sequence and head['current_hash'] == previous)
