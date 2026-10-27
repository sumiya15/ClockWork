import {test,expect} from '@playwright/test';
import {readFile,writeFile} from 'node:fs/promises';
test('EVC new institution queue and recorded video metadata',async({page})=>{
 await page.goto('/#registers');await page.getByLabel('EVC institution type').selectOption('New institution');
 await expect(page.locator('.register-grid article').first()).toContainText('New institution');await expect(page.locator('.register-grid article').first()).toContainText('Scheduled');
 await page.screenshot({path:'../docs/presentation/screenshots/04b-evc-new-institutions.png'});
 const bytes=await readFile('../docs/presentation/video/clockwork-26262-silent.webm');
 await page.setContent('<html><body style="margin:0;background:white"><video style="width:390px;height:844px" muted></video></body></html>');
 const metadata=await page.locator('video').evaluate((v,src)=>new Promise((resolve,reject)=>{v.onloadedmetadata=()=>resolve({duration:v.duration,width:v.videoWidth,height:v.videoHeight});v.onerror=()=>reject(new Error('Video decode failed'));v.src=src;}),'data:video/webm;base64,'+bytes.toString('base64'));
 expect(metadata.width).toBe(390);expect(metadata.height).toBe(844);expect(metadata.duration).toBeGreaterThanOrEqual(179.9);expect(metadata.duration).toBeLessThanOrEqual(180.3);
 for(const seconds of [1,21,40,60,80,100,120,140,160,175,179]){
  await page.locator('video').evaluate((v,t)=>new Promise(resolve=>{v.onseeked=resolve;v.currentTime=t;}),seconds);
  await page.locator('video').screenshot({path:`../docs/presentation/evidence/video-final-${seconds}.png`});
 }
 await writeFile('../docs/presentation/evidence/video-metadata.json',JSON.stringify({...metadata,bytes:bytes.length,audio:'No audio track; silent browser capture',sampledSeconds:[1,21,40,60,80,100,120,140,160,175,179]},null,2));
});
