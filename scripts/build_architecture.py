"""Generate editable architecture SVGs and matching Mermaid sources; no bitmap synthesis."""
from pathlib import Path
from html import escape
import re
OUT=Path('docs/presentation/architecture');OUT.mkdir(parents=True,exist_ok=True)
def text(x,y,lines,size=24,color='#24332c',weight=400):
 return ''.join(f'<text x="{x}" y="{y+i*34}" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(line)}</text>' for i,line in enumerate(lines))
def box(x,y,w,h,title,lines=(),dashed=False,fill='#ffffff'):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{fill}" stroke="#5b8770" stroke-width="2" {"stroke-dasharray=\"10 7\"" if dashed else ""}/>'+text(x+24,y+42,[title],26,'#146347',650)+text(x+24,y+86,lines,23)
def arrow(points,label,x,y,dashed=False):
 return f'<polyline points="{points}" fill="none" stroke="#356b50" stroke-width="3" marker-end="url(#arrow)" {"stroke-dasharray=\"9 6\"" if dashed else ""}/>'+text(x,y,[label],21,'#56645c')
def start(title,subtitle):
 return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080" role="img"><title>{escape(title)}</title><desc>{escape(subtitle)}</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#356b50"/></marker></defs><rect width="1920" height="1080" fill="#f7f8f5"/><g font-family="Segoe UI,Arial,sans-serif">'''+text(70,88,[title],50,'#163f2d',700)+text(72,135,[subtitle],25,'#56645c')
def finish(s):return s+'</g></svg>'
s=start('ClockWork | Current prototype','Working browser interactions with fictional records; no operational backend calls from this interface')
s+=box(65,230,360,245,'React mobile interface',['Today · dashboards · registers','Case actions · six CSV reports','Personas simulate role scope','Human: return, visit, verify'],fill='#e8f3ec')
s+=box(525,230,360,245,'Shared local state',['DemoApp: data + current ref','act(operation) passes state','Case, evidence and rule records','Results trigger React rendering'])
s+=box(985,230,400,245,'Workflow & deadlines',['service.js + model.js','Routes · SLA pause/resume','targets → evaluate → milestones','Officer verification gates'])
s+=box(1485,230,370,245,'Local persistence',['saveDemo / loadDemo','localStorage: full state','sessionStorage: view choices','File metadata only'])
s+=arrow('425,340 525,340','Actions',440,321)+arrow('885,340 985,340','Calculate',895,321)+arrow('1385,340 1485,340','Save',1408,321)
s+=arrow('1185,475 1185,550 705,550 705,475','Return next state; update React',765,533)
s+=arrow('1670,475 1670,600 705,600 705,475','Reload restores state',1410,628)
s+=box(65,710,510,205,'AI Assist · simulated preview',['assistant.js reads scoped case facts','Deterministic templates; no model','Drafts require human review'],fill='#e8f3ec')
s+=box(690,710,520,205,'Notifications · simulated',['Same evaluator records rule and threshold','Manual scan / +1, +7, +30 workspace days','Channel records only; no delivery'],fill='#e8f3ec')
s+=box(1325,710,530,205,'Separate API foundation',['FastAPI / MongoDB exist separately','Auth · scoped reads · audit/outbox helpers','Not connected to these workflow actions'],dashed=True)
s+=arrow('525,405 470,405 470,670 320,670 320,710','Scoped snapshot',80,650)
s+=arrow('1280,475 1280,670 950,670 950,710','Alert records',990,696)
s+=text(72,988,['Solid: implemented local behavior  ·  Dashed: separate or incomplete operational connection'],23,'#56645c')
s+=text(72,1032,['Human actions remain explicit. No statutory approval, secure evidence storage or AICTE integration is implied.'],24,'#146347')
(OUT/'current-prototype.svg').write_text(finish(s),encoding='utf-8')
s=start('ClockWork | Target system architecture','Solid borders identify existing backend foundations; dashed components or links require operational implementation')
s+=box(60,230,270,370,'Users',['Institution','Regional officer','Bureau officer','Committee','Admin'],fill='#e8f3ec')
s+=box(395,285,275,240,'React interface',['Mobile workflows','Scoped dashboards','Evidence & reports','Human review actions'],fill='#e8f3ec')
# Group FastAPI; implemented auth and incomplete domain layer are visually separate.
s+='<rect x="740" y="195" width="430" height="480" rx="20" fill="#eef4ef" stroke="#9eb7a6" stroke-width="2"/>'
s+=text(766,235,['FastAPI'],31,'#146347',700)
s+=box(765,258,380,145,'Auth & scoped reads',['Cookie sessions · CSRF · scope','Institution / obligation / rules'])
s+=box(765,430,380,218,'Operational services',['Applications · EVC','Undertakings · Documents','Reports · decisions / closure','Human verification gates'],dashed=True)
s+=box(1240,195,620,235,'Shared engine',['Published rules · state transitions','SLA pause/resume · deadline evaluation','Escalation and versioned obligations','Partial foundation: rule/date helpers exist'],dashed=True)
s+=box(1240,510,290,205,'Worker',['Scheduled scans','Outbox consumption','Delivery / retries'],dashed=True)
s+=box(1590,510,270,205,'Adapters',['Authorised AICTE','systems','Notification providers'],dashed=True)
s+=box(60,800,610,170,'Future AI endpoint',['Scoped retrieval through backend','Human review; no autonomous decisions'],dashed=True)
s+=box(740,800,520,170,'MongoDB & audit foundation',['Collections · sessions · audit / outbox','Complete domain persistence still required'])
s+=box(1350,800,510,170,'Protected document storage',['Authorised upload / download','Evidence bytes, retention and access logs'],dashed=True)
s+=arrow('330,405 395,405','Use',345,385)
s+=arrow('670,330 740,330','HTTPS',673,307,True)
s+=arrow('955,403 955,430','',960,421,True)
s+=arrow('1170,310 1240,310','Rules',1177,290,True)
s+=arrow('1385,510 1385,430','Run scan',1400,480,True)
s+=arrow('1530,610 1590,610','Send',1532,590,True)
s+=arrow('1720,510 1720,465 1170,465','Data exchange',1630,493,True)
s+=arrow('1000,675 1000,800','Read / write + audit',780,778,True)
s+=arrow('1385,715 1385,755 1175,755 1175,800','Outbox / results',1180,735,True)
s+=arrow('1145,580 1200,580 1200,780 1585,780 1585,800','Verified evidence reference',1450,762,True)
s+=arrow('800,675 800,735 365,735 365,800','Scoped request via FastAPI',390,718,True)
s+=text(70,1025,['Solid: existing component/foundation  ·  Dashed: proposed or incomplete  ·  Arrows: requests, records or jobs'],23,'#56645c')
(OUT/'target-system.svg').write_text(finish(s),encoding='utf-8')
current='''flowchart LR
 subgraph Browser[Current browser prototype]
 UI[React mobile interface\nHuman return, visit and verification actions]
 State[Shared state\nDemoApp data and current ref]
 Engine[service.js and model.js\nRoutes, SLA, deadlines, verification]
 Store[localStorage full state\nsessionStorage view choices]
 AI[AI Assist\nDeterministic simulated preview]
 Alerts[Simulated notification records\nManual scan and isolated clock]
 UI -->|Actions| State
 State -->|Calculate| Engine
 Engine -->|Save through act| Store
 Engine -->|Return next state / React render| State
 Store -->|Reload| State
 State -->|Scoped snapshot| AI
 Engine -->|Alert records| Alerts
 end
 Foundation[Separate FastAPI / MongoDB foundation\nNot connected to demo workflows]
 classDef current fill:#e8f3ec,stroke:#146347,color:#24332c;
 classDef incomplete fill:#fff,stroke:#5b8770,color:#24332c,stroke-dasharray:8 5;
 class UI,State,Engine,Store,AI,Alerts current;
 class Foundation incomplete;
'''
target='''flowchart LR
 Users[Institution / Regional officer / Bureau officer / Committee / Admin]
 UI[React mobile interface\nHuman review actions]
 subgraph API[FastAPI]
 Auth[Existing auth and scoped reads\nCookie sessions, CSRF, scope]
 Ops[Incomplete operational services\nApplications, EVC, undertakings, documents, reports\nHuman verification and final decisions]
 Auth -.->|Authorised operations| Ops
 end
 Engine[Shared engine — incomplete\nPublished rules, transitions, SLA pause/resume\nDeadline evaluation and escalation]
 Worker[Proposed worker\nScheduled scans, outbox delivery, retries]
 Mongo[Existing MongoDB / audit / outbox foundation\nDomain persistence incomplete]
 Files[Proposed protected document storage]
 Adapters[Proposed adapters\nAuthorised AICTE systems / notification providers]
 AI[Future backend AI endpoint\nScoped facts and human review]
 Users -->|Use| UI
 UI -.->|HTTPS| Auth
 Ops -.->|Rules and transitions| Engine
 Worker -.->|Run deadline evaluation| Engine
 Worker -.->|Send| Adapters
 Adapters -.->|Authorised data exchange| Ops
 Ops -.->|Read / write and audit| Mongo
 Worker -.->|Outbox / results| Mongo
 Ops -.->|Verified evidence reference| Files
 Ops -.->|Scoped request| AI
 classDef current fill:#e8f3ec,stroke:#146347,color:#24332c;
 classDef proposed fill:#fff,stroke:#5b8770,color:#24332c,stroke-dasharray:8 5;
 class Users,UI,Auth,Mongo current;
 class Ops,Engine,Worker,Files,Adapters,AI proposed;
'''
def mermaid_labels(s):return re.sub(r'([A-Za-z][\w]*)\[([^\]]+)\]',lambda m:m[1]+'["'+m[2].replace('\n','<br/>')+'"]',s)
(OUT/'current-prototype.mmd').write_text(mermaid_labels(current),encoding='utf-8');(OUT/'target-system.mmd').write_text(mermaid_labels(target),encoding='utf-8')
print('Created two editable SVG diagrams and matching Mermaid sources.')
