import {chromium} from '@playwright/test';
const browser=await chromium.launch({channel:'msedge',headless:true});
try{const page=await browser.newPage({viewport:{width:390,height:844}});await page.goto('http://127.0.0.1:5176');console.log(await page.locator('.app-brand strong').evaluate(e=>{let a=e;const rows=[];while(a){rows.push([a.tagName,a.className,getComputedStyle(a).color]);a=a.parentElement;}return rows;}));}finally{await browser.close();}
