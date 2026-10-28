import {defineConfig} from '@playwright/test';
import base from './playwright.demo.config.js';
export default defineConfig({...base,testMatch:'presentation.spec.js',timeout:260000,globalTimeout:300000,outputDir:'../docs/presentation/video/raw',webServer:undefined,use:{...base.use,baseURL:'http://127.0.0.1:5176',video:{mode:'on',size:{width:390,height:844}}}});
