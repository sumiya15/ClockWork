import {defineConfig} from '@playwright/test';
import base from './playwright.demo.config.js';
export default defineConfig({...base,testMatch:'final-presentation.spec.js',timeout:180000,globalTimeout:300000,outputDir:'../docs/presentation/evidence/green-test-results',webServer:undefined,use:{...base.use,baseURL:'http://127.0.0.1:5176',video:'off',trace:'off',screenshot:'off'}});
