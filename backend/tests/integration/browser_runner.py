"""Launch a disposable seeded API for Playwright; clean up only this run's DB."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.request import urlopen
from uuid import uuid4
from pymongo import MongoClient
from backend.app.db.lifecycle import initialize
from backend.scripts.seed import seed


def main():
    root = Path(__file__).resolve().parents[3]
    # Never connect the browser tests to an already running API.
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 8002))
    name = 'clockwork_test_browser_' + uuid4().hex
    uri = 'mongodb://127.0.0.1:27018/?replicaSet=rs0'
    client = MongoClient(uri, tz_aware=True, serverSelectionTimeoutMS=2000)
    process = None
    try:
        initialize(client[name])
        seed(client[name])
        print('Disposable browser database seeded.', flush=True)
        env = {**os.environ, 'CW_MONGO_URI':uri, 'CW_MONGO_DATABASE':name, 'CW_MODE':'demo',
               'CW_COOKIE_SECURE':'false', 'CW_ALLOWED_ORIGINS':'["http://127.0.0.1:5173"]'}
        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        process = subprocess.Popen([sys.executable,'-m','uvicorn','backend.app.main:app','--host','127.0.0.1',
                                    '--port','8002','--no-access-log'], cwd=root, env=env, creationflags=flags)
        for _ in range(40):
            try:
                with urlopen('http://127.0.0.1:8002/api/v1/health/ready',timeout=1) as response:
                    if response.status == 200:
                        break
            except OSError:
                time.sleep(0.25)
        else:
            raise RuntimeError('Disposable API failed to become ready')
        print('Disposable API ready; running Playwright.', flush=True)
        result = subprocess.run(['node','node_modules/@playwright/test/cli.js','test'],
                                cwd=root/'frontend', env=env, creationflags=flags, timeout=90)
        return result.returncode
    finally:
        if process:
            process.terminate()
            process.wait(timeout=10)
        assert name.startswith('clockwork_test_browser_')
        client.drop_database(name)
        client.close()


if __name__ == '__main__':
    raise SystemExit(main())
