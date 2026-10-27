import {userText,statusLabel} from '../wording.js';
import {InstitutionCover} from '../InstitutionIdentity.jsx';
import {scopedApps,validity} from '../model.js';
import {Due,AppTable} from '../ui.jsx';
export default function InstitutionProfile({data,id,navigate}){
 const apps=scopedApps(data).filter(a=>!id||a.institutionId===id);
 if(!apps.length)return <p className="empty">Institution unavailable in this persona scope.</p>;
 if(!id)return <AppTable data={data} apps={apps} navigate={navigate} institutions/>;
 const app=apps[0],records=data.registers.filter(r=>apps.some(a=>a.id===r.applicationId));
 return <><p className="eyebrow">{app.institutionId} / {app.region} REGION</p><h1>{app.institution}</h1><InstitutionCover app={app}/><section className="demo-card case-section"><h2>Institution profile</h2><p className="muted">{app.type} · institution profile</p><p className="summary-text">Contact: {app.contactEmail||'Unavailable'}</p><h3>Applications ({apps.length})</h3>{apps.map(a=><button className="linked-record" key={a.id} onClick={()=>navigate(`case/${a.id}`)}><span>{a.id}<small>{a.stage} · {a.status}</small></span><span>Open</span></button>)}<button className="primary full-width" onClick={()=>navigate(`assist/${app.id}`)}>AI Assist for this case</button></section><section className="demo-card case-section"><h2>Requirements ({records.filter(r=>r.state!=='Verified').length} unverified)</h2>{records.map(r=><button className="linked-record" key={userText(r.id)} onClick={()=>navigate(`registers/${r.id}`)}><span>{r.title}<small>{userText(r.id)} · {statusLabel(r.state)} · {validity(data,r)}</small>{!(r.kind==='Undertaking'&&r.state==='Verified')&&<Due date={r.due} today={data.clock}/>}</span></button>)}</section></>;
}
