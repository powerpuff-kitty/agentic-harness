import { test, expect } from '@playwright/test';

test('approved unread count follows the full session, independent of the filter', async ({ page }) => {
  await page.goto('/');
  const count = page.getByRole('status', { name: 'Unread count', exact: true });
  await expect(count).toHaveText('Unread in this session: 0');
  for (const title of ['One', 'Two']) {
    await page.getByLabel('Title', { exact: true }).fill(title);
    await page.getByRole('button', { name: 'Add entry' }).click();
  }
  await expect(count).toHaveText('Unread in this session: 2');
  await page.getByRole('button', { name: 'Read: One', exact: true }).click();
  await expect(count).toHaveText('Unread in this session: 1');
  await page.getByLabel('Show entries').selectOption('unread');
  await expect(count).toHaveText('Unread in this session: 1');
  await expect(page.getByRole('listitem')).toHaveCount(1);
  await page.getByLabel('Show entries').selectOption('all');
  await page.getByRole('button', { name: 'Read: One', exact: true }).click();
  await expect(count).toHaveText('Unread in this session: 2');
  await page.getByRole('button', { name: 'Add entry' }).click();
  await expect(count).toHaveText('Unread in this session: 2');
  await page.reload();
  await expect(count).toHaveText('Unread in this session: 0');
});
