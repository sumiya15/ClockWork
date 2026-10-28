import {defineConfig} from '@playwright/test';
import base from './playwright.presentation.config.js';
export default defineConfig({...base,testMatch:'presentation-assets.spec.js',timeout:180000,globalTimeout:240000,outputDir:'../docs/presentation/evidence/qa',use:{...base.use,video:'off'}});
