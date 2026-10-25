import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: 'foundation.spec.js',
  workers: 1,
  timeout: 15000,
  globalTimeout: 60000,
  reporter: 'list',
  use: { baseURL: 'http://127.0.0.1:5173', channel: 'msedge', headless: true },
  webServer: {
    command: 'npm run dev',
    env: { VITE_APP_MODE: 'api' },
    url: 'http://127.0.0.1:5173',
    reuseExistingServer: false,
  },
});
