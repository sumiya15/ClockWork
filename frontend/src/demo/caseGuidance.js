export function caseGuidance(data,app){
 const evc=data.evc.find(e=>e.applicationId===app.id);
 if(app.status==='Awaiting clarification')return {label:'Review clarification',path:`case/${app.id}`};
 if(app.stage?.startsWith('EVC')&&evc)return {label:app.stage==='EVC scheduling'?'Schedule committee visit':app.stage==='EVC report'?'Review EVC report':'Review scheduled visit',path:`registers/${evc.id}`};
 return {label:app.stage==='Human decision'?'Review for human decision':'Review current stage',path:`case/${app.id}`};
}
