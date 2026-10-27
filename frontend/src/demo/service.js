import { START_DATE, STAGES, ROUTES, REGIONS, seedDemo as seedModel, enrich, isOpen, isActive, addDays, difference, validDate, ruleFor, effectiveDue, activeDays, can, visible, ownerFor } from './model.js';
export * from './model.js';
const KEY = 'clockwork.presentation.v3';
export function seedDemo() { return evaluate(seedModel()); }
const copy = value => JSON.parse(JSON.stringify(value));
const requireThat = (condition, message) => { if (!condition) throw new Error(message); };
const reasonText = reason => { requireThat(typeof reason === 'string' && reason.trim().length > 0 && reason.trim().length <= 1000, 'Enter a reason or observation (1–1000 characters).'); return reason.trim(); };
export function loadDemo() {
  try {
    const raw = window.localStorage.getItem(KEY);
    if (raw) {
      const d = JSON.parse(raw);
      requireThat(d.schemaVersion === 3 && d.applications.length >= 50 && validDate(d.clock) && Array.isArray(d.rules) && Array.isArray(d.evc) && Array.isArray(d.notifications) && d.applications.every(a => ruleFor(d, a)?.routes[a.route]?.includes(a.stage)), 'Unsupported saved data');
      return { data: d, warning: '' };
    }
    const prior = window.localStorage.getItem('clockwork.presentation.v2');
    if (prior) { const d=JSON.parse(prior); requireThat(d.schemaVersion===2 && Array.isArray(d.applications), 'Invalid prior snapshot'); d.schemaVersion=3; return {data:d,warning:'Your saved demo is preserved. Open Demo controls and Reset Demo to load the improved 60-case mobile seed. The v2 copy remains untouched.'}; }
    const legacy = window.localStorage.getItem('clockwork.presentation.v1');
    if (legacy) {
      const old = JSON.parse(legacy);
      requireThat(old.schemaVersion === 1 && old.applications?.length === 50 && Array.isArray(old.registers), 'Invalid legacy data');
      const upgraded = enrich(old); upgraded.schemaVersion=3;
      requireThat(upgraded.applications.every(a => ruleFor(upgraded, a)?.routes[a.route]?.includes(a.stage)), 'Unsupported legacy route');
      return { data: upgraded, warning: 'Existing local cases retained. Use Reset Demo for the improved 60-case mobile fixtures. The v1 storage copy remains untouched.' };
    }
    return { data: seedDemo(), warning: '' };
  } catch { return { data: seedDemo(), warning: 'Saved data could not be read. Original fictional data is displayed; Reset Demo explicitly replaces only the v3 demo snapshot.' }; }
}
export function saveDemo(data) { window.localStorage.setItem(KEY, JSON.stringify(data)); }
const actor = data => `${data.persona.role} / ${data.persona.role === 'institution' ? data.persona.institutionId : data.persona.role === 'committee' ? data.persona.committee : data.persona.role === 'regional' ? data.persona.region : 'all Regions'}`;
function event(d, a, title, detail, actorOverride) {
  const entry = { id: `ACT-${d.activity.length + 1}`, applicationId: a?.id || null, title, detail, date: d.clock, realAt: new Date().toISOString(), actor: actorOverride || actor(d) };
  d.activity.push(entry); if (a) { a.history.push(entry); a.version += 1; if (title === 'Returned for clarification' || title === 'Institution resubmitted') { a.communications ||= []; a.communications.push({id:`COMM-${entry.id}`,template:title === 'Returned for clarification' ? 'Deficiency notice v1' : 'Resubmission acknowledgement v1',date:d.clock,recipient:a.contactEmail || 'institution@example.org',text:`${a.id}: ${detail} Simulated communication; not sent.`}); } }
}
function appFor(d, id, action, version) {
  const a = d.applications.find(x => x.id === id);
  requireThat(a && can(d, a, action), 'This simulated persona cannot perform that action for this case.');
  if (version !== undefined) requireThat(a.version === version, 'This case changed. Refresh the action and try again.');
  return a;
}
function enqueueEvc(d, a) {
  if (!d.evc.some(e => e.applicationId === a.id)) d.evc.push({ id: `EVC-${a.id}`, applicationId: a.id, queued: d.clock, committee: '', visitDate: '', scheduling: 'Queued', completion: 'Pending', report: 'Pending' });
}
function nextStage(d, a) {
  const rule = ruleFor(d, a), route = rule.routes[a.route];
  const next = route[route.indexOf(a.stage) + 1];
  requireThat(next, 'The final statutory decision remains with the competent human authority.');
  a.completedStages.push({ stage: a.stage, completed: d.clock, activeDays: activeDays(d, a), started: a.stageStarted });
  a.stage = next; a.stageEpoch += 1; a.stageStarted = d.clock; a.pausedDays = 0; a.pausedAt = null;
  a.owner = ownerFor(a.region, next); a.due = addDays(d.clock, rule.timelines[next]); a.status = 'In progress'; a.reason = '';
  if (next === 'EVC scheduling') enqueueEvc(d, a);
}
export function changeCase(data, id, action, reason, version) {
  const d = copy(data), a = appFor(d, id, action, version), text = reasonText(reason), stage = a.stage;
  if (action === 'return') {
    requireThat(isActive(a), 'Only an in-progress stage can be returned.');
    a.status = 'Awaiting clarification'; a.reason = text;
    if (ruleFor(d, a).pausable.includes(a.stage)) { a.pausedAt = d.clock; a.pauseIntervals.push({ start: d.clock, end: null, stage: a.stage, reason: text }); }
    event(d, a, 'Returned for clarification', `${text} ${a.pausedAt ? 'Configured SLA paused.' : 'This stage clock continues under its rule.'}`);
  } else if (action === 'resubmit') {
    requireThat(a.status === 'Awaiting clarification', 'This case is not awaiting clarification.');
    if (a.pausedAt) {
      const elapsed = difference(d.clock, a.pausedAt); a.due = addDays(a.due, elapsed); a.pausedDays += elapsed;
      const interval = a.pauseIntervals.findLast(p => p.end === null); if (interval) interval.end = d.clock;
      a.pausedAt = null;
    }
    a.status = 'Resubmitted'; a.reason = ''; a.attempts += 1;
    event(d, a, 'Institution resubmitted', `${text} Attempt ${a.attempts}; remaining SLA preserved.`);
  } else {
    requireThat(action === 'complete' && isActive(a), 'Invalid stage transition.');
    requireThat(!a.stage.includes('EVC'), 'Use the EVC register for scheduling, visit completion, and report actions.');
    nextStage(d, a); event(d, a, `${stage} completed`, text);
  }
  return d;
}
export function evcAction(data, id, action, fields) {
  const d = copy(data), a = appFor(d, id, action === 'schedule' ? 'schedule' : action === 'verify-report' ? 'verify' : 'complete', fields.version);
  const e = d.evc.find(x => x.applicationId === id), text = reasonText(fields.reason);
  requireThat(e && isActive(a), 'An active EVC queue item is required.');
  if (action === 'schedule') {
    requireThat(e.scheduling === 'Queued' && a.stage === 'EVC scheduling', 'Visit already scheduled or no longer eligible.');
    requireThat(fields.committee === `${a.region} EVC Committee`, 'Assign an explicit EVC committee in the application Region.');
    requireThat(validDate(fields.visitDate) && fields.visitDate >= d.clock, 'Choose a visit date on or after demo today.');
    e.committee = fields.committee; e.visitDate = fields.visitDate; e.scheduling = 'Scheduled'; nextStage(d, a); a.due = fields.visitDate; a.owner = e.committee;
  } else if (action === 'visit') {
    requireThat(a.stage === 'EVC visit' && e.completion === 'Pending' && e.visitDate <= d.clock, 'A scheduled visit must reach its visit date before completion.');
    e.completion = 'Completed'; e.completedOn = d.clock; nextStage(d, a); a.owner = e.committee;
  } else if (action === 'report') {
    requireThat(a.stage === 'EVC report' && e.completion === 'Completed' && e.report === 'Pending', 'Complete the visit before submitting its report.');
    e.report = 'Submitted'; e.reportedOn = d.clock;
  } else if (action === 'verify-report') {
    requireThat(a.stage === 'EVC report' && e.report === 'Submitted', 'Submit the committee report before officer verification.');
    e.report = 'Verified'; e.verifiedOn = d.clock; nextStage(d, a);
  } else throw new Error('Unknown EVC action.');
  event(d, a, { schedule: 'EVC scheduled', visit: 'EVC visit completed', report: 'EVC report submitted', 'verify-report': 'EVC report verified' }[action], `${text}${action === 'schedule' ? ` ${e.committee}; visit ${e.visitDate}.` : ''}`);
  return d;
}
export function evidenceAction(data, id, action, fields, focused = false) {
  const d = copy(data), r = d.registers.find(x => x.id === id); requireThat(r, 'Evidence target not found.');
  const a = d.applications.find(x => x.id === r.applicationId);
  // Focused links are explicitly public local simulations, not security credentials.
  if (!focused || action !== 'submit') requireThat(can(d, a, action), 'This simulated persona cannot act on this evidence.');
  const text = reasonText(fields.reason);
  if (action === 'submit') {
    requireThat(r.state !== 'Evidence submitted', 'An evidence submission is already awaiting verification.');
    requireThat(r.kind === 'Lease validity' || r.state !== 'Verified', 'This undertaking is already verified.');
    requireThat(typeof fields.filename === 'string' && /\.(pdf|png|jpe?g)$/i.test(fields.filename) && fields.size > 0 && fields.size <= 5 * 1024 * 1024, 'Choose a nonempty PDF, PNG or JPG up to 5 MB.');
    if (r.kind === 'Lease validity') requireThat(validDate(fields.issueDate) && validDate(fields.expiryDate) && fields.issueDate <= d.clock && fields.expiryDate > fields.issueDate && fields.expiryDate > r.expiryDate && fields.expiryDate > d.clock, 'Renewal issue date must be on/before today; expiry must follow issue, current expiry and today.');
    r.pending = { filename: fields.filename, size: fields.size, submitted: d.clock, reason: text, issueDate: fields.issueDate || null, expiryDate: fields.expiryDate || null };
    r.state = 'Evidence submitted'; r.filename = fields.filename;
    event(d, a, 'Evidence submitted', `${r.id}: ${text}. Filename metadata only; officer verification pending.`, focused ? `institution-link / ${a.institutionId} (simulated)` : undefined);
  } else {
    requireThat(['verify', 'reject'].includes(action) && r.pending && r.state === 'Evidence submitted', 'Evidence must be pending before verification or rejection.');
    r.submissions.push({ ...r.pending, outcome: action === 'verify' ? 'Verified' : 'Rejected', decisionDate: d.clock, decisionReason: text, actor: actor(d) });
    if (action === 'verify') {
      if (r.kind === 'Lease validity') { r.renewalHistory.push({ issueDate: r.issueDate, expiryDate: r.expiryDate, replacedOn: d.clock }); r.issueDate = r.pending.issueDate; r.expiryDate = r.pending.expiryDate; r.due = r.expiryDate; r.revision += 1; }
      r.state = 'Verified'; r.verifiedOn = d.clock;
    } else r.state = 'Rejected';
    r.pending = null; event(d, a, `Evidence ${action === 'verify' ? 'verified' : 'rejected'}`, `${r.id}: ${text}`);
  }
  return d;
}
export function targets(data) {
  return [
    ...data.applications.filter(isOpen).map(a => ({ id: a.id, applicationId: a.id, epoch: a.stageEpoch, ruleVersion: a.ruleVersion, due: effectiveDue(data, a), paused: !!a.pausedAt, title: `${a.stage}: ${a.institution}`, path: `case/${a.id}` })),
    ...data.registers.filter(r => r.kind === 'Lease validity' || r.state !== 'Verified').map(r => ({ id: r.id, applicationId: r.applicationId, epoch: r.revision, ruleVersion: r.ruleVersion, due: r.due, paused: false, title: r.title, path: `upload/${r.id}`, register: true })),
  ];
}
function evaluate(d) {
  for (const target of targets(d).filter(t => !t.paused)) {
    const rule = ruleFor(d, target), elapsed = difference(d.clock, target.due);
    const thresholds = [...rule.reminders.map(n => -n), ...rule.escalations].sort((a, b) => a - b);
    const newly = thresholds.filter(t => elapsed >= t && !d.milestones.some(m => m.key === `${target.id}:${target.epoch}:v${rule.version}:${t}`));
    if (!newly.length) continue;
    newly.forEach(threshold => d.milestones.push({ key: `${target.id}:${target.epoch}:v${rule.version}:${threshold}`, targetId: target.id, epoch: target.epoch, ruleVersion: rule.version, threshold, date: d.clock, why: `DEMO-CW v${rule.version}: ${target.title}; due ${target.due}; ${elapsed} days after due on ${d.clock}; crossed ${threshold < 0 ? `${-threshold} days before due` : `${threshold} days after due`}.` }));
    const threshold = Math.max(...newly), why = d.milestones.find(m => m.key === `${target.id}:${target.epoch}:v${rule.version}:${threshold}`).why;
    const authority = ['Regional desk', 'Bureau oversight', 'Senior review'][Math.min(rule.escalations.indexOf(threshold), 2)];
    const recipient = threshold > 0 ? `${authority} (fictional)` : target.register ? 'Institution evidence contact (fictional)' : `${d.applications.find(a => a.id === target.applicationId).owner} (fictional)`;
    for (const channel of ['email', 'SMS', 'WhatsApp']) d.notifications.push({ id: `${target.id}:${target.epoch}:v${rule.version}:${threshold}:${channel}`, targetId: target.id, applicationId: target.applicationId, epoch: target.epoch, ruleVersion: rule.version, threshold, why, date: d.clock, title: target.title, channel, status: 'Simulated — not sent', path: target.path, coalesced: newly.length, recipient });
    const a = d.applications.find(x => x.id === target.applicationId);
    event(d, a, threshold > 0 ? 'Demo escalation recorded' : 'Demo reminder recorded', `${why} ${newly.length} milestone(s) recorded; one message per simulated channel.`);
  }
  return d;
}
export function scan(data, advance = 0) {
  requireThat(['bureau', 'admin'].includes(data.persona.role), 'Use bureau or admin persona for demo clock and scans.');
  requireThat([0, 1, 7, 30].includes(advance), 'Advance by 1, 7 or 30 days. Backward time is not supported.');
  const d = copy(data); d.clock = addDays(d.clock, advance);
  if (advance) event(d, null, 'Demo clock advanced', `Advanced ${advance} calendar days to ${d.clock}.`);
  return evaluate(d);
}
export function setPersona(data, changes) { return { ...data, persona: { ...data.persona, ...changes } }; }
export function validateRule(raw) {
  const r = copy(raw);
  requireThat(r && typeof r === 'object', 'Provide a rule object.');
  requireThat(STAGES.every(s => Number.isInteger(r.timelines?.[s]) && r.timelines[s] >= 1 && r.timelines[s] <= 365), 'Every timeline must be an integer from 1 to 365 days.');
  for (const [key, min] of [['reminders', 0], ['escalations', 1]]) requireThat(Array.isArray(r[key]) && r[key].length > 0 && r[key].length <= 6 && r[key].every(n => Number.isInteger(n) && n >= min && n <= 365) && new Set(r[key]).size === r[key].length, `${key}: use 1–6 distinct integer day offsets (${min}–365).`);
  requireThat(Array.isArray(r.pausable) && r.pausable.every(s => STAGES.includes(s) && s !== 'Human decision'), 'Pause settings must use supported non-decision stages.');
  requireThat(Object.keys(r.routes || {}).length === 4 && Object.keys(ROUTES).every(k => Array.isArray(r.routes[k])), 'Configure all four named routes.');
  Object.values(r.routes).forEach(route => {
    requireThat(route.length >= 2 && new Set(route).size === route.length && route.every(s => STAGES.includes(s)) && route.at(-1) === 'Human decision', 'Routes need unique supported stages and must end with Human decision.');
    if (route.some(s => s.includes('EVC'))) requireThat(['EVC scheduling', 'EVC visit', 'EVC report'].every((s, i) => route[route.indexOf('EVC scheduling') + i] === s), 'EVC routes must include scheduling → visit → report in that order.');
    requireThat(!route.includes('Scrutiny') || route[0] === 'Scrutiny', 'Scrutiny must be first when present.');
  });
  return { version: r.version, label: 'DEMO-CW', timelines: r.timelines, reminders: [...r.reminders].sort((a,b) => b-a), escalations: [...r.escalations].sort((a,b) => a-b), routes: r.routes, pausable: r.pausable };
}
export function previewRule(data, raw, migrate) {
  requireThat(data.persona.role === 'admin', 'Only the simulated admin edits rules.');
  const rule = validateRule(raw);
  const changes = migrate ? data.applications.map(a => {
    requireThat(rule.routes[a.route].includes(a.stage), `Cannot migrate ${a.id}: its current stage would disappear.`);
    const oldRoute = ruleFor(data, a).routes[a.route], proposed = rule.routes[a.route];
    requireThat(JSON.stringify(oldRoute.slice(0, oldRoute.indexOf(a.stage) + 1)) === JSON.stringify(proposed.slice(0, proposed.indexOf(a.stage) + 1)), `Cannot rewrite the traversed route for ${a.id}. Future stages may change.`);
    requireThat(!a.pausedAt || rule.pausable.includes(a.stage), `Resume ${a.id} before removing its pause setting.`);
    return { id: a.id, before: effectiveDue(data, a), after: a.stage === 'EVC visit' ? a.due : addDays(a.stageStarted, rule.timelines[a.stage] + a.pausedDays + (a.pausedAt ? difference(data.clock, a.pausedAt) : 0)) };
  }) : [];
  return { rule, changes };
}
export function publishRule(data, raw, migrate, reason) {
  const preview = previewRule(data, raw, migrate), d = copy(data), text = reasonText(reason), rule = { ...preview.rule, version: Math.max(...d.rules.map(r => r.version)) + 1 };
  d.rules.push(rule);
  if (migrate) {
    d.applications.forEach(a => { const c = preview.changes.find(x => x.id === a.id); a.due = a.pausedAt ? addDays(c.after, -difference(d.clock, a.pausedAt)) : c.after; a.ruleVersion = rule.version; event(d, a, 'Demo rule migration', `${text}. Rule v${rule.version}; active target ${c.after}.`); });
    d.registers.forEach(r => { r.ruleVersion = rule.version; });
  }
  event(d, null, 'Demo rules published', `${text}. Version ${rule.version}; ${migrate ? 'existing cases explicitly migrated' : 'existing cases retain pinned versions'}.`);
  return d;
}
export function notificationCurrent(data, n) {
  return targets(data).some(t => t.id === n.targetId && t.epoch === n.epoch && t.ruleVersion === n.ruleVersion && !t.paused && difference(data.clock, t.due) >= n.threshold);
}
export const visibleNotifications = data => data.notifications.filter(n => visible(data, data.applications.find(a => a.id === n.applicationId)));
export const committees = REGIONS.flatMap(r => [`${r} EVC Committee`, `${r} SAC Committee`]);
export { START_DATE };
