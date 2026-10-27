export const readableDate=value=>/^\d{4}-\d{2}-\d{2}$/.test(value||'')?new Date(`${value}T00:00:00Z`).toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'}):value||'Unavailable';
export const plural=(count,word)=>`${count} ${word}${count===1?'':'s'}`;
export const statusLabel=value=>value==='Evidence submitted'?'Awaiting officer verification':value;
export const statusTone=value=>['Verified','Completed','Compliant','Valid'].includes(value)?'status-success':['Rejected','Expired','Overdue'].includes(value)?'status-danger':['Evidence submitted','Pending','Submitted','Queued','Awaiting clarification','Expiring'].includes(value)?'status-warning':'status-neutral';
export function alertReason(n){const due=n.why?.match(/due (\d{4}-\d{2}-\d{2})/)?.[1];return `${n.threshold>0?`Escalation after ${plural(n.threshold,'day')} overdue`:n.threshold===0?'Due-date reminder':`Reminder ${plural(-n.threshold,'day')} before due`}. ${due?`Deadline: ${readableDate(due)}. `:''}Evaluated ${readableDate(n.date)}. Rule version ${n.ruleVersion}.`;}
export function activityCopy(entry){
 const title=entry.title.replace(/^Demo /,'').replace('Evidence submitted','Evidence received');
 const detail=/^Demo (escalation|reminder) recorded$/.test(entry.title)?'Deadline reviewed and an alert recorded. Open Notifications for the deadline, recipient and explanation.':userText(entry.detail).replace(/Filename metadata only; officer verification pending\./g,'Awaiting officer verification.').replace(/\bFictional\b ?/g,'').replace(/Simulated communication; not sent\./g,'').replace(/\bDEMO-CW v\d+: /g,'');
 return {title,detail,actor:userText(entry.actor||'Initial record').replace(/institution-link \/ /,'Institution / ').replace(/ \(simulated\)/g,'').replace(/ \(seeded demo\)/g,'')};
}
export const userText=value=>String(value??'').replace(/REG-DEMO-U/g,'Laboratory undertaking').replace(/REG-DEMO-L/g,'Campus lease').replace(/\.\./g,'.').replace(/&#x20;|&#32;|&nbsp;/gi,' ').replace(/\s*\(fictional\)/gi,'').replace(/Institution evidence contact/g,'Institution document coordinator').replace(/Fictional acknowledgement; not sent\./g,'').replace(/Demo notice; not sent\./g,'').replace(/\b\d{4}-\d{2}-\d{2}\b/g,readableDate);
export function alertCopy(n){
 const due=n.why?.match(/due (\d{4}-\d{2}-\d{2})/)?.[1];
 const days=due?Math.round((Date.parse(n.date)-Date.parse(due))/86400000):null;
 const lease=/lease/i.test(n.title),overdue=days>0;
 return {title:lease&&overdue?'Campus lease expired':`${n.title}${overdue?' overdue':''}`,detail:due?`${lease&&overdue?'Expired':'Due'} ${readableDate(due)} / ${days>0?plural(days,'day')+' overdue':days===0?'Due today':plural(-days,'day')+' remaining'}`:'Deadline unavailable',action:n.path.startsWith('upload')?(lease?'Upload renewed lease':'Submit required evidence'):'Review case',recipient:userText(n.recipient)};
}
