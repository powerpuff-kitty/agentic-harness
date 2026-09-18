import { defineConfig } from '@playwright/test';

const port = Number(process.env.READING_LIST_PORT ?? '43186');
if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('Invalid READING_LIST_PORT');
const baseURL = `http://127.0.0.1:${port}`;

export default defineConfig({
  testDir: './tests/browser',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: 'list',
  use: { baseURL, trace: 'retain-on-failure' },
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }],
  webServer: { command: `npm run preview -- --port ${port}`, url: baseURL, reuseExistingServer: false },
});
