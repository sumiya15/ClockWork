import test from 'node:test';
import assert from 'node:assert/strict';
import {seedDemo} from '../src/demo/service.js';
import {askCase} from '../src/demo/assistant.js';

test('assistant summaries and references are case-specific and deterministic',async()=>{
 const d=seedDemo(),snapshot=JSON.stringify(d);
 for(const a of d.applications.slice(0,6)){
  const result=await askCase(d,a.id,'Summarize this case');
  assert.ok(result.body.includes(a.institution));assert.ok(result.body.includes(a.stage));assert.equal(result.caseId,a.id);
  assert.ok(result.sources.some(s=>s.id===a.id));
  assert.ok(result.sources.every(s=>s.id===a.id||s.id===`rule-v${a.ruleVersion}`||d.evc.some(e=>e.id===s.id&&e.applicationId===a.id)||d.registers.some(r=>r.id===s.id&&r.applicationId===a.id)));
  assert.deepEqual(result,await askCase(d,a.id,'Summarize this case'));
 }
 assert.equal(JSON.stringify(d),snapshot);
});
test('assistant refuses out-of-scope or missing cases and invalid questions',async()=>{
 const d=seedDemo();d.persona={role:'institution',institutionId:'INST-2'};
 await assert.rejects(askCase(d,'CW-2026-001','Summarize this case'),/scope/);
 await assert.rejects(askCase(d,'missing','summary'),/scope/);
 await assert.rejects(askCase(d,'CW-2026-002',' '),/Enter/);
 await assert.rejects(askCase(d,'CW-2026-002','x'.repeat(501)),/500/);
 assert.equal((await askCase(d,'CW-2026-002','summary')).caseId,'CW-2026-002');
});
test('drafts cannot invent deficiency reasons, recipients or send/approve anything',async()=>{
 const d=seedDemo(),a=d.applications[1];a.reason='';delete a.contactEmail;
 const before=JSON.stringify(d),draft=await askCase(d,a.id,'Draft a deficiency letter');
 assert.equal(draft.draft,true);assert.match(draft.body,/No deficiency reason is recorded/);assert.match(draft.body,/recipient unavailable/);assert.match(draft.body,/has not been sent/);assert.equal(JSON.stringify(d),before);
 a.reason='Clarify laboratory capacity';const updated=await askCase(d,a.id,'Draft a deficiency letter');assert.match(updated.body,/Clarify laboratory capacity/);
});
test('unknown questions remain unavailable; pending evidence and pause stay explicit',async()=>{
 const d=seedDemo(),a=d.applications[1];a.pausedAt=d.clock;
 const summary=await askCase(d,a.id,'Summarize this case');assert.match(summary.body,/Clock paused/);
 const unknown=await askCase(d,a.id,'What is the director salary?');assert.equal(unknown.title,'Information unavailable');assert.match(unknown.body,/unavailable/);
 const pending=await askCase(d,a.id,'Explain what is pending');assert.match(pending.body,/separate from verification/);
 const decision=await askCase(d,a.id,'Was approval granted?');assert.match(decision.body,/No additional inspection result or statutory approval can be inferred/);
});

test('missing timing and stage facts stay unavailable rather than NaN or invented dates',async()=>{
 const d=seedDemo(),a=d.applications[1];delete a.due;delete a.stage;delete a.ruleVersion;a.pausedAt=d.clock;
 const r=await askCase(d,a.id,'Summarize this case');assert.match(r.body,/Timing information unavailable/);assert.match(r.body,/Stage unavailable/);assert.doesNotMatch(r.body,/NaN|undefined/);assert.ok(!r.sources.some(s=>s.id.startsWith('rule-')));
 const draft=await askCase(d,a.id,'Draft a reminder');assert.match(draft.body,/target of unavailable/);assert.doesNotMatch(draft.body,/undefined|null|NaN/);
});

test('EVC blockers and drafts use recorded committee, deadline and linked action',async()=>{const d=seedDemo();const a=d.applications.find(a=>a.stage.startsWith('EVC')&&a.due<d.clock);const e=d.evc.find(e=>e.applicationId===a.id);const r=await askCase(d,a.id,'What is blocking progress?');assert.ok(r.body.includes(a.due));assert.ok(r.body.includes(e.committee||'unavailable'));assert.equal(r.suggestedAction.path,`registers/${e.id}`);assert.ok(r.sources.some(s=>s.id===e.id));assert.match(r.body,/reason for delay is unavailable|Recorded return reason/);const draft=await askCase(d,a.id,'Draft a reminder');assert.ok(draft.body.includes(e.committee||'unavailable'));});
