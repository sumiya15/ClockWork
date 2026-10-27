import {chromium} from '@playwright/test';
import {readFile,writeFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import {resolve} from 'node:path';
const root=resolve('..'),source=resolve(root,'docs/presentation/video/clockwork-26262-source.webm'),output=resolve(root,'docs/presentation/video/clockwork-26262-silent.webm');
const browser=await chromium.launch({channel:'msedge',headless:true});
let start=0,duration=0;
try{
 const page=await browser.newPage();await page.setContent('<video muted></video><canvas width="390" height="844"></canvas>');
 const bytes=await readFile(source);
 duration=await page.locator('video').evaluate((v,src)=>new Promise((resolve,reject)=>{v.onloadedmetadata=()=>resolve(v.duration);v.onerror=()=>reject(new Error('Source video not decodable'));v.src=src;}),'data:video/webm;base64,'+bytes.toString('base64'));
 let found=false;
 for(let t=0.04;t<10;t+=0.12){
  const loaded=await page.locator('video').evaluate((v,t)=>new Promise(resolve=>{v.onseeked=()=>{const ctx=document.querySelector('canvas').getContext('2d');ctx.drawImage(v,0,0);const rgba=ctx.getImageData(30,30,1,1).data;resolve(rgba[0]<100&&rgba[1]<120&&rgba[2]<160);};v.currentTime=t;}),t);
  if(loaded){start=Number(t.toFixed(2));found=true;break;}
 }
 if(!found)throw new Error('Could not identify the first rendered Today frame');
 if(duration-start<180)throw new Error('Source does not contain 180 seconds after the first rendered frame');
}finally{await browser.close();}
const ffmpeg=resolve(root,'.local/presentation-browsers/ffmpeg-1013/ffmpeg-win64.exe');
const run=spawnSync(ffmpeg,['-hide_banner','-y','-ss',String(start),'-i',source,'-t','180','-c:v','libvpx-vp9','-deadline','realtime','-cpu-used','8','-b:v','1200k',output],{encoding:'utf8',windowsHide:true});
if(run.status!==0)throw new Error(run.stderr);
const record={sourceDuration:duration,startTrimSeconds:start,requestedDuration:180,method:'Decode source video to locate first rendered Today frame; trim blank startup and closing tail, re-encode actual interaction as VP9. No slides or reconstructed states.',audio:'Silent; no microphone audio captured'};
await writeFile(resolve(root,'docs/presentation/evidence/video-processing.json'),JSON.stringify(record,null,2));console.log(JSON.stringify(record,null,2));
