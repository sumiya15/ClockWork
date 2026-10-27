import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {seedDemo,setPersona,remaining,activeDays,changeCase,evcAction,evidenceAction,scan,targets,difference,validity,isOpen} from '../src/demo/service.js';
import {report,REPORTS} from '../src/demo/reports.js';
const seed=seedDemo(),id='CW-2026-002',a=d=>d.applications.find(x=>x.id===id),as=(d,role,extra={})=>setPersona(d,{role,...extra}),reason='Fictional measured demonstration';
const results={date:'2026-10-26',method:'Direct production frontend functions with assertions; fresh independent synthetic seed per scenario.',dataset:{applications:seed.applications.length,institutions:new Set(seed.applications.map(a=>a.institutionId)).size,regions:new Set(seed.applications.map(a=>a.region)).size,undertakings:seed.registers.filter(r=>r.kind==='Undertaking').length,leases:seed.registers.filter(r=>r.kind==='Lease validity').length,evc:seed.evc.length},routes:[]};
for(const route of Object.keys(seed.rules[0].routes)){
 let d=seedDemo();Object.assign(a(d),{route,stage:d.rules[0].routes[route][0],owner:route.startsWith('Only Scrutiny')||route==='Scrutiny + EVC'?'South Review Desk':'South EVC Committee'});
 if(a(d).stage==='EVC scheduling')d.evc.push({id:`EVC-${id}`,applicationId:id,committee:'',scheduling:'Queued',completion:'Pending',report:'Pending'});
 const observed=[a(d).stage];
 while(a(d).stage!=='Human decision'){
  const stage=a(d).stage;
  if(stage==='EVC scheduling')d=evcAction(as(d,'regional'),id,'schedule',{committee:'South EVC Committee',visitDate:d.clock,reason});
  else if(stage==='EVC visit')d=evcAction(as(d,'committee',{committee:'South EVC Committee'}),id,'visit',{reason});
  else if(stage==='EVC report'){d=evcAction(as(d,'committee',{committee:'South EVC Committee'}),id,'report',{reason});assert.equal(a(d).stage,'EVC report');d=evcAction(as(d,'bureau'),id,'verify-report',{reason});}
  else d=changeCase(as(d,stage==='SAC/SHC'?'committee':'regional',{committee:'South SAC Committee'}),id,'complete',reason);
  observed.push(a(d).stage);assert.ok(observed.length<=10);
 }
 assert.deepEqual(observed,d.rules[0].routes[route]);assert.equal(a(d).status,'In progress');results.routes.push({route,observed,terminal:'Awaiting human decision; no approval issued'});
}
results.deadlines=[];
for(const advance of [0,1,7,30]){
 const d=advance?scan(seed,advance):seed,ts=targets(d).filter(t=>!t.paused);
 const overdue=ts.filter(t=>difference(d.clock,t.due)>0),due=ts.filter(t=>difference(d.clock,t.due)===0),upcoming=ts.filter(t=>difference(t.due,d.clock)>0&&difference(t.due,d.clock)<=7);
 for(const t of [...overdue,...due,...upcoming])assert.ok(d.notifications.some(n=>n.targetId===t.id&&n.epoch===t.epoch));
 const expected=ts.filter(t=>difference(d.clock,t.due)>0).map(t=>t.id).sort();
 // The report includes paused cases with overdue effective dates, so compare only non-paused IDs.
 const actual=report(d,'overdue').rows.filter(r=>ts.some(t=>t.id===r[0])).map(r=>r[0]).sort();assert.deepEqual(actual,expected);
 results.deadlines.push({advanceDays:advance,date:d.clock,activeTargets:ts.length,overdue:overdue.length,dueToday:due.length,upcoming7Days:upcoming.length,reportMatches:true,eligibleTargetsHaveAlerts:true,openApplicationOverdue:d.applications.filter(x=>isOpen(x)&&remaining(d,x)<0).length});
}
let d=scan(seed,30),before=d.notifications.length;for(let i=0;i<5;i++)d=scan(d);assert.equal(d.notifications.length,before);assert.equal(new Set(d.notifications.map(n=>n.id)).size,before);results.duplicates={messages:before,repeatedScans:5,added:0,duplicateIds:0};
for(const n of d.notifications.filter(n=>n.threshold>0)){const index=d.rules.find(r=>r.version===n.ruleVersion).escalations.indexOf(n.threshold);assert.equal(n.recipient,`${['Regional desk','Bureau oversight','Senior review'][Math.min(index,2)]} (fictional)`);}
results.escalationRecipients='All generated overdue application and compliance alerts match the displayed authority ladder.';
d=seedDemo();const initial={remaining:remaining(d,a(d)),activeElapsed:activeDays(d,a(d))};for(let i=0;i<2;i++){d=changeCase(as(d,'regional'),id,'return',reason);d=scan(as(d,'bureau'),7);assert.equal(remaining(d,a(d)),initial.remaining);assert.equal(activeDays(d,a(d)),initial.activeElapsed);d=changeCase(as(d,'institution'),id,'resubmit',reason);}
results.sla={initial,after:{remaining:remaining(d,a(d)),activeElapsed:activeDays(d,a(d)),pausedDays:a(d).pausedDays,resubmissions:a(d).attempts}};
results.evidence=[];
for(const rid of ['REG-DEMO-U','REG-DEMO-L']){let x=seedDemo();const r=()=>x.registers.find(r=>r.id===rid),old=r().expiryDate;x=evidenceAction(as(x,'institution'),rid,'submit',{filename:'fictional.pdf',size:23,reason,issueDate:x.clock,expiryDate:'2027-10-25'});assert.equal(r().state,'Evidence submitted');assert.equal(r().expiryDate,old);const pending={state:r().state,validity:validity(x,r()),expiry:r().expiryDate};assert.throws(()=>evidenceAction(as(x,'institution'),rid,'verify',{reason}),/persona/);x=evidenceAction(as(x,'bureau'),rid,'verify',{reason});assert.equal(r().state,'Verified');results.evidence.push({id:rid,pending,verified:{state:r().state,validity:validity(x,r()),expiry:r().expiryDate,history:r().renewalHistory.length}});}
results.reports=Object.keys(REPORTS).map(type=>({type,rows:report(seed,type).rows.length}));
results.limitations=['Synthetic functional scenarios, not production accuracy or time-savings measurement.','Four route tests reset one seeded case to each initial stage; browser presentation journey exercises Scrutiny + EVC.','No backend, file bytes, communications delivery or official APH verification.','Reminder evaluation coalesces crossed milestones per target/channel; repeated scans are measured at fixed time.'];
await mkdir('../docs/presentation/evidence',{recursive:true});await writeFile('../docs/presentation/evidence/measurements.json',JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2));
