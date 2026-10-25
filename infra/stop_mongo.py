"""Graceful local demo shutdown, limited to this workspace's mongod dbpath."""
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import AutoReconnect

expected = (Path(__file__).resolve().parents[1] / '.local/mongo-demo-data').resolve()
with MongoClient('mongodb://127.0.0.1:27018/?directConnection=true',serverSelectionTimeoutMS=2000) as client:
    options = client.admin.command('getCmdLineOpts')['parsed']
    actual = Path(options.get('storage', {}).get('dbPath', '')).resolve()
    if actual != expected:
        raise SystemExit('Refusing shutdown: server dbpath is not this workspace demo')
    try:
        client.admin.command({'shutdown':1})
    except AutoReconnect:
        pass  # Expected: server closes its socket during graceful shutdown.
print('Workspace MongoDB stopped; its data was retained.')
