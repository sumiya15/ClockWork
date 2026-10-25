"""Initialize only the explicit local development replica set, never a user URI."""
import time
from pymongo import MongoClient
from pymongo.errors import OperationFailure

with MongoClient('mongodb://127.0.0.1:27018/?directConnection=true', serverSelectionTimeoutMS=2000) as client:
    try:
        client.admin.command('replSetInitiate', {'_id':'rs0', 'members':[{'_id':0,'host':'127.0.0.1:27018'}]})
    except OperationFailure as exc:
        if exc.code != 23:  # AlreadyInitialized; never reconfigure an existing set.
            raise
    for _ in range(30):
        if client.admin.command('hello').get('isWritablePrimary'):
            print('Local rs0 primary ready on port 27018')
            break
        time.sleep(1)
    else:
        raise SystemExit('Replica set did not become writable')
