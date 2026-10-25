"""Workflow HTTP tests using disposable ports and database copies."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3
import unittest
from urllib.request import build_opener
from uuid import uuid4

from backend.database import CONFIG_PATH, engine_for, initialize
from backend.tests import test_auth as harness


class WorkflowHTTPTests(unittest.TestCase):
    fixed_port = int(os.environ.get('CLOCKWORK_TEST_PORT', '0'))
    setUpClass = classmethod(harness.AuthHTTPTests.setUpClass.__func__)
    tearDownClass = classmethod(harness.AuthHTTPTests.tearDownClass.__func__)
    start = harness.AuthHTTPTests.start
    stop = harness.AuthHTTPTests.stop
    tearDown = harness.AuthHTTPTests.tearDown
    sql = harness.AuthHTTPTests.sql
    request = harness.AuthHTTPTests.request
    login = harness.AuthHTTPTests.login
    account = harness.AuthHTTPTests.account

    def setUp(self):
        harness.AuthHTTPTests.setUp(self)
        self.config = json.loads(CONFIG_PATH.read_text())

    def switch(self, username):
        code,data,_=self.request('/api/auth/login','POST',{'username':username,'password':harness.DEMO_PASSWORD})
        self.assertEqual(code,200,data)

    def file(self, route='SCRUTINY_EVC', key=None):
        return self.request('/api/applications','POST',{'route_code':route},
                            {'Idempotency-Key': key or str(uuid4())})

    def action(self, app, action, version, reason='Processing checked with recorded demonstration explanation', key=None):
        return self.request(f'/api/applications/{app}/actions/{action}','POST',
                            {'expected_version':version,'reason':reason},{'Idempotency-Key':key or str(uuid4())})

    def snapshot(self):
        tables=['applications','obligations','pause_intervals','audit_events','workflow_states','workflow_events','workflow_requests']
        return {t:self.sql(f'SELECT * FROM {t} ORDER BY 1') for t in tables}

    def install_config(self):
        self.stop()
        path=Path(self.tmp.name)/'config.json'
        path.write_text(json.dumps(self.config))
        self.extra_env={'CLOCKWORK_WORKFLOW_CONFIG':str(path)}
        self.start()

    def test_full_journey_pause_dates_audit_history_restart(self):
        self.switch('institution_1.demo')
        code, filed,_=self.file()
        self.assertEqual(code,200,filed)
        app=filed['application_id']
        info=self.request(f'/api/applications/{app}/workflow')[1]
        self.assertEqual((info['current_stage'],info['owner_user_id'],info['version']),('SCRUTINY','DEMO-USER-RO-1',1))
        original=info['current_obligation']['base_due_at']
        self.switch('regional_1.demo')
        code,returned,_=self.action(app,'return',1,'Please clarify the synthetic laboratory details')
        self.assertEqual((code,returned['status']),(200,'returned_for_deficiency'))
        self.sql("UPDATE demo_clock SET now_at='2026-10-28T00:00:00+00:00'")
        self.switch('institution_1.demo')
        self.assertEqual(self.action(app,'resubmit',2,'Laboratory details clarified in this demonstration')[0],200)
        info=self.request(f'/api/applications/{app}/workflow')[1]
        self.assertEqual(info['current_obligation']['base_due_at'],original)
        self.assertEqual(info['current_obligation']['paused_seconds'],259200)
        self.assertEqual(info['current_obligation']['paused_at'],None)
        self.assertEqual((datetime.fromisoformat(info['adjusted_due_at'])-datetime.fromisoformat(original)).total_seconds(),259200)
        self.switch('regional_1.demo')
        self.assertEqual(self.action(app,'complete',3)[1]['current_stage'],'EVC')
        self.switch('committee_1.demo')
        self.assertEqual(self.action(app,'complete',4)[1]['status'],'awaiting_authorised_decision')
        self.switch('institution_1.demo')
        history=self.request(f'/api/applications/{app}/history')[1]
        self.assertEqual(history['total'],5)
        self.assertEqual([e['action'] for e in history['items']],['file','return','resubmit','complete','complete'])
        self.assertEqual([e['actor_user_id'] for e in history['items']],
                         ['DEMO-USER-INST-1','DEMO-USER-RO-1','DEMO-USER-INST-1','DEMO-USER-RO-1','DEMO-USER-COMMITTEE-1'])
        for e in history['items']:
            self.assertEqual(e['generator_version'],'clockwork-workflow-1')
            self.assertLess(abs((datetime.now(timezone.utc)-datetime.fromisoformat(e['recorded_at'])).total_seconds()),30)
        self.assertEqual(history['items'][1]['previous_state'],'in_progress')
        self.assertEqual(history['items'][1]['resulting_state'],'returned_for_deficiency')
        self.assertEqual(history['items'][3]['previous_stage'],'SCRUTINY')
        self.assertEqual(history['items'][3]['resulting_stage'],'EVC')
        self.stop(); self.start()
        self.assertEqual(self.request(f'/api/applications/{app}/history')[1],history)
        self.assertEqual(self.request(f'/api/applications/{app}/workflow')[1]['status'],'awaiting_authorised_decision')
        self.assertEqual(self.sql('SELECT COUNT(*) FROM applications')[0][0],41)
        self.assertEqual(self.sql('SELECT COUNT(*) FROM obligations')[0][0],58)
        self.assertEqual(self.sql('SELECT COUNT(*) FROM audit_events')[0][0],49)
        print(f'WORKFLOW HTTP journey on {self.base}: 41 apps, 58 obligations, 49 audit events; restart passed')

    def test_all_routes_and_final_state_never_approval(self):
        actors={'SCRUTINY':'regional_1.demo','EVC':'committee_1.demo','SAC_SHC':'committee_2.demo'}
        for code,stages in self.config['routes'].items():
            self.switch('institution_1.demo')
            status,filed,_=self.file(code)
            self.assertEqual(status,200)
            app=filed['application_id']
            for index,stage in enumerate(stages,1):
                self.switch(actors[stage])
                self.assertEqual(self.request(f'/api/applications/{app}/workflow')[1]['current_stage'],stage)
                status,result,_=self.action(app,'complete',index)
                self.assertEqual(status,200,result)
            self.assertEqual(result['status'],'awaiting_authorised_decision')
            self.assertEqual(self.sql('SELECT COUNT(*) FROM obligations WHERE application_id=?',(app,))[0][0],len(stages))
            self.assertEqual(self.action(app,'complete',len(stages)+1)[0],409)
        self.assertEqual(self.sql('SELECT COUNT(*) FROM applications')[0][0],44)
        self.assertEqual(self.sql('SELECT COUNT(*) FROM obligations')[0][0],62)

    def test_write_authority_csrf_spoofing_and_cross_institution(self):
        self.assertEqual(self.file()[0],401)
        self.switch('institution_1.demo'); app=self.file()[1]['application_id']
        self.assertEqual(self.action(app,'complete',1)[0],403)
        self.assertEqual(self.action(app,'return',1)[0],403)
        for who in ['admin.demo','bureau.demo']:
            self.switch(who)
            self.assertEqual(self.file()[0],403)
            self.assertEqual(self.action(app,'complete',1)[0],403)
        for who in ['institution_2.demo','regional_2.demo','committee_1.demo']:
            self.switch(who)
            self.assertEqual(self.action(app,'return',1)[0],404)
            self.assertEqual(self.request(f'/api/applications/{app}/history')[0],404)
        self.switch('institution_1.demo')
        self.assertEqual(self.request('/api/applications','POST',{'route_code':'EVC_ONLY','institution_id':'DEMO-INST-002'}, {'Idempotency-Key':'spoofing-key'})[0],422)
        self.assertEqual(self.request('/api/applications','POST',{'route_code':'EVC_ONLY'}, {'Idempotency-Key':'csrf-key'},csrf=False)[0],403)
        self.switch('regional_1.demo')
        for extra in ['actor','role','current_stage','next_owner']:
            self.assertEqual(self.request(f'/api/applications/{app}/actions/complete','POST',{'expected_version':1,'reason':'A valid explanation',extra:'spoof'}, {'Idempotency-Key':str(uuid4())})[0],422)
        self.assertEqual(self.action(app,'approve',1)[0],422)
        self.assertEqual(self.action(app,'resubmit',1)[0],403)
        self.assertEqual(self.request(f'/api/applications/{app}/actions/return','POST',{'expected_version':1,'reason':'A valid explanation'}, {'Idempotency-Key':'csrf-action'},csrf=False)[0],403)

    def test_idempotency_stale_versions_and_repeated_returns(self):
        self.switch('institution_1.demo')
        key=str(uuid4()); first=self.file(key=key)[1]; app=first['application_id']
        self.assertTrue(self.file(key=key)[1]['replayed'])
        self.assertEqual(self.file('EVC_ONLY',key)[0],409)
        self.switch('regional_1.demo')
        key=str(uuid4())
        self.assertEqual(self.action(app,'return',1,key=key)[0],200)
        self.assertTrue(self.action(app,'return',1,key=key)[1]['replayed'])
        self.assertEqual(self.action(app,'return',1)[0],409)
        self.assertEqual(self.action(app,'return',2)[0],409)
        self.assertEqual(self.action(app,'complete',2)[0],409)
        self.switch('institution_1.demo'); key=str(uuid4())
        self.assertEqual(self.action(app,'resubmit',2,key=key)[0],200)
        self.assertTrue(self.action(app,'resubmit',2,key=key)[1]['replayed'])
        self.assertEqual(self.action(app,'resubmit',3)[0],409)
        self.switch('regional_1.demo'); key=str(uuid4())
        self.assertEqual(self.action(app,'complete',3,key=key)[0],200)
        self.assertTrue(self.action(app,'complete',3,key=key)[1]['replayed'])
        self.assertEqual(self.action(app,'complete',3)[0],409)
        self.assertEqual(self.action(app,'complete',4)[0],403)
        self.assertEqual(self.sql('SELECT COUNT(*) FROM obligations WHERE application_id=?',(app,))[0][0],2)
        self.assertEqual(self.sql('SELECT COUNT(*) FROM audit_events WHERE application_id=?',(app,))[0][0],4)
        self.stop(); self.start()
        self.assertTrue(self.action(app,'complete',3,key=key)[1]['replayed'])

    def test_missing_ambiguous_or_wrong_next_assignment_is_atomic(self):
        self.switch('institution_1.demo'); app=self.file()[1]['application_id']
        self.switch('regional_1.demo')
        original=json.loads(json.dumps(self.config))
        for variant in ['missing','ambiguous','wrong_role','wrong_committee','rule_missing','route_changed']:
            self.config=json.loads(json.dumps(original))
            assignments=self.config['workflow']['assignments']
            evc=next(a for a in assignments if a['region']=='DEMO-REGION-A' and a['stage']=='EVC')
            if variant=='missing': assignments.remove(evc)
            if variant=='ambiguous': assignments.append(dict(evc))
            if variant=='wrong_role': evc['owner_user_id']='DEMO-USER-ADMIN'
            if variant=='wrong_committee': evc['committee']='MISSING'
            if variant=='rule_missing': self.config['workflow']['stage_rules']['EVC']['rule_version']=99
            if variant=='route_changed': self.config['routes']['SCRUTINY_EVC']=['SCRUTINY']
            self.install_config(); before=self.snapshot()
            self.assertEqual(self.action(app,'complete',1)[0],409,variant)
            self.assertEqual(self.snapshot(),before,variant)

    def test_missing_first_assignment_and_bad_route_no_application(self):
        self.switch('institution_1.demo')
        before=self.snapshot()
        self.assertEqual(self.file('NOT_A_ROUTE')[0],409)
        self.assertEqual(self.snapshot(),before)
        self.config['workflow']['assignments']=[]; self.install_config()
        self.assertEqual(self.file()[0],409)
        self.assertEqual(self.snapshot(),before)

    def test_reason_required_and_accumulated_pause_does_not_change_documents(self):
        # Operate on an existing seeded EVC task with a previous completed pause.
        app='DEMO-APP-001'
        self.switch('committee_1.demo')
        original=self.sql('SELECT * FROM documents')
        unrelated=self.sql("SELECT * FROM obligations WHERE type != 'stage'")
        due=self.sql("SELECT base_due_at FROM obligations WHERE id='DEMO-OBL-001-STAGE'")
        for reason in ['', 'short','             ','!!!!!!!!!!!!']:
            self.assertEqual(self.action(app,'return',0,reason)[0],422)
        for version,date_return,date_resume in [(0,'2026-10-25','2026-10-27'),(2,'2026-10-28','2026-10-29')]:
            self.switch('committee_1.demo')
            self.sql('UPDATE demo_clock SET now_at=?',(date_return+'T00:00:00+00:00',))
            self.assertEqual(self.action(app,'return',version)[0],200)
            self.switch('institution_2.demo')
            self.assertEqual(self.action(app,'resubmit',version+1)[0],404)
            self.switch('institution_1.demo')
            self.assertEqual(self.action(app,'resubmit',version+1,'')[0],422)
            self.sql('UPDATE demo_clock SET now_at=?',(date_resume+'T00:00:00+00:00',))
            self.assertEqual(self.action(app,'resubmit',version+1)[0],200)
        self.assertEqual(self.sql("SELECT paused_seconds FROM obligations WHERE id='DEMO-OBL-001-STAGE'")[0][0],6*86400)
        self.assertEqual(self.sql("SELECT base_due_at FROM obligations WHERE id='DEMO-OBL-001-STAGE'"),due)
        self.assertEqual(self.sql('SELECT * FROM documents'),original)
        self.assertEqual(self.sql("SELECT * FROM obligations WHERE type != 'stage'"),unrelated)

    def test_concurrent_double_click_and_conflicting_actions(self):
        self.switch('institution_1.demo')
        cookie=next(iter(self.cookies)).value
        key=str(uuid4())
        def filing():
            return self.request('/api/applications','POST',{'route_code':'SCRUTINY_EVC'},
                                {'Idempotency-Key':key,'Cookie':'clockwork_session='+cookie},client=build_opener())
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:filing(), range(2)))
        self.assertEqual([r[0] for r in results],[200,200])
        self.assertEqual({r[1]['replayed'] for r in results},{False,True})
        app=results[0][1]['application_id']; self.switch('regional_1.demo')
        cookie=next(iter(self.cookies)).value
        def act(action):
            return self.request(f'/api/applications/{app}/actions/{action}','POST',
                                {'expected_version':1,'reason':'Concurrent processing test explanation'},
                                {'Idempotency-Key':str(uuid4()),'Cookie':'clockwork_session='+cookie},client=build_opener())
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(act,['return','complete']))
        self.assertEqual(sorted(r[0] for r in results),[200,409])
        self.assertEqual(self.sql('SELECT COUNT(*) FROM audit_events WHERE application_id=?',(app,))[0][0],2)

    def test_history_and_workflow_do_not_leak_other_committee_tasks(self):
        self.switch('institution_1.demo'); app=self.file()[1]['application_id']
        self.switch('regional_1.demo'); self.action(app,'complete',1)
        self.switch('committee_1.demo')
        self.assertEqual(self.request(f'/api/applications/{app}/history')[1]['total'],0)
        self.assertEqual(self.action(app,'return',2)[0],200)
        self.switch('institution_1.demo'); self.action(app,'resubmit',3)
        self.switch('committee_1.demo')
        history=self.request(f'/api/applications/{app}/history?limit=1&offset=1')[1]
        self.assertEqual((history['total'],len(history['items'])),(2,1))
        self.switch('committee_2.demo')
        self.assertEqual(self.request(f'/api/applications/{app}/workflow')[0],404)
        self.assertEqual(self.request(f'/api/applications/{app}/history')[0],404)

    def test_backward_clock_and_audit_failure_roll_back_everything(self):
        self.switch('institution_1.demo'); app=self.file()[1]['application_id']
        self.switch('regional_1.demo')
        self.sql("UPDATE demo_clock SET now_at='2020-01-01T00:00:00+00:00'")
        before=self.snapshot(); self.assertEqual(self.action(app,'return',1)[0],409)
        self.assertEqual(self.snapshot(),before)
        self.sql("UPDATE demo_clock SET now_at='2026-10-25T00:00:00+00:00'")
        self.sql("CREATE TRIGGER reject_workflow_audit BEFORE INSERT ON workflow_events BEGIN SELECT RAISE(ABORT, 'forced test failure'); END")
        before=self.snapshot(); self.assertEqual(self.action(app,'complete',1)[0],409)
        self.assertEqual(self.snapshot(),before)

    def test_version_two_migration_preserves_sessions_and_all_existing_rows(self):
        self.switch('institution_1.demo'); self.stop()
        for table in ['workflow_requests','workflow_events','workflow_states']:
            self.sql('DROP TABLE '+table)
        self.sql('UPDATE clockwork_application_schema SET version=2')
        tables=[r[0] for r in self.sql("SELECT name FROM sqlite_master WHERE type='table'") if r[0]!='clockwork_application_schema']
        before={t:self.sql(f'SELECT * FROM {t} ORDER BY 1') for t in tables}
        engine=engine_for(self.db)
        try: initialize(engine); initialize(engine)
        finally: engine.dispose()
        self.assertEqual(before,{t:self.sql(f'SELECT * FROM {t} ORDER BY 1') for t in tables})
        self.assertEqual(len(list(self.db.parent.glob('*.pre-workflow-*.sqlite3'))),1)
        self.start()
        self.assertEqual(self.request('/api/auth/me')[0],200)


if __name__ == '__main__':
    unittest.main()
