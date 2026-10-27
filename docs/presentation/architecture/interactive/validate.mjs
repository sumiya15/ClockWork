import {chromium} from '../../../../frontend/node_modules/@playwright/test/index.mjs';
import {readFile,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
const here=new URL('./',import.meta.url),out=new URL('../',here);
const browser=await chromium.launch({channel:'msedge',headless:true});
const checks=[],errors=[],external=[];
try{
 const context=await browser.newContext({viewport:{width:1600,height:900},offline:true,reducedMotion:'reduce'});
 const p=await context.newPage();p.on('pageerror',e=>errors.push(e.message));p.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
 await p.goto(new URL('index.html',here).href);await p.locator('.node').first().waitFor();
 assert.equal(await p.locator('.node').count(),8);checks.push('file:// opening with offline browser context; eight current nodes');
 await p.locator('[data-id="engine"]').hover();assert.equal(await p.locator('#explanation-title').innerText(),'Workflow + deadlines');assert.equal(await p.locator('.edge.active').count(),3);checks.push('hover highlights node and all three connected arrows');
 await p.locator('[data-id="engine"]').click();await p.locator('[data-id="ai"]').hover();assert.equal(await p.locator('#explanation-title').innerText(),'Workflow + deadlines');assert.equal(await p.locator('#unpin').isVisible(),true);
 await p.locator('#unpin').click();await p.locator('[data-id="ai"]').hover();assert.equal(await p.locator('#explanation-title').innerText(),'AI Assist');checks.push('click pins; other hover preserves pin; Unpin releases');
 await p.locator('#reset').click();await p.keyboard.press('ArrowRight');assert.match(await p.locator('#step-label').innerText(),/Step 2/);await p.locator('#previous').click();assert.match(await p.locator('#step-label').innerText(),/Step 1/);await p.locator('#next').click();assert.match(await p.locator('#step-label').innerText(),/Step 2/);
 for(let i=0;i<14;i++){
  await p.locator('#steps button').nth(i).click();assert.match(await p.locator('#step-label').innerText(),new RegExp(`Step ${i+1} of`));
  const fit=await p.locator('#explanation').evaluate(e=>({scroll:e.scrollHeight,height:e.clientHeight,children:[...e.children].filter(c=>!c.hidden).map(c=>({text:c.textContent,r:c.getBoundingClientRect().bottom,b:e.getBoundingClientRect().bottom}))}));
  assert.ok(fit.scroll<=fit.height+1,`Panel overflow at step ${i+1}: ${JSON.stringify(fit)}`);
 }
 checks.push('all 14 numbered steps; Next/Previous and arrow keys; explanation panel fit');
 for(const view of ['current','target']){
  await p.locator(`[data-view="${view}"]`).click();
  for(const id of ['ui','core','engine','monitor','store','notify','ai','bridge']){
   await p.locator(`[data-id="${id}"]`).click();assert.ok(await p.locator('#explanation').evaluate(e=>e.scrollHeight<=e.clientHeight+1),`${view}/${id} explanation overflow`);
  }
 }
 checks.push('all 16 component explanations fit, including components outside the guided sequence');
 await p.keyboard.press('Home');await p.keyboard.press('End');assert.match(await p.locator('#step-label').innerText(),/Step 14/);await p.keyboard.press('r');assert.match(await p.locator('#step-label').innerText(),/Step 1/);
 await p.locator('[data-id="monitor"]').focus();await p.keyboard.press('Enter');assert.equal(await p.locator('[data-id="monitor"]').getAttribute('aria-pressed'),'true');await p.keyboard.press('Escape');assert.equal(await p.locator('#unpin').isVisible(),false);checks.push('focus + Enter pins; Escape unpins; Home/End/R keys');
 await p.locator('#zoom-in').click();assert.equal(await p.locator('#zoom-label').innerText(),'120%');const before=await p.locator('#diagram').getAttribute('style');await p.mouse.move(700,500);await p.mouse.down();await p.mouse.move(600,450,{steps:5});await p.mouse.up();assert.notEqual(await p.locator('#diagram').getAttribute('style'),before);await p.locator('#zoom-out').click();assert.equal(await p.locator('#zoom-label').innerText(),'100%');checks.push('zoom controls and drag panning');
 await p.locator('#fullscreen').click();assert.equal(await p.evaluate(()=>!!document.fullscreenElement),true);await p.locator('#fullscreen').click();assert.equal(await p.evaluate(()=>!!document.fullscreenElement),false);checks.push('actual Fullscreen API enter and exit from local file');
 const layouts=[];
 for(const size of [{width:1600,height:900},{width:1920,height:1080},{width:1366,height:768}]){
  await p.setViewportSize(size);await p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  const bounds=await p.evaluate(()=>({width:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight,vw:innerWidth,vh:innerHeight}));
  assert.ok(bounds.width<=bounds.vw&&bounds.height<=bounds.vh,JSON.stringify(bounds));
  layouts.push({...size,noScroll:true});
 }
 await p.setViewportSize({width:1600,height:900});await p.locator('#reset').click();await p.mouse.move(1590,890);
 await p.screenshot({path:fileURLToPath(new URL('interactive-current.png',here))});
 await p.locator('[data-view="target"]').click();await p.mouse.move(1590,890);await p.screenshot({path:fileURLToPath(new URL('interactive-target.png',here))});
 checks.push('both view buttons, reset and no horizontal/vertical scroll at three desktop sizes');
 assert.equal(await p.evaluate(()=>matchMedia('(prefers-reduced-motion: reduce)').matches),true);assert.equal(await p.locator('.node .box').first().evaluate(e=>getComputedStyle(e).transitionDuration),'0s');checks.push('reduced motion disables transitions');
 const exported=[];
 for(const view of ['current','target']){
  const svg=await p.evaluate(v=>window.ClockWorkArchitecture.staticSVG(v),view);const stem=`walkthrough-${view}`;
  await writeFile(new URL(stem+'.svg',out),svg,'utf8');
  const exportPage=await context.newPage();await exportPage.setViewportSize({width:1600,height:900});await exportPage.setContent('<style>body{margin:0}</style>'+svg);await exportPage.evaluate(()=>document.fonts.ready);
  const overflow=await exportPage.locator('.node').evaluateAll(nodes=>nodes.flatMap(n=>{const r=n.querySelector('rect').getBBox();return [...n.querySelectorAll('text')].filter(t=>{const b=t.getBBox();return b.x<r.x||b.x+b.width>r.x+r.width-8||b.y+b.height>r.y+r.height;}).map(t=>t.textContent);}));assert.deepEqual(overflow,[],'Node text fit');
  const crossed=await exportPage.evaluate(()=>{const paths=[...document.querySelectorAll('.edge>path')];return [...document.querySelectorAll('.edge-label')].filter(t=>{const b=t.getBBox();return paths.some(p=>{const pts=p.getAttribute('d').match(/-?\d+,\d+/g).map(v=>v.split(',').map(Number));return pts.slice(1).some(([x2,y2],i)=>{const[x1,y1]=pts[i];return x1===x2?x1>b.x&&x1<b.x+b.width&&Math.max(y1,y2)>b.y&&Math.min(y1,y2)<b.y+b.height:y1>b.y&&y1<b.y+b.height&&Math.max(x1,x2)>b.x&&Math.min(x1,x2)<b.x+b.width;});});}).map(t=>t.textContent);});assert.deepEqual(crossed,[],'No arrow crosses an edge label');
  await exportPage.close();
  const hi=await browser.newContext({viewport:{width:1600,height:900},deviceScaleFactor:2,offline:true});const ep=await hi.newPage();await ep.setContent('<style>body{margin:0}</style>'+svg);await ep.evaluate(()=>document.fonts.ready);await ep.screenshot({path:fileURLToPath(new URL(stem+'.png',out))});await hi.close();exported.push({name:stem,width:3200,height:1800,nodeTextOverflow:overflow});
 }
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 const source=await readFile(new URL('presentation.js',here),'utf8');assert.equal(/fetch\(|XMLHttpRequest|localStorage|sessionStorage/.test(source.replace(/'Local persistence'[\s\S]*?'notify'/,'')),false,'Viewer should not access application persistence');
 await writeFile(new URL('VALIDATION.json',here),JSON.stringify({date:'2026-10-26',browser:'Installed Microsoft Edge through Playwright',offline:true,checks,layouts,exported,pageErrors:errors,externalRequests:external,video:'Never enabled or recorded'},null,2));
 console.log(JSON.stringify({checks,layouts,exported,errors,external},null,2));
}finally{await browser.close();}
