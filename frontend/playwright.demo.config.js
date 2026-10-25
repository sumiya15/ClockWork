import {defineConfig} from '@playwright/test';
import base from './playwright.config.js';
export default defineConfig({...base,testMatch:'demo.spec.js',timeout:90000,globalTimeout:300000,use:{...base.use,baseURL:'http://127.0.0.1:5175',viewport:{width:390,height:844},deviceScaleFactor:1,isMobile:true,hasTouch:true},webServer:{...base.webServer,command:'npm run dev -- --port 5175',url:'http://127.0.0.1:5175',env:{VITE_APP_MODE:'demo'}}});
