import test from 'node:test';
import assert from 'node:assert/strict';
import { seedDemo, setPersona, remaining, activeDays, effectiveDue, changeCase, evcAction, evidenceAction, scan, previewRule, publishRule, visible, can, validity } from '../src/demo/service.js';
import { report, csv } from '../src/demo/reports.js';
const id = 'CW-2026-002';
const app = d => d.applications.find(a => a.id === id);
const as = (d, role, rest = {}) => setPersona(d, { role, ...rest });
const reason = 'Fictional validation observation';
test('seed relationships, five personas and scope-checked actions', () => {
 const d = seedDemo(); assert.equal(d.applications.length,60); assert.equal(new Set(d.applications.map(a=>a.region)).size,4);
 assert.equal(new Set(d.evc.map(e=>e.applicationId)).size,d.evc.length);
 assert.equal(d.registers.every(r=>d.applications.some(a=>a.id===r.applicationId)),true);
 assert.equal(d.applications.filter(a=>visible(as(d,'regional',{region:'North'}),a)).length,15);
 assert.equal(d.applications.filter(a=>visible(as(d,'institution',{institutionId:'INST-2'}),a)).length,1);
 assert.equal(can(as(d,'admin'),app(d),'complete'),false);
 assert.throws(()=>changeCase(as(d,'regional',{region:'North'}),id,'complete',reason),/persona/);
 assert.throws(()=>changeCase(as(d,'institution',{institutionId:'INST-1'}),id,'resubmit',reason),/persona/);
 assert.throws(()=>changeCase(as(d,'committee',{committee:'North EVC Committee'}),id,'return',reason),/persona/);
});
test('repeated pause/resume preserves remaining allowance and elapsed, nonpausable runs', () => {
 let d=seedDemo(); const startRemaining=remaining(d,app(d)), startElapsed=activeDays(d,app(d));
 assert.throws(()=>changeCase(d,id,'return','  '),/reason/);
 for(let i=0;i<2;i++) {
  d=changeCase(as(d,'regional'),id,'return',reason,app(d).version);
  d=scan(as(d,'bureau'),7); assert.equal(remaining(d,app(d)),startRemaining); assert.equal(activeDays(d,app(d)),startElapsed);
  d=changeCase(as(d,'institution'),id,'resubmit',reason,app(d).version);
 }
 assert.equal(app(d).pausedDays,14); assert.equal(app(d).pauseIntervals.length,2); assert.equal(app(d).attempts,2); assert.equal(remaining(d,app(d)),5);
 let n=seedDemo(); const evc=n.applications.find(a=>a.stage==='EVC visit'&&a.status==='In progress');
 n=as(n,'committee',{committee:evc.owner}); const before=remaining(n,evc); n=changeCase(n,evc.id,'return',reason); n=scan(as(n,'bureau'),7);
 assert.equal(n.applications.find(a=>a.id===evc.id).pausedAt,null); assert.equal(remaining(n,n.applications.find(a=>a.id===evc.id)),before-7);
});
test('all four routes terminate at human decision; EVC once, stale actions fail', () => {
 for(const route of Object.keys(seedDemo().rules[0].routes)) {
  let d=seedDemo(); const a=app(d); a.route=route; a.stage=d.rules[0].routes[route][0]; a.owner=a.stage==='Scrutiny'?'South Review Desk':'South EVC Committee';
  if(a.stage==='EVC scheduling') d.evc.push({id:`EVC-${id}`,applicationId:id,committee:'',visitDate:'',scheduling:'Queued',completion:'Pending',report:'Pending'});
  for(let i=0;i<10&&app(d).stage!=='Human decision';i++) {
   const stage=app(d).stage;
   if(stage==='EVC scheduling') d=evcAction(as(d,'regional'),id,'schedule',{committee:'South EVC Committee',visitDate:d.clock,reason});
   else if(stage==='EVC visit') d=evcAction(as(d,'committee',{committee:'South EVC Committee'}),id,'visit',{reason});
   else if(stage==='EVC report') {d=evcAction(as(d,'committee',{committee:'South EVC Committee'}),id,'report',{reason}); d=evcAction(as(d,'bureau'),id,'verify-report',{reason});}
   else d=changeCase(as(d,stage==='SAC/SHC'?'committee':'regional',{committee:'South SAC Committee'}),id,'complete',reason,app(d).version);
  }
  assert.equal(app(d).stage,'Human decision'); assert.equal(app(d).status,'In progress'); assert.ok(d.evc.filter(e=>e.applicationId===id).length<=1);
 }
 let d=seedDemo(),v=app(d).version; d=changeCase(d,id,'complete',reason,v); assert.throws(()=>evcAction(as(d,'regional'),id,'schedule',{reason,committee:'South EVC Committee',visitDate:d.clock,version:v}),/changed/);
 assert.equal(d.evc.filter(e=>e.applicationId===id).length,1);
});
test('multi-threshold scans are idempotent, report submission stays open, clock cannot reverse', () => {
 let d=scan(seedDemo(),30); const messages=d.notifications.length, milestones=d.milestones.length;
 assert.ok(messages>0); assert.ok(milestones>0); assert.equal(new Set(d.notifications.map(n=>n.id)).size,messages);
 d=scan(d); assert.equal(d.notifications.length,messages); assert.equal(d.milestones.length,milestones);
 assert.ok(d.notifications.every(n=>n.why.includes('DEMO-CW') && n.status.includes('not sent')));
 assert.throws(()=>scan(d,-1),/Advance/);
});
test('pending/rejected lease never changes verified validity; submission and verification scoped', () => {
 let d=seedDemo(),r=d.registers.find(r=>r.id==='REG-DEMO-L'); const old=r.expiryDate;
 const fields={filename:'fictional.pdf',size:12,reason,issueDate:d.clock,expiryDate:'2027-10-25'};
 assert.throws(()=>evidenceAction(d,r.id,'submit',fields),/persona/);
 d=evidenceAction(as(d,'institution'),r.id,'submit',fields); r=d.registers.find(x=>x.id===r.id); assert.equal(r.expiryDate,old); assert.equal(validity(d,r),'Expired');
 assert.throws(()=>evidenceAction(as(d,'regional',{region:'North'}),r.id,'verify',{reason}),/persona/);
 assert.throws(()=>evidenceAction(as(d,'bureau'),r.id,'reject',{reason:' '}),/reason/);
 d=evidenceAction(as(d,'bureau'),r.id,'reject',{reason}); assert.equal(d.registers.find(x=>x.id===r.id).expiryDate,old);
 d=evidenceAction(as(d,'institution'),r.id,'submit',fields); d=evidenceAction(as(d,'bureau'),r.id,'verify',{reason}); r=d.registers.find(x=>x.id===r.id);
 assert.equal(r.expiryDate,'2027-10-25'); assert.equal(r.renewalHistory[0].expiryDate,old); assert.equal(r.submissions.length,2); assert.equal(validity(d,r),'Valid');
});
test('rules validate, preview is pure, versions pinned until explicit migration; scoped reports and CSV', () => {
 let d=as(seedDemo(),'admin'),rule=JSON.parse(JSON.stringify(d.rules[0])); rule.timelines.Scrutiny=21;
 const due=effectiveDue(d,app(d)); const preview=previewRule(d,rule,true); assert.equal(preview.changes.length,60); assert.equal(effectiveDue(d,app(d)),due);
 d=publishRule(d,rule,false,reason); assert.equal(app(d).ruleVersion,1); assert.equal(d.rules.at(-1).version,2);
 d=publishRule(d,rule,true,reason); assert.equal(app(d).ruleVersion,3); assert.notEqual(effectiveDue(d,app(d)),due);
 rule.timelines.Scrutiny=0; assert.throws(()=>previewRule(d,rule,true),/timeline/);
 d=as(d,'institution',{institutionId:'INST-2'}); assert.equal(report(d,'pendency').rows.length,1); assert.equal(report(d,'documents').rows.length,1); assert.equal(report(d,'pendency',{region:'North'}).rows.length,0);
 for(const type of ['pendency','evc','undertakings','documents','overdue','performance']) assert.ok(Array.isArray(report(d,type).rows));
 assert.ok(csv({headers:['x'],rows:[[' =SUM(A1)']]}).includes("' =SUM"));
});
test('due-day boundary, explicit committee assignment and report verification boundary',()=>{
 let d=seedDemo(); const a=app(d); a.due=d.clock; assert.equal(remaining(d,a),0); d=scan(d,1); assert.equal(remaining(d,app(d)),-1);
 d=changeCase(d,id,'complete',reason,app(d).version);
 assert.equal(visible(as(d,'committee'),app(d)),false);
 assert.throws(()=>evcAction(as(d,'regional'),id,'schedule',{committee:'North EVC Committee',visitDate:d.clock,reason}),/explicit/);
 d=evcAction(as(d,'regional'),id,'schedule',{committee:'South EVC Committee',visitDate:d.clock,reason});
 d=evcAction(as(d,'committee'),id,'visit',{reason}); d=evcAction(as(d,'committee'),id,'report',{reason});
 assert.equal(app(d).stage,'EVC report'); assert.equal(d.evc.find(e=>e.applicationId===id).report,'Submitted');
 assert.throws(()=>evcAction(as(d,'committee'),id,'verify-report',{reason}),/persona/);
 d=evcAction(as(d,'bureau'),id,'verify-report',{reason}); assert.equal(app(d).stage,'Human decision');
});
test('mobile seed covers every persona scope, route and register state with internally derived counts',()=>{
 const d=seedDemo();
 for(const region of ['North','South','East','West']){
  const cohort=d.applications.filter(a=>a.region===region);assert.equal(cohort.length,15);assert.equal(new Set(cohort.map(a=>a.route)).size,4);
  for(const kind of ['EVC','SAC'])assert.ok(d.applications.some(a=>visible(as(d,'committee',{committee:`${region} ${kind} Committee`}),a)));
 }
 for(const a of d.applications){const p=as(d,'institution',{institutionId:a.institutionId});assert.equal(p.applications.filter(x=>visible(p,x)).length,1);assert.equal(d.registers.filter(r=>r.applicationId===a.id).length,2);assert.match(a.contactEmail,/@example\.org$/);}
 assert.equal(new Set(d.applications.map(a=>a.institution)).size,60);
 for(const state of ['In progress','Awaiting clarification','Resubmitted','Completed'])assert.ok(d.applications.some(a=>a.status===state));
 for(const state of ['Valid','Expiring','Expired'])assert.ok(d.registers.some(r=>r.kind==='Lease validity'&&validity(d,r)===state));
 assert.ok(d.registers.some(r=>r.kind==='Lease validity'&&r.pending&&validity(d,r)==='Expired'));
 const completed=d.applications.find(a=>a.status==='Completed');assert.equal(can(as(d,'bureau'),completed,'return'),false);assert.ok(!d.notifications.some(n=>n.targetId===completed.id));
 assert.ok(d.notifications.length>0);assert.equal(scan(d).notifications.length,d.notifications.length);
});
