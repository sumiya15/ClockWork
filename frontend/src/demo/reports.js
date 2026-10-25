import { scopedApps, difference, effectiveDue, remaining, activeDays, validity, REGIONS, isOpen } from './model.js';
export const REPORTS = { pendency: 'Application pendency', evc: 'EVC status', undertakings: 'Undertaking compliance', documents: 'Document validity', overdue: 'Overdue cases', performance: 'Region-wise processing performance' };
export function filterApps(data, filters = {}) {
  return scopedApps(data).filter(a => ['region', 'stage', 'institution', 'owner'].every(k => !filters[k] || a[k] === filters[k]) && (!filters.due || isOpen(a) && remaining(data,a)>=0 && remaining(data,a)<=7) && (!filters.status || a.status === filters.status) && (!filters.overdue || isOpen(a) && remaining(data,a)<0) && (!filters.type || a.type===filters.type) && (!filters.from || a.submitted >= filters.from) && (!filters.to || a.submitted <= filters.to) && (!filters.search || `${a.id} ${a.institution}`.toLowerCase().includes(filters.search.toLowerCase())));
}
export function report(data, type, filters = {}) {
  const apps = filterApps(data, filters), ids = new Set(apps.map(a => a.id)), regs = data.registers.filter(r => ids.has(r.applicationId));
  if (type === 'pendency') return { headers: ['Application', 'Institution', 'Region', 'Stage', 'Owner', 'State', 'Submitted', 'Active due', 'Remaining days', 'Active stage days'], rows: apps.filter(isOpen).map(a => [a.id, a.institution, a.region, a.stage, a.owner, a.status, a.submitted, effectiveDue(data, a), remaining(data, a), activeDays(data, a)]) };
  if (type === 'evc') return { headers: ['Application', 'Region', 'Committee', 'Visit date', 'Scheduling', 'Visit completion', 'Report', 'Current due'], rows: data.evc.filter(e => ids.has(e.applicationId)).map(e => { const a = apps.find(a => a.id === e.applicationId); return [a.id, a.region, e.committee || 'Unassigned', e.visitDate, e.scheduling, e.completion, e.report, a.stage.includes('EVC') ? effectiveDue(data, a) : 'EVC concluded']; }) };
  if (type === 'undertakings') return { headers: ['Record', 'Application', 'Due', 'Evidence state', 'Compliance', 'Verification date'], rows: regs.filter(r => r.kind === 'Undertaking').map(r => [r.id, r.applicationId, r.due, r.state, validity(data, r), r.verifiedOn || '']) };
  if (type === 'documents') return { headers: ['Record', 'Application', 'Verified issue', 'Verified expiry', 'Validity', 'Evidence state', 'Pending expiry', 'Historical validity versions'], rows: regs.filter(r => r.kind === 'Lease validity').map(r => [r.id, r.applicationId, r.issueDate, r.expiryDate, validity(data, r), r.state, r.pending?.expiryDate || '', r.renewalHistory.length]) };
  if (type === 'overdue') return { headers: ['Record', 'Application', 'Type', 'Due', 'Days overdue', 'Paused / verification'], rows: [...apps.filter(a => isOpen(a) && remaining(data, a) < 0).map(a => [a.id, a.id, a.stage, effectiveDue(data, a), -remaining(data, a), a.pausedAt ? 'Paused' : a.status]), ...regs.filter(r => difference(r.due, data.clock) < 0 && (r.kind === 'Lease validity' || r.state !== 'Verified')).map(r => [r.id, r.applicationId, r.kind, r.due, -difference(r.due, data.clock), r.state])] };
  return { headers: ['Region', 'Stage', 'Open sample n', 'Overdue n', 'Mean open active stage days', 'Completed stage sample n', 'Mean completed active days'], rows: REGIONS.flatMap(region => [...new Set(apps.flatMap(a => [a.stage, ...a.completedStages.map(c => c.stage)]))].map(stage => {
    const open = apps.filter(a => isOpen(a) && a.region === region && a.stage === stage), complete = apps.filter(a => a.region === region).flatMap(a => a.completedStages).filter(c => c.stage === stage);
    if (!open.length && !complete.length) return null;
    return [region, stage, open.length, open.filter(a => remaining(data, a) < 0).length, open.length ? (open.reduce((sum, a) => sum + activeDays(data, a), 0) / open.length).toFixed(1) : 'Insufficient data', complete.length, complete.length ? (complete.reduce((sum, c) => sum + c.activeDays, 0) / complete.length).toFixed(1) : 'Insufficient data'];
  }).filter(Boolean)) };
}
export const csv = result => [result.headers, ...result.rows].map(row => row.map(value => { let s = String(value ?? ''); if (/^[\s]*[=+@\-]/.test(s) || /^[\t\r\n]/.test(s)) s = "'" + s; return `"${s.replaceAll('"', '""')}"`; }).join(',')).join('\r\n');
export function downloadReport(data, type, filters) {
  const result = report(data, type, filters), link = document.createElement('a');
  link.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent('\uFEFF' + csv(result)); link.download = `clockwork-demo-${type}-${data.clock}.csv`; link.click();
  return result.rows.length;
}
