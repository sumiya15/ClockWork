import CampusImage from './CampusImage.jsx';
export function InstitutionAvatar({app,cover=false}){
 const initials=(app.institution||'Institution').split(/\s+/).slice(0,2).map(w=>w[0]).join('');
 const tone=[...(app.institutionId||'')].reduce((n,c)=>n+c.charCodeAt(0),0)%5;
 return <div className={`${cover?'initials-cover':'institution-avatar'} identity-tone-${tone}`} aria-hidden="true"><span>{initials}</span>{cover&&<small>{app.region} Region / {app.institutionId}</small>}</div>;
}
// One licensed exterior is available. Never reuse interior photos as campus covers.
export function InstitutionCover({app}){return app.institutionId==='INST-2'?<CampusImage/>:<InstitutionAvatar app={app} cover/>;}
