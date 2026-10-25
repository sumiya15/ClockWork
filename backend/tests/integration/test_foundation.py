"""Real MongoDB integration tests. Only generated clockwork_test_* DBs are dropped."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError

from backend.app.main import create_app
from backend.app.core.settings import Settings
from backend.app.db.lifecycle import initialize
from backend.scripts.seed import seed, identifier, DEMO_PASSWORD
from backend.app.modules.auth.guards import COOKIE
from backend.app.modules.auth.service import token_hash
from backend.app.db.transactions import mutate
from backend.app.modules.audit.service import verify
from backend.app.engine.clock import DemoClock, RealClock
from backend.app.modules.rules.service import load_seed, publish_seed
from backend.app.engine.rules import RuleSet
from backend.app.engine.timing import baseline_due
from backend.app.modules.obligations.service import view
from backend.app.modules.notifications.schemas import NotificationJob

URI = 'mongodb://127.0.0.1:27018/?replicaSet=rs0'
HEADERS = {'Origin': 'http://127.0.0.1:5173', 'X-ClockWork-CSRF': '1'}


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.name = 'clockwork_test_' + uuid4().hex
        self.mongo = MongoClient(URI, tz_aware=True, serverSelectionTimeoutMS=2000)
        self.db = self.mongo[self.name]
        initialize(self.db)  # Deliberately fail, not mock/skip, if real replica set is unavailable.
        seed(self.db)
        self.settings = Settings(mongo_uri=URI, mongo_database=self.name)
        self.http = TestClient(create_app(self.settings))
        self.http.__enter__()

    def tearDown(self):
        self.http.__exit__(None, None, None)
        assert self.db.name == self.name and self.name.startswith('clockwork_test_')
        self.mongo.drop_database(self.name)
        self.mongo.close()

    def login(self, username='institution_1.demo'):
        self.http.cookies.clear()
        response = self.http.post('/api/v1/auth/login', headers=HEADERS,
                                  json={'username':username, 'password':DEMO_PASSWORD})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertNotIn('access_token', response.json())
        return response

    def audited(self, operation=lambda session: None, **kwargs):
        return mutate(self.db, actor='test', institution=None, action='test', resource='test',
                      correlation_id=str(uuid4()), operation=operation, **kwargs)

    def test_cookie_csrf_rotation_logout_and_expiry(self):
        self.assertEqual(self.http.get('/api/v1/auth/me').status_code, 401)
        self.assertEqual(self.http.post('/api/v1/auth/login', json={'username':'institution_1.demo','password':DEMO_PASSWORD}).status_code, 403)
        response = self.login()
        self.assertIn('HttpOnly', response.headers['set-cookie'])
        self.assertIn('SameSite=strict', response.headers['set-cookie'])
        first = self.http.cookies.get(COOKIE)
        self.assertIsNotNone(self.db.sessions.find_one({'_id':token_hash(first)}))
        self.assertNotIn(first, str(list(self.db.audit_events.find())))
        response = self.http.post('/api/v1/auth/login', headers=HEADERS,
                                  json={'username':'institution_1.demo','password':DEMO_PASSWORD})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(self.db.sessions.find_one({'_id':token_hash(first)})['revoked_at'])
        active = self.http.cookies.get(COOKIE)
        self.assertEqual(self.http.post('/api/v1/auth/logout', headers=HEADERS, json={}).status_code, 200)
        self.http.cookies.set(COOKIE, active)
        self.assertEqual(self.http.get('/api/v1/auth/me').status_code, 401)
        self.login()
        token = self.http.cookies.get(COOKIE)
        self.db.sessions.update_one({'_id':token_hash(token)}, {'$set':{'expires_at':datetime.now(timezone.utc)-timedelta(seconds=1)}})
        self.assertEqual(self.http.get('/api/v1/auth/me').status_code, 401)  # TTL cleanup not needed.

    def test_all_roles_and_region_institution_committee_isolation(self):
        for name, count in [('institution_1.demo',1), ('institution_2.demo',1),
                            ('regional_1.demo',1), ('regional_2.demo',1),
                            ('committee_1.demo',2), ('committee_2.demo',0), ('bureau.demo',4)]:
            self.login(name)
            response = self.http.get('/api/v1/obligations')
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.json()['total'],count,name)
        self.login('institution_1.demo')
        self.assertEqual(self.http.get('/api/v1/obligations/'+identifier(2002)).status_code,404)
        self.assertEqual(self.http.get('/api/v1/institutions/'+identifier(2)).status_code,404)
        self.assertEqual(self.http.get('/api/v1/rules').status_code,403)
        self.login('admin.demo')
        self.assertEqual(self.http.get('/api/v1/obligations').status_code,403)
        self.assertEqual(self.http.get('/api/v1/rules').status_code,200)
        self.db.users.update_one({'username':'admin.demo'}, {'$set':{'role':'regional_officer','region':None}})
        self.assertEqual(self.http.get('/api/v1/obligations').status_code,403)

    def test_safe_boundaries_pagination_and_no_mass_assignment(self):
        bad = self.http.post('/api/v1/auth/login', headers=HEADERS,
                             json={'username':{'$ne':None}, 'password':'secret-value', 'role':'admin'})
        self.assertEqual(bad.status_code,422)
        self.assertNotIn('secret-value',bad.text)
        self.login('bureau.demo')
        self.assertEqual(self.http.get('/api/v1/obligations?region[$ne]=x').status_code,422)
        self.assertEqual(self.http.get('/api/v1/obligations?limit=101').status_code,422)
        self.assertEqual(self.http.get('/api/v1/obligations/not-an-id').status_code,422)
        page1 = self.http.get('/api/v1/obligations?limit=2').json()
        page2 = self.http.get('/api/v1/obligations?limit=2&offset=2').json()
        self.assertEqual(len({x['id'] for x in page1['items']+page2['items']}),4)
        self.assertNotIn('password_hash',self.http.get('/api/v1/auth/me').text)

    def test_real_unique_index_race(self):
        def attempt(i):
            try:
                self.db.stage_events.insert_one({'idempotency_key':'race', 'value':i})
                return True
            except DuplicateKeyError:
                return False
        with ThreadPoolExecutor(max_workers=6) as pool:
            self.assertEqual(sum(pool.map(attempt,range(12))),1)

    def test_concurrent_audit_writes_across_independent_clients(self):
        def append(i):
            with MongoClient(URI,tz_aware=True) as client:
                mutate(client[self.name], actor='test', institution=None, action='parallel',
                       resource=str(i), correlation_id=str(uuid4()), operation=lambda s: None)
        with ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(append,range(12)))
        self.assertTrue(verify(self.db))
        self.assertEqual(self.db.audit_events.count_documents({}),13)

    def test_audit_failure_rolls_back_session_and_logout(self):
        before = self.db.sessions.count_documents({})
        with patch('backend.app.modules.audit.repository.append', side_effect=RuntimeError('injected')):
            response = self.http.post('/api/v1/auth/login', headers=HEADERS,
                                      json={'username':'institution_1.demo','password':DEMO_PASSWORD})
        self.assertEqual(response.status_code,503)
        self.assertNotIn('set-cookie',response.headers)
        self.assertEqual(self.db.sessions.count_documents({}),before)
        self.login()
        with patch('backend.app.modules.audit.repository.append', side_effect=RuntimeError('injected')):
            self.assertEqual(self.http.post('/api/v1/auth/logout',headers=HEADERS,json={}).status_code,503)
        self.assertEqual(self.http.get('/api/v1/auth/me').status_code,200)
        self.assertTrue(verify(self.db))

    def test_login_scope_change_cannot_commit_stale_audit_identity(self):
        before_sessions = self.db.sessions.count_documents({})
        before_events = self.db.audit_events.count_documents({})
        before_head = self.db.checkpoints.find_one({'_id': 'audit_head'})

        def change_scope_then_mutate(*args, **kwargs):
            # Deterministic concurrent-write interleaving: after the initial user
            # read, before the real replica-set transaction begins.
            self.db.users.update_one({'username': 'institution_1.demo'},
                                     {'$set': {'institution_id': identifier(2)}})
            return mutate(*args, **kwargs)

        with patch('backend.app.modules.auth.service.mutate', side_effect=change_scope_then_mutate):
            response = self.http.post('/api/v1/auth/login', headers=HEADERS,
                                      json={'username': 'institution_1.demo', 'password': DEMO_PASSWORD})
        self.assertEqual(response.status_code, 409)
        self.assertNotIn('set-cookie', response.headers)
        self.assertEqual(self.db.sessions.count_documents({}), before_sessions)
        self.assertEqual(self.db.audit_events.count_documents({}), before_events)
        self.assertEqual(self.db.checkpoints.find_one({'_id': 'audit_head'}), before_head)
        self.login()
        event = self.db.audit_events.find_one({'action': 'auth.login'}, sort=[('sequence', -1)])
        self.assertEqual(event['institution_id'], identifier(2))
        self.assertTrue(verify(self.db))

    def test_logout_role_change_is_retryable_without_false_revocation(self):
        self.login()
        token = self.http.cookies.get(COOKIE)
        before_events = self.db.audit_events.count_documents({})

        def change_role_then_mutate(*args, **kwargs):
            self.db.users.update_one({'username': 'institution_1.demo'},
                                     {'$set': {'role': 'regional_officer', 'institution_id': None,
                                               'region': 'DEMO-REGION-B'}})
            return mutate(*args, **kwargs)

        with patch('backend.app.modules.auth.service.mutate', side_effect=change_role_then_mutate):
            response = self.http.post('/api/v1/auth/logout', headers=HEADERS, json={})
        self.assertEqual(response.status_code, 409)
        self.assertNotIn('set-cookie', response.headers)
        self.assertIsNone(self.db.sessions.find_one({'_id': token_hash(token)})['revoked_at'])
        self.assertEqual(self.db.audit_events.count_documents({}), before_events)
        self.assertEqual(self.http.post('/api/v1/auth/logout', headers=HEADERS, json={}).status_code, 200)
        event = self.db.audit_events.find_one({'action': 'auth.logout'}, sort=[('sequence', -1)])
        self.assertEqual(event['role'], 'regional_officer')
        self.assertEqual(event['scope']['region'], 'DEMO-REGION-B')
        self.assertIsNone(event['institution_id'])
        self.assertEqual(self.http.get('/api/v1/auth/me').status_code, 401)
        self.assertTrue(verify(self.db))

    def test_atomic_outbox_and_idempotency(self):
        job = NotificationJob(idempotency_key='same-alert',application_id=identifier(1001),
                              obligation_id=identifier(2001),rule_id='DEMO-CLOCKWORK',rule_version=1,
                              channel='in_app',recipient_user_id=identifier(101),why='Demo threshold reached',
                              threshold_days=1,business_at=DemoClock(self.db).now(),template_version=1)
        def write(session):
            self.db.stage_events.insert_one({'idempotency_key':'domain-event'},session=session)
        with patch('backend.app.modules.audit.repository.append',side_effect=RuntimeError('injected')):
            with self.assertRaises(RuntimeError):
                self.audited(write,jobs=[job])
        self.assertEqual(self.db.notification_jobs.count_documents({}),0)
        self.assertEqual(self.db.stage_events.count_documents({}),0)
        self.audited(write,jobs=[job])
        self.audited(jobs=[job])
        self.assertEqual(self.db.notification_jobs.count_documents({}),1)
        self.assertTrue(verify(self.db))

    def test_audit_verifier_detects_edits_and_missing_entries(self):
        self.audited()
        self.audited()
        self.assertTrue(verify(self.db))
        entry = self.db.audit_events.find_one({'sequence':2})
        self.db.audit_events.update_one({'_id':entry['_id']},{'$set':{'reason':'changed'}})
        self.assertFalse(verify(self.db))
        self.db.audit_events.replace_one({'_id':entry['_id']},entry)
        self.assertTrue(verify(self.db))
        self.db.audit_events.delete_one({'_id':entry['_id']})
        self.assertFalse(verify(self.db))

    def test_rule_versions_and_non_overwriting_seed(self):
        rule = load_seed()
        self.assertEqual(len(rule.routes),4)
        bad = rule.model_dump()
        bad['routes']['UNKNOWN'] = ['UNSUPPORTED']
        with self.assertRaises(ValidationError):
            RuleSet.model_validate(bad)
        changed = rule.model_copy(update={'label':'Changed same version'})
        with self.assertRaises(ValueError):
            self.audited(lambda s: publish_seed(self.db,changed,s))
        user = self.db.users.find_one({'username':'institution_1.demo'})
        self.db.institutions.update_one({'_id':identifier(1)},{'$set':{'name':'User edit'}})
        seed(self.db)
        self.assertEqual(self.db.institutions.find_one({'_id':identifier(1)})['name'],'User edit')
        self.assertEqual(self.db.users.find_one({'_id':user['_id']})['password_hash'],user['password_hash'])
        self.assertEqual(self.db.obligations.count_documents({}),4)

    def test_calendar_due_boundary_and_security_clock_separation(self):
        row = self.db.obligations.find_one({'_id':identifier(2001)})
        due = baseline_due(datetime(2026,10,1,tzinfo=timezone.utc),30,'Asia/Kolkata')
        row['baseline_due_at'] = row['active_due_at'] = due
        self.assertEqual(view(row,due,'Asia/Kolkata').deadline_severity,'due_today')
        self.assertEqual(view(row,due+timedelta(milliseconds=1),'Asia/Kolkata').deadline_severity,'overdue')
        row['state'] = 'awaiting_verification'
        row['evidence_state'] = 'submitted'
        self.assertEqual(view(row,due+timedelta(days=1),'Asia/Kolkata').deadline_severity,'overdue')
        self.login()
        self.db.checkpoints.update_one({'_id':'demo_clock'},{'$set':{'business_at':datetime(2099,1,1,tzinfo=timezone.utc)}})
        self.assertEqual(self.http.get('/api/v1/auth/me').status_code,200)
        self.assertLess(abs((RealClock().now()-datetime.now(timezone.utc)).total_seconds()),1)
        with self.assertRaises(ValueError):
            DemoClock(self.mongo['clockwork_live_forbidden'])

    def test_health_and_cors(self):
        self.assertEqual(self.http.get('/api/v1/health/live').status_code,200)
        self.assertEqual(self.http.get('/api/v1/health/ready').status_code,200)
        self.assertEqual(self.http.get('/api/v1/health/scheduler').json()['status'],'disabled')
        response = self.http.options('/api/v1/auth/login',headers={'Origin':'https://evil.example',
                                    'Access-Control-Request-Method':'POST'})
        self.assertNotIn('access-control-allow-origin',response.headers)
        self.assertIn('x-correlation-id',response.headers)


