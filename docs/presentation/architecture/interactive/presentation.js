/* Standalone, offline architecture viewer. No network calls or app-state access. */
(() => {
  'use strict';
  const positions={ui:[30,35,320,150],core:[440,35,320,150],engine:[850,35,320,150],monitor:[30,300,320,150],store:[440,300,320,150],notify:[850,300,320,150],ai:[30,520,320,110],bridge:[850,520,320,110]};
  const node=(id,title,lines,status,group,body,note,source)=>({id,title,lines,status,group,body,note,source});
  const target=[
    node('ui','Users + React interface',['Institution · region · bureau','Committee · admin'],'design','1 · Users and mobile interface','A role-based interface connects institutions, regional officers, bureau officers, committees and administrators to a shared workflow. Authenticated APIs provide records and actions within each assigned scope.','People review evidence, return cases with reasons and record decisions.','Role-based access · responsive interface'),
    node('core','FastAPI + authorization',['Sessions · CSRF · scoped access','Validated domain operations'],'design','2 · API and authorization','FastAPI provides the service boundary for authentication, scoped access and domain operations. Each request passes permission checks and validation before changing workflow state.','Server-side authorization protects every operational transition.','Session security · scope checks · request validation'),
    node('engine','Shared workflow engine',['Versioned rules · transitions','SLA · deadlines · escalation'],'design','3 · Workflow and deadline engine','A shared engine applies versioned rules to case transitions, SLA clocks and deadlines. Pause and resume preserve elapsed time, while milestone tracking prevents duplicate escalation events.','Rule versions and decision authority follow the applicable published policy.','Rule evaluation · time accounting · milestone tracking'),
    node('monitor','EVC + compliance APIs',['Visits · undertakings · documents','Officer verification gates'],'design','4 · Monitoring and verification','Domain services coordinate visit scheduling, evidence submissions, report review and compliance records. Explicit verification gates control changes to compliance and document validity.','Submission alone does not establish compliance; an authorized officer verifies the evidence.','Visit lifecycle · evidence review · renewal verification'),
    node('store','MongoDB + documents',['Domain records · audit history','Protected document storage'],'design','5 · Data, documents and audit','MongoDB holds domain records, workflow state and audit events. Protected document storage links evidence to cases through authorized upload and download operations and retention controls.','Decision history links each action to its actor, evidence and timestamp.','Domain persistence · document access · audit trail'),
    node('notify','Worker + escalation',['Scheduled scans · outbox jobs','Delivery results + retries'],'design','6 · Notifications and escalation','A scheduled worker evaluates deadlines and consumes durable notification jobs. Provider results, retries and escalation milestones feed back into operational records.','Escalation follows authority rules; a notification does not make an approval decision.','Deadline scans · durable outbox · retry handling'),
    node('ai','AI Assist endpoint',['Scoped summaries + draft support'],'design','8 · AI assistance','A scoped assistance endpoint uses authorized case facts to support summaries, blocker explanations and reminder drafts. Responses remain separate from authoritative workflow decisions.','People review drafts. AI has no authority to approve cases or supply missing evidence.','Scoped retrieval · grounded responses · human review'),
    node('bridge','Integration adapters',['AICTE systems + providers'],'design','7 · External integrations','Adapters define authorized exchanges with AICTE systems and notification providers through agreed contracts, identity mapping and delivery acknowledgements.','Each integration follows the permissions and data contract of the connected service.','API contracts · identity mapping · delivery receipts')
  ];
  // Edge labels sit in the open corridors, never on top of another label.
  const edge=(from,to,points,label,x,y,planned=false)=>({from,to,points,label,x,y,planned});
  const graphs={target:{nodes:target,caption:'Target architecture · secure workflows, accountable decisions and connected services',edges:[
    edge('ui','core','350,105 440,105','HTTPS',366,91,false),
    edge('core','engine','760,90 850,90','Actions',773,75,false),
    edge('engine','core','850,150 760,150','Results',774,174,false),
    edge('core','monitor','440,160 400,160 400,255 190,255 190,300','Verify / record',200,243,false),
    edge('core','store','600,185 600,300','Read / write',610,221,false),
    edge('engine','store','870,185 870,260 740,260 740,300','State + audit',748,245,false),
    edge('notify','engine','1010,300 1010,185','Scan',1026,244,false),
    edge('store','notify','760,375 850,375','Outbox',769,360,false),
    edge('notify','store','850,420 760,420','Results',769,443,false),
    edge('notify','bridge','1010,450 1010,520','Deliver',1025,492,false),
    edge('bridge','core','1170,575 1190,575 1190,15 600,15 600,35','Authorised exchange',892,10,false),
    edge('core','ai','440,175 415,175 415,575 350,575','Scoped request',425,495,false)
  ]}};
  const steps=['ui','core','engine','monitor','store','notify','bridge','ai'].map(id=>['target',id]);
  const statusText={design:'Target design'};
  const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
  const text=(x,y,s,size=20,fill='#52665b',weight=400,cls='')=>`<text x="${x}" y="${y}" font-size="${size}" fill="${fill}" font-weight="${weight}" class="${cls}">${escape(s)}</text>`;
  function contents(view,interactive=true){
    const g=graphs[view];let s='<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#56806a"/></marker></defs>';
    s+=g.edges.map(e=>`<g class="edge" data-from="${e.from}" data-to="${e.to}"><path d="M${e.points.split(' ').join(' L')}" fill="none" stroke="#6b8f7a" stroke-width="2" ${e.planned?'stroke-dasharray="7 5"':''} marker-end="url(#arrow)"/>${text(e.x,e.y,e.label,16,'#52665b',400,'edge-label')}</g>`).join('');
    s+=g.nodes.map(n=>{const[x,y,w,h]=positions[n.id],colors=n.status==='simulated'?['#fff9ed','#a17b31']:n.status==='planned'?['#fff','#81988a']:['#fff','#3e795d'];const dash=n.status==='planned'?'9 5':n.status==='simulated'?'2 4':'';return `<g class="node" data-id="${n.id}" ${interactive?`tabindex="0" role="button" aria-label="${escape(n.title)}: ${statusText[n.status]}" aria-pressed="false"`:''}><rect class="box" x="${x}" y="${y}" width="${w}" height="${h}" rx="13" fill="${colors[0]}" stroke="${colors[1]}" stroke-width="2" ${dash?`stroke-dasharray="${dash}"`:''}/>${text(x+20,y+29,'TARGET DESIGN',11,colors[1],700)}${text(x+20,y+62,n.title,23,'#173e30',700)}${n.lines.map((l,i)=>text(x+20,y+92+i*27,l,18)).join('')}</g>`;}).join('');
    s+=text(470,546,'Human verification',22,'#146347',700)+text(470,578,'Before compliance or validity changes',16)+text(470,609,'Authorized officer decision',16);
    return s;
  }
  function svg(view){return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -15 1200 665" aria-label="${'Target architecture'} diagram" style="font-family:Segoe UI,Arial,sans-serif">${contents(view)}</svg>`;}
  function staticSVG(view='target'){return `<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" style="font-family:Segoe UI,Arial,sans-serif"><rect width="1600" height="900" fill="#f5f7f3"/>${text(55,55,'ClockWork | Target architecture',36,'#173e30',700)}${text(55,88,graphs[view].caption,18)}<g transform="translate(140,120) scale(1.1)">${contents(view,false)}</g>${text(55,867,'Target system design · Human verification at decision gates',17)}</svg>`;}
  // Exposed only for reproducible static export and local validation.
  window.ClockWorkArchitecture={graphs,steps,staticSVG};
  let view='target',step=0,pinned=null,active='ui',zoom=1,pan={x:0,y:0},drag=null,frameScale=1,messageTimer;
  const $=id=>document.getElementById(id),frame=$('presentation'),viewport=$('diagram-viewport');
  function fit(){frameScale=Math.min(window.innerWidth/1600,window.innerHeight/900);frame.style.transform=`scale(${frameScale})`;frame.style.left=`${(window.innerWidth-1600*frameScale)/2}px`;frame.style.top=`${(window.innerHeight-900*frameScale)/2}px`;}
  function transform(){const w=viewport.clientWidth,h=viewport.clientHeight;pan.x=Math.max(w*(1-zoom),Math.min(0,pan.x));pan.y=Math.max(h*(1-zoom),Math.min(0,pan.y));$('diagram').style.transform=`translate(${pan.x}px,${pan.y}px) scale(${zoom})`;$('zoom-label').textContent=`${Math.round(zoom*100)}%`;viewport.classList.toggle('zoomed',zoom>1);$('zoom-in').disabled=zoom>=1.8;$('zoom-out').disabled=zoom<=1;}
  function show(id){const n=graphs[view].nodes.find(n=>n.id===id);if(!n)return;active=id;$('explanation-status').textContent=statusText[n.status];$('explanation-status').className=`status ${n.status}`;$('explanation-title').textContent=n.title;$('explanation-group').textContent=n.group;$('explanation-body').textContent=n.body;$('explanation-note').textContent=n.note;$('explanation-source').textContent=n.source;$('unpin').hidden=!pinned;$('interaction-hint').textContent=pinned?'Pinned · click again or press Esc to release':'Hover to explore · click to pin';
    document.querySelectorAll('.node').forEach(el=>{el.classList.toggle('active',el.dataset.id===id);el.classList.toggle('pinned',el.dataset.id===pinned);el.setAttribute('aria-pressed',String(el.dataset.id===pinned));});document.querySelectorAll('.edge').forEach(el=>el.classList.toggle('active',[el.dataset.from,el.dataset.to].includes(id)));
  }
  function pin(id){pinned=pinned===id?null:id;show(id);}
  function render(){ $('diagram').innerHTML=svg(view);$('view-caption').textContent=graphs[view].caption;document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));document.querySelectorAll('.node').forEach(el=>{el.addEventListener('pointerenter',()=>{if(!pinned&&!drag)show(el.dataset.id);});el.addEventListener('focus',()=>{if(!pinned)show(el.dataset.id);});el.addEventListener('click',()=>{if(!suppressClick)pin(el.dataset.id);});el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();pin(el.dataset.id);}});});transform();}
  function go(index){step=Math.max(0,Math.min(steps.length-1,index));const[v,id]=steps[step];pinned=null;if(v!==view){view=v;zoom=1;pan={x:0,y:0};render();}show(id);$('step-label').textContent=`Step ${step+1} of ${steps.length} · ${'Target architecture'}`;document.querySelectorAll('#steps button').forEach((b,i)=>{if(i===step)b.setAttribute('aria-current','step');else b.removeAttribute('aria-current');});$('previous').disabled=step===0;$('next').disabled=step===steps.length-1;}
  function changeZoom(delta){const old=zoom;zoom=Math.round(Math.max(1,Math.min(1.8,zoom+delta))*10)/10;pan.x=(pan.x-viewport.clientWidth/2)*zoom/old+viewport.clientWidth/2;pan.y=(pan.y-viewport.clientHeight/2)*zoom/old+viewport.clientHeight/2;transform();}
  function reset(){view='target';zoom=1;pan={x:0,y:0};pinned=null;render();go(0);}
  function message(s){$('message').textContent=s;$('message').style.display='block';clearTimeout(messageTimer);messageTimer=setTimeout(()=>$('message').style.display='none',5000);}
  $('steps').innerHTML=steps.map(([v,id],i)=>`<button aria-label="Step ${i+1}: ${'Target'} — ${escape(graphs[v].nodes.find(n=>n.id===id).title)}" title="${escape(graphs[v].nodes.find(n=>n.id===id).title)}">${i+1}</button>`).join('');
  document.querySelectorAll('#steps button').forEach((b,i)=>b.addEventListener('click',()=>go(i)));document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>go(0)));
  $('previous').onclick=()=>go(step-1);$('next').onclick=()=>go(step+1);$('reset').onclick=reset;$('zoom-in').onclick=()=>changeZoom(.2);$('zoom-out').onclick=()=>changeZoom(-.2);$('unpin').onclick=()=>{pinned=null;show(active);};
  $('fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch{message('Fullscreen was blocked by this browser. Press F11 for browser fullscreen.');}};
  document.addEventListener('fullscreenchange',()=>{$('fullscreen').textContent=document.fullscreenElement?'Exit fullscreen':'Fullscreen';fit();});
  document.addEventListener('keydown',e=>{if(e.altKey||e.ctrlKey||e.metaKey)return;if(['ArrowRight','ArrowDown'].includes(e.key)){e.preventDefault();go(step+1);}else if(['ArrowLeft','ArrowUp'].includes(e.key)){e.preventDefault();go(step-1);}else if(e.key==='Escape'){pinned=null;show(active);}else if(e.key==='+'||e.key==='='){e.preventDefault();changeZoom(.2);}else if(e.key==='-'){e.preventDefault();changeZoom(-.2);}else if(e.key.toLowerCase()==='r'){reset();}else if(e.key==='Home'){e.preventDefault();go(0);}else if(e.key==='End'){e.preventDefault();go(steps.length-1);}});
  let suppressClick=false;
  viewport.addEventListener('pointerdown',e=>{if(zoom<=1||e.button!==0)return;drag={x:e.clientX,y:e.clientY,px:pan.x,py:pan.y};suppressClick=false;viewport.classList.add('dragging');});
  window.addEventListener('pointermove',e=>{if(!drag)return;const dx=(e.clientX-drag.x)/frameScale,dy=(e.clientY-drag.y)/frameScale;if(Math.abs(dx)+Math.abs(dy)>5)suppressClick=true;pan={x:drag.px+dx,y:drag.py+dy};transform();});
  window.addEventListener('pointerup',()=>{drag=null;viewport.classList.remove('dragging');setTimeout(()=>{suppressClick=false;},0);});
  window.addEventListener('resize',fit);fit();render();go(0);
})();
