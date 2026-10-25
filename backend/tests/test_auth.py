"""Real HTTP auth/scope tests. All writes use isolated temporary SQLite files."""
from contextlib import closing
from datetime import datetime, timedelta, timezone
import hashlib
from http.cookiejar import CookieJar
import json
import os
from pathlib import Path
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import build_opener, HTTPCookieProcessor, Request, urlopen

from backend.database import PROJECT_ROOT, engine_for, initialize
from backend.passwords import DEMO_PASSWORD
from backend.seed import BUNDLE_PATH, seed


class AuthHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(BUNDLE_PATH.read_text(encoding='utf-8'))
        cls.root = tempfile.TemporaryDirectory()
        cls.template = Path(cls.root.name) / 'template.sqlite3'
        engine = engine_for(cls.template)
        seed(engine, cls.fixture)
        engine.dispose()

    @classmethod
    def tearDownClass(cls):
        cls.root.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / 'test.sqlite3'
        shutil.copyfile(self.template, self.db)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', getattr(self, 'fixed_port', 0)))
            self.port = sock.getsockname()[1]
        self.base = f'http://127.0.0.1:{self.port}'
        self.cookies = CookieJar()
        self.client = build_opener(HTTPCookieProcessor(self.cookies))
        self.log = tempfile.TemporaryFile(mode='w+')
        self.server = None
        self.start()

    def start(self, secure=False):
        env = dict(os.environ, CLOCKWORK_DATABASE_URL='', CLOCKWORK_DB_PATH=str(self.db), CLOCKWORK_ALLOWED_ORIGINS=self.base,
                   CLOCKWORK_COOKIE_SECURE='true' if secure else 'false')
        env.update(getattr(self, 'extra_env', {}))
        self.server = subprocess.Popen([sys.executable,'-m','backend.tests.http_server','--port',str(self.port)],
                                      cwd=PROJECT_ROOT, env=env, stdin=subprocess.PIPE, text=True,
                                      stdout=self.log, stderr=self.log)
        deadline = time.monotonic()+15
        while True:
            try:
                with urlopen(self.base+'/api/health', timeout=1) as r:
                    if r.status == 200:
                        return
            except URLError:
                if self.server.poll() is not None or time.monotonic() > deadline:
                    self.log.seek(0)
                    self.fail(self.log.read())
                time.sleep(.05)

    def stop(self):
        if self.server and self.server.poll() is None:
            if self.server.stdin and not self.server.stdin.closed:
                self.server.stdin.write('stop\n')
                self.server.stdin.flush()
                self.server.stdin.close()
            self.server.wait(timeout=20)
            self.assertEqual(self.server.returncode, 0)

    def tearDown(self):
        self.stop()
        self.log.close()
        self.tmp.cleanup()

    def sql(self, sql, params=()):
        with closing(sqlite3.connect(self.db)) as con, con:
            return con.execute(sql, params).fetchall()

    def request(self, path, method='GET', body=None, headers=None, csrf=True, client=None):
        h = {}
        if method == 'POST' and csrf:
            h = {'Origin':self.base,'X-ClockWork-CSRF':'1','Content-Type':'application/json'}
        h.update(headers or {})
        data = json.dumps(body).encode() if body is not None else (b'{}' if method == 'POST' else None)
        req = Request(self.base+path, data=data, headers=h, method=method)
        try:
            result = (client or self.client).open(req, timeout=5)
        except HTTPError as e:
            result = e
        with result:
            payload = result.read()
            if result.status >= 500:
                self.log.seek(0)
                self.fail(f'HTTP {result.status}: {payload!r}\n{self.log.read()}')
            return result.status, json.loads(payload) if payload else None, result.headers

    def account(self, role):
        return next(u for u in self.fixture['users'] if u['role'] == role)

    def login(self, role='administrator'):
        user = self.account(role)
        status, data, headers = self.request('/api/auth/login','POST',{'username':user['username'],'password':DEMO_PASSWORD})
        self.assertEqual(status, 200, data)
        self.assertEqual(data['id'], user['id'])
        return user, headers

    def test_correct_incorrect_unknown_login_cookie_hash_and_rotation(self):
        for username in ['admin.demo','unknown.demo']:
            code, body, _ = self.request('/api/auth/login','POST',{'username':username,'password':'wrong'})
            self.assertEqual((code,body), (401,{'detail':'Invalid username or password'}))
        self.assertEqual(self.sql('SELECT COUNT(*) FROM auth_sessions')[0][0], 0)
        user, headers = self.login()
        cookie = headers['Set-Cookie']
        for flag in ['HttpOnly','SameSite=strict','Path=/api','Max-Age=28800','expires=']:
            self.assertIn(flag.lower(),cookie.lower())
        token = next(iter(self.cookies)).value
        digest, created, expires, revoked = self.sql('SELECT token_hash,created_at,expires_at,revoked_at FROM auth_sessions')[0]
        self.assertEqual(digest, hashlib.sha256(token.encode()).hexdigest())
        self.assertNotIn(token.encode(), self.db.read_bytes())
        self.assertIsNone(revoked)
        self.assertAlmostEqual((datetime.fromisoformat(expires)-datetime.fromisoformat(created)).total_seconds(),28800)
        self.assertLess(abs((datetime.now(timezone.utc)-datetime.fromisoformat(created)).total_seconds()), 10)
        self.login()
        self.assertNotEqual(token,next(iter(self.cookies)).value)
        self.assertIsNotNone(self.sql('SELECT revoked_at FROM auth_sessions WHERE token_hash=?',(digest,))[0][0])
        code, body, hdr = self.request('/api/auth/me')
        self.assertEqual(code,200)
        self.assertEqual(body['role'],'administrator')
        self.assertEqual(hdr['Cache-Control'],'no-store')
        self.assertNotIn('password',json.dumps(body))

    def test_anonymous_denied_all_business_and_nested_endpoints(self):
        for path in ['/api/auth/me','/api/institutions','/api/institutions/DEMO-INST-001',
                     '/api/institutions/DEMO-INST-001/applications','/api/applications',
                     '/api/applications/DEMO-APP-001','/api/obligations',
                     '/api/applications/DEMO-APP-001/obligations']:
            self.assertEqual(self.request(path)[0],401,path)
        self.assertEqual(self.request('/api/auth/logout','POST')[0],401)

    def check_scope(self, role):
        user,_ = self.login(role)
        if role == 'institution':
            inst_ids={user['institution_id']}
        else:
            inst_ids={i['id'] for i in self.fixture['institutions'] if i['region']==user['region']}
        app_ids={a['id'] for a in self.fixture['applications'] if a['institution_id'] in inst_ids}
        expected_obs={o['id'] for o in self.fixture['obligations'] if o['application_id'] in app_ids}
        for path, expected in [('/api/institutions',inst_ids),('/api/applications',app_ids),('/api/obligations',expected_obs)]:
            code,result,_=self.request(path)
            self.assertEqual(code,200)
            self.assertEqual(result['total'],len(expected))
            self.assertEqual({r['id'] for r in result['items']},expected)
        for inst in self.fixture['institutions']:
            code,_,_=self.request('/api/institutions/'+inst['id'])
            self.assertEqual(code,200 if inst['id'] in inst_ids else 404)
        for app in self.fixture['applications']:
            code,_,_=self.request('/api/applications/'+app['id'])
            self.assertEqual(code,200 if app['id'] in app_ids else 404)
        foreign=next(a for a in self.fixture['applications'] if a['id'] not in app_ids)
        self.assertEqual(self.request('/api/applications/'+foreign['id']+'/obligations')[0],404)
        self.assertEqual(self.request('/api/obligations?application_id='+foreign['id'])[1]['total'],0)
        self.assertEqual(self.request('/api/applications?institution_id='+foreign['institution_id'])[1]['total'],0)
        code,result,_=self.request('/api/applications?limit=2&offset=1')
        self.assertEqual(code,200)
        self.assertEqual(result['total'],len(app_ids))
        self.assertEqual([r['id'] for r in result['items']],sorted(app_ids)[1:3])
        self.assertEqual(self.request('/api/applications?offset=500')[1]['total'],len(app_ids))
        self.assertEqual(self.request('/api/applications?offset=500')[1]['items'],[])

    def test_institution_scope(self):
        self.check_scope('institution')

    def test_regional_scope(self):
        self.check_scope('regional_officer')
        other=next(i['region'] for i in self.fixture['institutions'] if i['region']!=self.account('regional_officer')['region'])
        self.assertEqual(self.request('/api/institutions?region='+other)[1]['total'],0)
        self.assertEqual(self.request('/api/applications?region='+other)[1]['total'],0)

    def test_committee_assignment_never_broadens_to_institution_or_other_tasks(self):
        user,_=self.login('committee')
        owned={o['id'] for o in self.fixture['obligations'] if o['owner_user_id']==user['id']}
        apps={o['application_id'] for o in self.fixture['obligations'] if o['id'] in owned}
        institution_ids={a['institution_id'] for a in self.fixture['applications'] if a['id'] in apps}
        self.assertEqual({a['id'] for a in self.request('/api/applications')[1]['items']}, apps)
        self.assertEqual({o['id'] for o in self.request('/api/obligations')[1]['items']}, owned)
        for inst in institution_ids:
            expected={a['id'] for a in self.fixture['applications'] if a['institution_id']==inst and a['id'] in apps}
            result=self.request('/api/institutions/'+inst+'/applications')[1]
            self.assertEqual(result['total'],len(expected))
            self.assertEqual({a['id'] for a in result['items']},expected)
        sibling=next(a for a in self.fixture['applications'] if a['institution_id'] in institution_ids and a['id'] not in apps)
        self.assertEqual(self.request('/api/applications/'+sibling['id'])[0],404)
        self.assertEqual(self.request('/api/applications/'+sibling['id']+'/obligations')[0],404)
        for app in apps:
            result=self.request('/api/applications/'+app+'/obligations')[1]
            expected={o['id'] for o in self.fixture['obligations'] if o['application_id']==app and o['id'] in owned}
            self.assertEqual(result['total'],len(expected))
            self.assertEqual({o['id'] for o in result['items']},expected)
        # Existing session must immediately reflect changed database assignments.
        self.sql("UPDATE obligations SET owner_user_id='DEMO-USER-ADMIN' WHERE owner_user_id=?",(user['id'],))
        self.assertEqual(self.request('/api/applications')[1]['total'],0)
        self.assertEqual(self.request('/api/institutions')[1]['total'],0)

    def test_bureau_and_administrator_cross_region_reads(self):
        for role in ['bureau_officer','administrator']:
            self.login(role)
            for path,total in [('/api/institutions',8),('/api/applications',40),('/api/obligations',56)]:
                code,result,_=self.request(path+'?limit=100')
                self.assertEqual((code,result['total'],len(result['items'])),(200,total,total))
                serialized=json.dumps(result)
                for excluded in ['password_hash','token_hash','evidence_file','storage_path','scrypt$']:
                    self.assertNotIn(excluded,serialized)
            for i in self.fixture['institutions']:
                self.assertEqual(self.request('/api/institutions/'+i['id'])[0],200)

    def test_missing_scopes_fail_closed_and_database_role_changes_apply(self):
        for role,field in [('regional_officer','region'),('committee','committee')]:
            user,_=self.login(role)
            self.sql(f'UPDATE users SET {field}=? WHERE id=?',('',user['id']))
            for path in ['/api/institutions','/api/applications','/api/obligations']:
                self.assertEqual(self.request(path)[1]['total'],0)
        user,_=self.login('institution')
        # Simulate legacy damaged data without weakening application DB constraints.
        with closing(sqlite3.connect(self.db)) as con, con:
            con.execute('PRAGMA ignore_check_constraints=ON')
            con.execute('UPDATE users SET institution_id=NULL WHERE id=?',(user['id'],))
        self.assertEqual(self.request('/api/applications')[1]['total'],0)
        admin,_=self.login()
        self.sql("UPDATE users SET role='regional_officer',region='DEMO-REGION-A' WHERE id=?",(admin['id'],))
        self.assertEqual(self.request('/api/institutions')[1]['total'],2)

    def test_spoofing_and_invalid_filters_do_not_leak_or_override(self):
        code,body,_=self.request('/api/auth/login','POST',{'username':'admin.demo','password':DEMO_PASSWORD,'role':'administrator'})
        self.assertEqual(code,422)
        self.assertNotIn(DEMO_PASSWORD,json.dumps(body))
        self.login('institution')
        for suffix in ['?role=administrator','?scope=all','?limit=101','?offset=-1']:
            self.assertEqual(self.request('/api/applications'+suffix)[0],422)
        self.assertEqual(self.request('/api/applications',headers={'X-Role':'administrator'})[0],400)
        user=self.account('institution')
        self.assertEqual(self.request('/api/auth/me')[1]['role'],'institution')
        self.assertEqual(self.request('/api/institutions/'+user['institution_id']+'/applications?institution_id=DEMO-INST-008')[0],422)
        self.assertEqual(self.request('/api/applications?institution_id=%27%20OR%201=1--')[1]['total'],0)

    def test_csrf_origin_rejects_login_and_logout_without_revoking(self):
        credentials={'username':'admin.demo','password':DEMO_PASSWORD}
        cases=[{}, {'Origin':self.base,'Content-Type':'application/json'},
               {'Origin':'http://evil.example','X-ClockWork-CSRF':'1','Content-Type':'application/json'},
               {'Origin':'null','X-ClockWork-CSRF':'1','Content-Type':'application/json'},
               {'Origin':self.base+'.evil','X-ClockWork-CSRF':'1','Content-Type':'application/json'},
               {'Origin':self.base,'X-ClockWork-CSRF':'1','Content-Type':'text/plain'},
               {'Origin':self.base,'X-ClockWork-CSRF':'1','Content-Type':'application/json','Sec-Fetch-Site':'cross-site'}]
        for headers in cases:
            self.assertEqual(self.request('/api/auth/login','POST',credentials,headers,csrf=False)[0],403)
        self.login()
        for headers in cases:
            self.assertEqual(self.request('/api/auth/logout','POST',{},headers,csrf=False)[0],403)
        self.assertEqual(self.request('/api/auth/me')[0],200)
        code,_,headers=self.request('/api/auth/login','OPTIONS',headers={'Origin':'http://evil.example','Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'x-clockwork-csrf'})
        self.assertEqual(code,405)
        self.assertNotIn('Access-Control-Allow-Origin',headers)

    def test_logout_revokes_replayed_cookie_and_clears_browser_cookie(self):
        self.login()
        token=next(iter(self.cookies)).value
        code,body,headers=self.request('/api/auth/logout','POST')
        self.assertEqual((code,body),(200,{'status':'logged_out'}))
        self.assertIn('Max-Age=0',headers['Set-Cookie'])
        self.assertEqual(self.request('/api/auth/me')[0],401)
        self.assertEqual(self.request('/api/auth/me',headers={'Cookie':'clockwork_session='+token},client=build_opener())[0],401)
        self.assertIsNotNone(self.sql('SELECT revoked_at FROM auth_sessions')[0][0])

    def test_session_survives_process_restart_demo_clock_not_auth_clock_and_expiry(self):
        self.login()
        original=self.sql('SELECT token_hash,created_at,expires_at FROM auth_sessions')
        for date in ['1990-01-01T00:00:00+00:00','2099-01-01T00:00:00+00:00']:
            self.sql('UPDATE demo_clock SET now_at=? WHERE id=1',(date,))
            self.assertEqual(self.request('/api/auth/me')[0],200)
        self.stop()
        self.start()
        self.assertEqual(self.request('/api/auth/me')[0],200)
        self.assertEqual(original,self.sql('SELECT token_hash,created_at,expires_at FROM auth_sessions'))
        expired=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()
        self.sql('UPDATE auth_sessions SET expires_at=?',(expired,))
        self.assertEqual(self.request('/api/auth/me')[0],401)
        self.sql("UPDATE demo_clock SET now_at='1990-01-01T00:00:00+00:00'")
        self.assertEqual(self.request('/api/applications')[0],401)
        print(f'HTTP cookies/read/restart/expiry smoke passed on {self.base} (temporary DB)')

    def test_secure_cookie_configuration(self):
        self.stop()
        self.start(secure=True)
        _,headers=self.login()
        self.assertIn('Secure',headers['Set-Cookie'])

    def test_version_one_migration_preserves_rows_clock_and_passwords(self):
        self.stop()
        for table in ['workflow_requests','workflow_events','workflow_states']:
            self.sql('DROP TABLE '+table)
        self.sql('DROP TABLE auth_sessions')
        self.sql('UPDATE clockwork_application_schema SET version=1')
        self.sql("UPDATE institutions SET name='Manually edited' WHERE id='DEMO-INST-001'")
        tables=[r[0] for r in self.sql("SELECT name FROM sqlite_master WHERE type='table'") if r[0]!='clockwork_application_schema']
        before={t:self.sql(f'SELECT * FROM {t} ORDER BY 1') for t in tables}
        engine=engine_for(self.db)
        try:
            initialize(engine)
            initialize(engine)
        finally:
            engine.dispose()
        self.assertEqual(before,{t:self.sql(f'SELECT * FROM {t} ORDER BY 1') for t in tables})
        self.assertEqual(self.sql('SELECT version FROM clockwork_application_schema'),[(3,)])
        self.assertEqual(len(list(self.db.parent.glob('*.pre-auth-*.sqlite3'))),1)
        self.assertEqual(self.sql('PRAGMA foreign_key_check'),[])


if __name__ == '__main__':
    unittest.main()
