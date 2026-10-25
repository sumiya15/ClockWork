export const START_DATE = '2026-10-25';
export const REGIONS = ['North', 'South', 'East', 'West'];
export const STAGES = ['Scrutiny', 'EVC scheduling', 'EVC visit', 'EVC report', 'SAC/SHC', 'Human decision'];
export const ROUTES = {
  'Only Scrutiny': ['Scrutiny', 'Human decision'],
  'Scrutiny + EVC': ['Scrutiny', 'EVC scheduling', 'EVC visit', 'EVC report', 'Human decision'],
  'EVC + SAC/SHC': ['EVC scheduling', 'EVC visit', 'EVC report', 'SAC/SHC', 'Human decision'],
  'Only EVC': ['EVC scheduling', 'EVC visit', 'EVC report', 'Human decision'],
};
export const addDays = (date, days) => new Date(Date.parse(`${date}T00:00:00Z`) + days * 86400000).toISOString().slice(0, 10);
export const difference = (end, start) => Math.round((Date.parse(`${end}T00:00:00Z`) - Date.parse(`${start}T00:00:00Z`)) / 86400000);
export const validDate = date => typeof date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(date) && Number.isFinite(Date.parse(date)) && new Date(date).toISOString().slice(0, 10) === date;
export const ownerFor = (region, stage) => stage.includes('EVC') ? `${region} EVC Committee` : stage === 'SAC/SHC' ? `${region} SAC Committee` : `${region} Review Desk`;
export const DEFAULT_PERSONA = { role: 'bureau', region: 'South', institutionId: 'INST-2', committee: 'South EVC Committee' };
export const defaultRule = () => ({ version: 1, label: 'DEMO-CW', routes: JSON.parse(JSON.stringify(ROUTES)), timelines: { Scrutiny: 14, 'EVC scheduling': 7, 'EVC visit': 7, 'EVC report': 7, 'SAC/SHC': 14, 'Human decision': 14 }, pausable: ['Scrutiny', 'SAC/SHC'], reminders: [7, 3, 0], escalations: [1, 7, 14] });
export function enrich(data) {
  const rule = defaultRule();
  data.schemaVersion = 2; data.clock = START_DATE; data.persona = { ...DEFAULT_PERSONA }; data.rules = [rule]; data.notifications = []; data.milestones = []; data.activity = []; data.evc = [];
  data.applications.forEach(a => {
    Object.assign(a, { ruleVersion: 1, stageStarted: a.submitted, pausedAt: a.status === 'Awaiting clarification' && rule.pausable.includes(a.stage) ? START_DATE : null, pausedDays: 0, pauseIntervals: [], attempts: 0, stageEpoch: 1, completedStages: [] });
    if (a.pausedAt) a.pauseIntervals.push({ start: START_DATE, end: null, stage: a.stage, reason: a.reason || 'Seeded clarification' });
    if (rule.routes[a.route].includes('EVC scheduling') && rule.routes[a.route].indexOf(a.stage) >= rule.routes[a.route].indexOf('EVC scheduling')) {
      const past = !['EVC scheduling', 'EVC visit', 'EVC report'].includes(a.stage);
      data.evc.push({ id: `EVC-${a.id}`, applicationId: a.id, queued: a.submitted, committee: a.stage === 'EVC scheduling' ? '' : `${a.region} EVC Committee`, visitDate: a.stage === 'EVC scheduling' ? '' : addDays(START_DATE, -3), scheduling: a.stage === 'EVC scheduling' ? 'Queued' : 'Scheduled', completion: a.stage === 'EVC scheduling' || a.stage === 'EVC visit' ? 'Pending' : 'Completed', report: past ? 'Verified' : 'Pending' });
    }
  });
  data.registers.forEach(r => {
    Object.assign(r, { ruleVersion: 1, issueDate: addDays(r.due, -365), expiryDate: r.kind === 'Lease validity' ? r.due : null, renewalHistory: [], submissions: [], revision: 1 });
    if (r.state === 'Evidence submitted') r.pending = { filename: r.filename || 'fictional-evidence.pdf', submitted: START_DATE, reason: 'Seeded fictional submission', issueDate: START_DATE, expiryDate: addDays(START_DATE, 365) };
  });
  return data;
}
export function seedDemo() {
  const names = ['Aster Valley', 'Cedar', 'Juniper Heights', 'Meridian Grove', 'Willowbridge', 'Orchid Vale', 'Silverbrook', 'Maple Crest', 'Riverstone', 'Pinehaven', 'Cobalt Ridge', 'Meadowgate', 'Harborfield', 'Elmstead', 'Summit Glen'];
  const stages = ['Scrutiny','EVC scheduling','EVC visit','EVC report','SAC/SHC','Human decision','Scrutiny','Scrutiny','EVC visit','EVC report','Human decision','Scrutiny','EVC visit','Human decision','EVC report'];
  const routes = ['Scrutiny + EVC','Only EVC','Scrutiny + EVC','EVC + SAC/SHC','EVC + SAC/SHC','Only Scrutiny','Only Scrutiny','Scrutiny + EVC','Only EVC','EVC + SAC/SHC','Scrutiny + EVC','Only Scrutiny','Only EVC','Only Scrutiny','Scrutiny + EVC'];
  const applications = Array.from({length:60},(_,i)=>{
    const group=Math.floor(i/4), region=REGIONS[i%4], stage=stages[group], route=routes[group];
    const institution = i===1 ? 'Cedar Technical Institute' : `${names[(group+i%4)%names.length]} ${['Institute of Technology','Technical College','College of Engineering','Polytechnic'][i%4]}`;
    const elapsed = group===0 ? 9 : [3,12,22,5,17][(group+i%4)%5];
    const started=addDays(START_DATE,-elapsed), due=addDays(started,defaultRule().timelines[stage]);
    return {id:`CW-2026-${String(i+1).padStart(3,'0')}`,institutionId:`INST-${i+1}`,institution,region,type:(group+i%4)%3===0?'New institution':'Existing institution',contactEmail:`approvals.inst${i+1}@example.org`,route,stage,owner:stage.includes('EVC')||stage==='SAC/SHC'?ownerFor(region,stage):`${region} Review Desk ${i%2+1}`,due,submitted:addDays(started,-(ROUTES[route].indexOf(stage)*8)),status:group===6?'Awaiting clarification':group===7?'Resubmitted':[10,13].includes(group)?'Completed':'In progress',reason:group===6?'Clarify the accessible laboratory layout and equipment inventory.':'',history:[],version:1,seedStageStarted:started};
  });
  const conditions=['Submit the commissioned laboratory equipment inventory.','Provide the updated accessible campus plan.','Confirm the library resource procurement schedule.','Submit the approved faculty recruitment progress statement.'];
  const registers=applications.flatMap((a,i)=>{
    const group=Math.floor(i/4), state=['Awaiting evidence','Evidence submitted','Verified','Rejected'][group%4];
    return [{id:i===1?'REG-DEMO-U':`UND-${String(i+1).padStart(3,'0')}`,applicationId:a.id,kind:'Undertaking',title:i===1?'Cedar laboratory equipment undertaking':`${['Laboratory equipment','Campus accessibility','Library resources','Faculty recruitment'][i%4]} undertaking`,condition:conditions[i===1?0:i%4],due:addDays(START_DATE,i===1?7:[-5,3,12,24][group%4]),state:i===1?'Awaiting evidence':state,filename:state==='Evidence submitted'?'equipment-inventory-demo.pdf':''},
      {id:i===1?'REG-DEMO-L':`DOC-${String(i+1).padStart(3,'0')}`,applicationId:a.id,kind:'Lease validity',title:i===1?'Cedar campus lease renewal':'Campus lease validity',condition:'Maintain verified campus occupancy documentation through the approval period.',due:addDays(START_DATE,i===1?-2:[180,18,-8,-3,65][group%5]),state:i===1?'Awaiting evidence':group%5===3?'Evidence submitted':'Verified',filename:group%5===3?'campus-renewal-demo.pdf':''}];
  });
  const d=enrich({applications,registers}); d.schemaVersion=3;
  d.applications.forEach((a,i)=>{
    const group=Math.floor(i/4), route=ROUTES[a.route]; a.stageStarted=a.seedStageStarted; delete a.seedStageStarted;
    a.communications=[{id:`ACK-${a.id}`,template:'Acknowledgement v1',date:a.submitted,recipient:a.contactEmail,text:`Application ${a.id} received for ${a.route}. Assigned to ${a.region} Region. Fictional acknowledgement; not sent.`}];
    a.history=[{title:'Application received',detail:`Fictional ${a.type.toLowerCase()} application entered on ${a.route}.`,date:a.submitted,actor:'Institution (seeded demo)'}];
    a.completedStages=route.slice(0,route.indexOf(a.stage)).map((stage,j)=>({stage,started:addDays(a.submitted,j*8),completed:addDays(a.submitted,(j+1)*8),activeDays:8}));
    a.completedStages.forEach(c=>a.history.push({title:`${c.stage} completed`,detail:'Seeded fictional checklist reviewed by the assigned officer or committee.',date:c.completed,actor:'Review team (seeded demo)'}));
    if(group===6){ a.history.push({title:'Returned for clarification',detail:a.reason,date:START_DATE,actor:a.owner}); a.communications.push({id:`DEF-${a.id}`,template:'Deficiency notice v1',date:START_DATE,recipient:a.contactEmail,text:`${a.id}: ${a.reason} Please submit a clarification. Demo notice; not sent.`}); }
    if(group===7){a.attempts=1;a.pausedDays=3;a.pauseIntervals=[{start:addDays(START_DATE,-7),end:addDays(START_DATE,-4),stage:a.stage,reason:'Equipment schedule clarification'}];a.due=addDays(a.due,3);a.history.push({title:'Institution resubmitted',detail:'Updated equipment schedule supplied; three paused days retained.',date:addDays(START_DATE,-4),actor:'Institution (seeded demo)'});}
    if(a.status==='Completed'){a.completedAt=addDays(START_DATE,-1);a.decision='Approved in seeded simulation';a.history.push({title:'Simulated human decision recorded',detail:'Fictional completed case; no real statutory approval was issued.',date:a.completedAt,actor:'Competent authority (seeded simulation)'});}
    const e=d.evc.find(e=>e.applicationId===a.id);
    if(e){e.queued=a.completedStages.find(c=>c.stage==='Scrutiny')?.completed||a.submitted;if(e.scheduling==='Scheduled')e.visitDate=a.stage==='EVC visit'?a.due:addDays(a.stageStarted,-1);if(group===9)e.report='Submitted';}
  });
  d.registers.forEach(r=>{if(r.state==='Verified')r.verifiedOn=addDays(START_DATE,-12);if(r.state==='Rejected')r.submissions.push({filename:'equipment-list-demo.pdf',outcome:'Rejected',decisionDate:addDays(START_DATE,-3),decisionReason:'Include serial numbers and installation dates.',actor:'Regional officer (seeded demo)'});});
  return d;
}
export const isOpen = a => a.status !== 'Completed';
export const isActive = a => ['In progress','Resubmitted'].includes(a.status);
export const ruleFor = (data, record) => data.rules.find(r => r.version === record.ruleVersion);
export const effectiveDue = (data, app) => app.pausedAt ? addDays(app.due, difference(data.clock, app.pausedAt)) : app.due;
export const remaining = (data, app) => difference(effectiveDue(data, app), data.clock);
export const activeDays = (data, app) => Math.max(0, difference(data.clock, app.stageStarted) - app.pausedDays - (app.pausedAt ? difference(data.clock, app.pausedAt) : 0));
export function visible(data, a) {
  const p = data.persona;
  return ['bureau', 'admin'].includes(p.role) || p.role === 'regional' && p.region === a.region || p.role === 'institution' && p.institutionId === a.institutionId || p.role === 'committee' && (a.stage === 'SAC/SHC' && a.owner === p.committee || data.evc.some(e => e.applicationId === a.id && e.committee === p.committee));
}
export const isOfficer = (data, a) => data.persona.role === 'bureau' || data.persona.role === 'regional' && data.persona.region === a.region;
export function can(data, a, action) {
  if (!visible(data, a)) return false;
  if (!isOpen(a) && !['submit','verify','reject'].includes(action)) return false;
  if (action === 'submit' || action === 'resubmit') return data.persona.role === 'institution' && data.persona.institutionId === a.institutionId;
  if (['verify', 'reject', 'schedule'].includes(action)) return isOfficer(data, a);
  if (['complete', 'return'].includes(action)) return a.stage !== 'Human decision' && (a.stage.includes('EVC') ? data.persona.role === 'committee' && a.owner === data.persona.committee && data.evc.some(e => e.applicationId === a.id && e.committee === data.persona.committee) : a.stage === 'SAC/SHC' ? data.persona.role === 'committee' && a.owner === data.persona.committee : isOfficer(data, a));
  return false;
}
export const scopedApps = data => data.applications.filter(a => visible(data, a));
export const validity = (data, r) => r.kind === 'Lease validity' ? difference(r.expiryDate, data.clock) < 0 ? 'Expired' : difference(r.expiryDate, data.clock) <= 30 ? 'Expiring' : 'Valid' : r.state === 'Verified' ? 'Compliant' : difference(r.due, data.clock) < 0 ? 'Overdue' : 'Pending';
