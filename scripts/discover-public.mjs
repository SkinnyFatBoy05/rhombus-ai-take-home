import { chromium } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
await mkdir('artifacts', { recursive: true });
const browser = await chromium.launch();
try {
  const page = await browser.newPage();
  const requests = [];
  const pending = [];
  page.on('response', response => {
    if (!['xhr', 'fetch'].includes(response.request().resourceType())) return;
    pending.push((async () => {
      const url = new URL(response.url());
      if (!url.hostname.endsWith('rhombusai.com')) return;
      const item = { method: response.request().method(), url: url.origin + url.pathname,
        status: response.status(), contentType: response.headers()['content-type'] };
      // Only anonymous failure response excerpts; no authenticated data.
      if ([401, 403].includes(response.status())) item.body = (await response.text()).slice(0, 1000);
      requests.push(item);
    })());
  });
  await page.goto('https://rhombusai.com/');
  await page.getByRole('button', { name: 'Log In', exact: true }).waitFor({ timeout: 30_000 });
  await page.goto('https://rhombusai.com/workflow/0');
  await page.locator('body').waitFor({ state: 'visible' });
  await writeFile('artifacts/anonymous-project-text.txt', await page.locator('body').innerText());
  await Promise.all(pending);
  await page.screenshot({ path: 'artifacts/public-smoke.png' });
  await writeFile('artifacts/public-network.json', JSON.stringify(requests, null, 2));
  console.log(JSON.stringify(requests));
} finally { await browser.close(); }
