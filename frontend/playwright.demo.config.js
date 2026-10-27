import process from 'node:process';
import {defineConfig} from '@playwright/test';
import base from './playwright.config.js';
export default defineConfig({...base,testMatch:'demo.spec.js',timeout:90000,globalTimeout:300000,use:{...base.use,baseURL:'http://127.0.0.1:5175',viewport:{width:390,height:844},deviceScaleFactor:1,video:'off',trace:'off',screenshot:'off',isMobile:true,hasTouch:true},webServer:process.env.CLOCKWORK_EXTERNAL_SERVER==='1'?undefined:{...base.webServer,command:'node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5175',url:'http://127.0.0.1:5175',env:{VITE_APP_MODE:'demo'}}});
