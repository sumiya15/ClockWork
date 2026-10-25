"""Application checks only. Never connect to/reset the normal demonstration DB."""
import copy
from contextlib import closing
import json
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database import PROJECT_ROOT, database_path, demo_now, engine_for, initialize
from backend.data_cli import inspect_data
from backend.models import Application, DemoClock, Institution, Obligation, User, utc
from backend.passwords import DEMO_PASSWORD, verify_password
from backend.seed import BUNDLE_PATH, seed

EXPECTED = {'institutions': 8, 'users': 16, 'rules': 3, 'applications': 40,
            'obligations': 56, 'documents': 8, 'notifications': 0,
            'audit_events': 44, 'pause_intervals': 2}


class DataFoundationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'application.sqlite3'
        self.engine = engine_for(self.path)
        self.bundle = json.loads(BUNDLE_PATH.read_text(encoding='utf-8'))

    def tearDown(self):
        self.engine.dispose()
        self.tmp.cleanup()

    def test_counts_relationships_scopes_and_scenario_coverage(self):
        result = seed(self.engine, self.bundle)
        self.assertEqual(result['counts'], EXPECTED)
        with Session(self.engine) as s:
            self.assertEqual(len(set(s.scalars(select(Institution.region)))), 4)
            self.assertEqual(len(set(s.scalars(select(User.role)))), 5)
            self.assertEqual(s.get(Application, 'DEMO-APP-001').institution.id, 'DEMO-INST-001')
            obligation = s.get(Obligation, 'DEMO-OBL-001-STAGE')
            self.assertEqual(obligation.owner.role, 'committee')
            self.assertEqual(obligation.rule.version, 1)
            self.assertEqual(len(obligation.pauses), 1)
            self.assertEqual(obligation.paused_seconds, 259200)
            now = demo_now(s)
            obligations = s.scalars(select(Obligation)).all()
            self.assertTrue(any(o.base_due_at > now for o in obligations))
            self.assertTrue(any(o.base_due_at < now and o.status == 'open' for o in obligations))
            self.assertTrue(any(o.type == 'undertaking' and o.status == 'open' for o in obligations))
            self.assertTrue({'SCRUTINY','EVC'} <= set(s.scalars(select(Application.current_stage))))
        with self.engine.connect() as c:
            self.assertEqual(c.exec_driver_sql('PRAGMA foreign_key_check').all(), [])
            self.assertGreater(c.exec_driver_sql("SELECT COUNT(*) FROM documents WHERE expires_at > '2026-10-25' AND expires_at < '2026-11-25'").scalar(), 0)

    def test_second_seed_preserves_all_rows_hashes_edits_and_clock(self):
        seed(self.engine, self.bundle)
        with Session(self.engine) as s, s.begin():
            s.get(Institution, 'DEMO-INST-001').name = 'Manually edited synthetic institution'
            s.get(Application, 'DEMO-APP-001').status = 'manual_review'
            s.get(DemoClock, 1).now_at = '2026-11-12T00:00:00Z'
            old_hash = s.get(User, 'DEMO-USER-ADMIN').password_hash
        result = seed(self.engine, self.bundle)
        self.assertEqual(result['counts'], EXPECTED)
        self.assertEqual(sum(result['inserted'].values()), 0)
        self.assertEqual(len(result['preserved_differences']), 2)
        with Session(self.engine) as s:
            self.assertEqual(s.get(Institution, 'DEMO-INST-001').name, 'Manually edited synthetic institution')
            self.assertEqual(s.get(Application, 'DEMO-APP-001').status, 'manual_review')
            self.assertEqual(demo_now(s), utc('2026-11-12T00:00:00Z'))
            self.assertEqual(s.get(User, 'DEMO-USER-ADMIN').password_hash, old_hash)

    def test_passwords_salted_and_no_hashes_in_inspection(self):
        seed(self.engine, self.bundle)
        with Session(self.engine) as s:
            hashes = list(s.scalars(select(User.password_hash)))
        self.assertEqual(len(set(hashes)), 16)
        self.assertTrue(all(verify_password(DEMO_PASSWORD, h) for h in hashes))
        self.assertFalse(verify_password('wrong password', hashes[0]))
        self.assertNotIn(DEMO_PASSWORD.encode(), self.path.read_bytes())
        report = json.dumps(inspect_data(self.path))
        self.assertNotIn('scrypt$', report)
        self.assertNotIn(DEMO_PASSWORD, report)

    def test_fk_unique_keys_and_document_scope_enforced_by_database(self):
        seed(self.engine, self.bundle)
        bad_statements = [
            "UPDATE obligations SET owner_user_id='MISSING' WHERE id='DEMO-OBL-001-STAGE'",
            "UPDATE obligations SET rule_version=999 WHERE id='DEMO-OBL-001-STAGE'",
            "UPDATE applications SET submission_key='DEMO-SUBMISSION-001' WHERE id='DEMO-APP-002'",
            "UPDATE documents SET institution_id='DEMO-INST-002' WHERE id='DEMO-DOC-001'",
            "UPDATE documents SET obligation_id='DEMO-OBL-002-DOCUMENT' WHERE id='DEMO-DOC-001'",
            "UPDATE users SET institution_id=NULL WHERE role='institution'",
        ]
        for sql in bad_statements:
            with self.subTest(sql=sql), self.assertRaises(IntegrityError):
                with self.engine.begin() as c:
                    self.assertEqual(c.exec_driver_sql('PRAGMA foreign_keys').scalar(), 1)
                    c.execute(text(sql))
        with self.engine.connect() as c:
            indexes = c.exec_driver_sql('PRAGMA index_list(notifications)').all()
            self.assertTrue(any(row[2] for row in indexes))

    def test_malformed_batches_rejected_without_writes(self):
        seed(self.engine, self.bundle)
        mutations = [
            lambda b: b['metadata'].update(source_type='public_reference'),
            lambda b: b['obligations'][0].update(owner_user_id='MISSING'),
            lambda b: b['obligations'][0].update(base_due_at='2026-10-24'),
            lambda b: b['obligations'][0].update(paused_seconds=99),
            lambda b: b['applications'][0].update(current_stage='INVALID'),
            lambda b: b['applications'][1].update(submission_key=b['applications'][0]['submission_key']),
            lambda b: b['documents'][0].update(institution_id='DEMO-INST-002'),
            lambda b: b['documents'][0].update(issued_at='2028-01-01T00:00:00Z'),
            lambda b: b['users'][0].update(password_hash='plaintext'),
            lambda b: b['pause_intervals'][0].update(ended_at='2026-10-19T00:00:00Z'),
        ]
        for mutate in mutations:
            b = copy.deepcopy(self.bundle)
            mutate(b)
            with self.assertRaises(ValueError):
                seed(self.engine, b)
            self.assertEqual(inspect_data(self.path)['counts'], EXPECTED)

    def test_transaction_rolls_back_partial_insert_on_existing_unique_conflict(self):
        seed(self.engine, self.bundle)
        with Session(self.engine) as s, s.begin():
            s.get(User, 'DEMO-USER-ADMIN').username = 'new.synthetic'
        b = copy.deepcopy(self.bundle)
        institution = dict(b['institutions'][0], id='DEMO-INST-EXTRA')
        b['institutions'].append(institution)
        b['users'].append(dict(b['users'][0], id='DEMO-USER-EXTRA', username='new.synthetic'))
        with self.assertRaises(IntegrityError):
            seed(self.engine, b)
        self.assertEqual(inspect_data(self.path)['counts'], EXPECTED)
        with Session(self.engine) as s:
            self.assertIsNone(s.get(Institution, 'DEMO-INST-EXTRA'))

    def test_unrelated_database_is_untouched(self):
        with closing(sqlite3.connect(self.path)) as con, con:
            con.execute('CREATE TABLE unrelated(id INTEGER)')
        before = self.path.read_bytes()
        with self.assertRaises(ValueError):
            seed(self.engine, self.bundle)
        self.assertEqual(before, self.path.read_bytes())

    def test_initialize_is_idempotent_and_does_not_seed(self):
        initialize(self.engine)
        with Session(self.engine) as s, s.begin():
            s.get(DemoClock, 1).now_at = '2027-01-01T00:00:00Z'
        initialize(self.engine)
        result = inspect_data(self.path)
        self.assertTrue(all(v == 0 for v in result['counts'].values()))
        self.assertTrue(result['demo_clock'].startswith('2027-01-01'))

    def test_separate_process_restart_and_different_working_directory(self):
        env = dict(os.environ, PYTHONPATH=str(PROJECT_ROOT))
        command = [sys.executable, '-m', 'backend.data_cli', 'seed', '--db', str(self.path)]
        first = subprocess.run(command, cwd=self.tmp.name, env=env, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(first.stdout)['counts'], EXPECTED)
        edit = "from backend.database import engine_for; from sqlalchemy import text; e=engine_for(r'" + str(self.path) + "');\nwith e.begin() as c:\n c.execute(text(\"UPDATE institutions SET name='Edited in another process' WHERE id='DEMO-INST-001'\")); c.execute(text(\"UPDATE demo_clock SET now_at='2027-01-01T00:00:00+00:00' WHERE id=1\"))\ne.dispose()"
        subprocess.run([sys.executable, '-c', edit], cwd=self.tmp.name, env=env, check=True)
        second = subprocess.run(command, cwd=self.tmp.name, env=env, capture_output=True, text=True, check=True)
        result = json.loads(second.stdout)
        self.assertEqual(sum(result['inserted'].values()), 0)
        self.assertTrue(result['demo_clock'].startswith('2027-01-01'))
        self.assertTrue(any(r['id'] == 'DEMO-INST-001' for r in result['preserved_differences']))
        check_path = subprocess.run([sys.executable, '-c', 'from backend.database import database_path; print(database_path("data/clockwork.sqlite3"))'], cwd=self.tmp.name, env=env, capture_output=True, text=True, check=True)
        self.assertEqual(Path(check_path.stdout.strip()), PROJECT_ROOT / 'data/clockwork.sqlite3')

    def test_fresh_application_http_endpoints_and_no_anonymous_business_api(self):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        env = dict(os.environ, CLOCKWORK_DATABASE_URL='', CLOCKWORK_DB_PATH=str(self.path))
        with tempfile.TemporaryFile(mode='w+') as log:
            process = subprocess.Popen([sys.executable, '-m', 'backend.tests.http_server', '--port',str(port)], cwd=PROJECT_ROOT, env=env, stdin=subprocess.PIPE, text=True, stdout=log, stderr=log)
            try:
                base = f'http://127.0.0.1:{port}'
                deadline = time.monotonic() + 15
                while True:
                    try:
                        with urlopen(base + '/api/health', timeout=1) as r:
                            self.assertEqual(r.status, 200)
                            self.assertEqual(json.load(r), {'status':'ok'})
                        break
                    except URLError:
                        if process.poll() is not None or time.monotonic() > deadline:
                            log.seek(0)
                            self.fail(log.read())
                        time.sleep(.1)
                with urlopen(base + '/') as r:
                    self.assertEqual(r.status, 200)
                    self.assertEqual(json.load(r), {'project':'ClockWork','message':'ClockWork API is running as a student demonstration.','demo_mode':True})
                with urlopen(base + '/docs') as r:
                    body = r.read().decode()
                    self.assertEqual(r.status, 200)
                    self.assertIn('SwaggerUIBundle', body)
                    self.assertIn('/openapi.json', body)
                with urlopen(base + '/openapi.json') as r:
                    self.assertEqual(r.status, 200)
                    schema = json.load(r)
                    self.assertEqual(schema['info']['title'], 'ClockWork API')
                    self.assertIn('local synthetic database', schema['info']['description'])
                    self.assertTrue({'/','/api/health','/api/auth/login','/api/applications'} <= set(schema['paths']))
                for path in ['/api/applications','/api/users','/api/documents']:
                    with self.assertRaises(HTTPError) as err:
                        urlopen(base + path)
                    self.assertEqual(err.exception.code, 401 if path == '/api/applications' else 404)
                    err.exception.close()
                self.assertFalse(self.path.exists(), 'API startup should not silently initialize/seed')
                print(f'Integrated HTTP check passed at {base}; test process stopped afterward')
            finally:
                process.communicate('stop\n', timeout=10)


if __name__ == '__main__':
    unittest.main()
