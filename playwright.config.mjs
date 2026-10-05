import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  workers: 1,
  fullyParallel: false,
  retries: 0, // Retrying mutations would create extra projects/schedules.
  timeout: 120_000,
  expect: { timeout: 15_000 },
  outputDir: 'artifacts/playwright',
  reporter: [['list'], ['json', { outputFile: 'artifacts/playwright-results.json' }]],
  use: { baseURL: 'https://rhombusai.com', trace: 'retain-on-failure', screenshot: 'only-on-failure' },
  projects: [
    { name: 'public-smoke', testMatch: 'ui-tests/public-smoke.spec.mjs' },
    { name: 'ui', testMatch: 'ui-tests/pipeline.spec.mjs' },
    { name: 'api', testMatch: 'api-tests/*.spec.mjs' },
  ],
});
