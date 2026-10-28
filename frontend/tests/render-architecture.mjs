import {chromium} from '@playwright/test';
import {readFile,writeFile} from 'node:fs/promises';
const browser=await chromium.launch({channel:'msedge',headless:true});
try{
 const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:2});
 const results=[];
 for(const name of ['current-prototype','target-system']){
  const svg=await readFile(`../docs/presentation/architecture/${name}.svg`,'utf8');
  await page.setContent('<style>body{margin:0}</style>'+svg);await page.evaluate(()=>document.fonts.ready);
  const outside=await page.locator('svg text').evaluateAll(nodes=>nodes.filter(e=>{const r=e.getBBox();return r.x<0||r.y<0||r.x+r.width>1920||r.y+r.height>1080;}).map(e=>e.textContent));
  if(outside.length)throw new Error('Text outside canvas: '+outside.join(', '));
  await page.screenshot({path:`../docs/presentation/architecture/${name}.png`});results.push({name,width:3840,height:2160,textOutsideCanvas:outside});
 }
 await writeFile('../docs/presentation/evidence/architecture-render.json',JSON.stringify(results,null,2));
}finally{await browser.close();}
