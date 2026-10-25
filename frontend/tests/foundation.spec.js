import { test, expect } from '@playwright/test';

test('institution login, real scoped obligations, cookie restoration and logout', async ({ page }) => {
  await page.goto('/');
  await page.getByLabel('Username').fill('institution_1.demo');
  await page.getByLabel('Password').fill('ClockWork-Demo-Only-2026!');
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Today', exact: true })).toBeVisible();
  await expect(page.getByText('1 visible obligations', { exact: false })).toBeVisible();
  await expect(page.getByText('DEMO-REGION-A', { exact: false })).toBeVisible();
  await expect(page.getByText('DEMO-REGION-B', { exact: false })).toHaveCount(0);
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Today', exact: true })).toBeVisible();
  await page.getByRole('button', { name: /scrutiny/i }).click();
  await expect(page.getByText('DEMO-CLOCKWORK · version 1')).toBeVisible();
  await page.screenshot({ path: 'test-results/today.png', fullPage: true });
  expect(await page.evaluate(() => window.localStorage.length)).toBe(0);
  expect(await page.evaluate(() => document.cookie)).not.toContain('clockwork_v1_session');
  await page.getByRole('button', { name: 'Sign out' }).click();
  await expect(page.getByRole('heading', { name: 'Sign in to ClockWork' })).toBeVisible();
  const response = await page.request.get('/api/v1/obligations');
  expect(response.status()).toBe(401);
});

test('admin sees published rules and receives no operational scope', async ({ page }) => {
  await page.goto('/');
  await page.getByLabel('Username').fill('admin.demo');
  await page.getByLabel('Password').fill('ClockWork-Demo-Only-2026!');
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Published rules' })).toBeVisible();
  await expect(page.getByText('SCRUTINY_EVC', { exact: true })).toBeVisible();
  expect((await page.request.get('/api/v1/obligations')).status()).toBe(403);
});
