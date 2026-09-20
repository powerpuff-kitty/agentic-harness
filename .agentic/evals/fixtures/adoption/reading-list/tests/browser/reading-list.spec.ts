import { test, expect, type Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

async function add(page: Page, title: string) {
  await page.getByLabel('Title', { exact: true }).fill(title);
  await page.getByRole('button', { name: 'Add entry' }).click();
}

test('keyboard add, duplicate titles, read filtering and focus recovery', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('No entries yet.', { exact: false })).toBeVisible();
  await page.keyboard.press('Tab');
  await expect(page.getByLabel('Title', { exact: true })).toBeFocused();
  await page.keyboard.type('One');
  await page.keyboard.press('Enter');
  await expect(page.getByLabel('Title', { exact: true })).toBeFocused();
  await add(page, 'Two');
  await add(page, 'Two');
  await expect(page.getByRole('listitem')).toHaveCount(3);
  await page.getByLabel('Show entries').selectOption('unread');
  await page.getByRole('button', { name: 'Read: One', exact: true }).focus();
  await page.keyboard.press('Space');
  await expect(page.getByRole('button', { name: 'Read: Two' }).first()).toBeFocused();
  await page.keyboard.press('Space');
  await expect(page.getByRole('button', { name: 'Read: Two' })).toBeFocused();
  await page.keyboard.press('Space');
  await expect(page.getByLabel('Show entries')).toBeFocused();
  await expect(page.getByText('Nothing unread.', { exact: false })).toBeVisible();
  await add(page, 'New unread');
  await expect(page.getByRole('listitem')).toHaveCount(1);
  await page.getByLabel('Show entries').selectOption('all');
  await expect(page.getByRole('listitem')).toHaveCount(4);
  await expect(page.getByRole('button', { name: 'Read: One', exact: true })).toHaveAttribute('aria-pressed', 'true');
});

test('invalid input remains editable and errors are associated', async ({ page }) => {
  await page.goto('/');
  await page.getByLabel('Title', { exact: true }).fill('Kept title');
  await page.getByLabel('Link (optional)').fill('javascript:alert(1)');
  await page.getByRole('button', { name: 'Add entry' }).click();
  await expect(page.getByLabel('Title', { exact: true })).toHaveValue('Kept title');
  await expect(page.getByLabel('Link (optional)')).toHaveValue('javascript:alert(1)');
  await expect(page.getByLabel('Link (optional)')).toBeFocused();
  await expect(page.getByLabel('Link (optional)')).toHaveAttribute('aria-describedby', 'url-error');
  await expect(page.getByRole('listitem')).toHaveCount(0);
  await page.getByLabel('Link (optional)').fill('');
  await page.getByLabel('Title', { exact: true }).fill('x'.repeat(121));
  await page.getByRole('button', { name: 'Add entry' }).click();
  await expect(page.getByLabel('Title', { exact: true })).toBeFocused();
  await expect(page.getByLabel('Title', { exact: true })).toHaveAttribute('aria-invalid', 'true');
});

test('escaped text, isolated links, no app persistence or remote requests', async ({ page, context, browser, baseURL }) => {
  const outbound: string[] = [];
  page.on('request', request => {
    if (new URL(request.url()).origin !== new URL(baseURL!).origin) outbound.push(request.url());
  });
  await page.goto('/');
  const title = '<img src=x onerror=alert(1)>';
  await page.getByLabel('Link (optional)').fill('https://example.test/reading');
  await add(page, title);
  const link = page.getByRole('link', { name: title });
  await expect(link).toHaveAttribute('href', 'https://example.test/reading');
  await expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  await expect(link).toHaveAttribute('target', '_blank');
  await expect(page.locator('img')).toHaveCount(0);
  expect(await page.evaluate(async () => ({
    local: localStorage.length, session: sessionStorage.length,
    databases: (await indexedDB.databases()).length,
    caches: (await caches.keys()).length,
    workers: (await navigator.serviceWorker.getRegistrations()).length,
  }))).toEqual({ local: 0, session: 0, databases: 0, caches: 0, workers: 0 });
  expect(await context.cookies()).toEqual([]);
  await page.reload();
  await expect(page.getByRole('listitem')).toHaveCount(0);
  expect(outbound).toEqual([]);
  console.log(`Verified browser: Chromium ${browser.version()}`);
});

test('320px reflow and automated accessibility across empty, invalid and populated states', async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 740 });
  await page.goto('/');
  for (const state of ['empty', 'invalid', 'populated']) {
    if (state === 'invalid') await page.getByRole('button', { name: 'Add entry' }).click();
    if (state === 'populated') await add(page, 'A'.repeat(120));
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), state).toBe(true);
    const result = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
    expect(result.violations, state).toEqual([]);
  }
});
