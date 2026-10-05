// Interactive capture utility for YOUR assessment account. Raw HAR and storage
// state contain secrets: saved only under ignored artifacts/ and .auth/.
import { chromium } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import { createInterface } from 'node:readline/promises';
import { stdin, stdout } from 'node:process';

await mkdir('artifacts', { recursive: true });
await mkdir('.auth', { recursive: true });
// Use a supported installed browser when requested, with normal automation
// settings. Never hide automation or bypass provider security warnings.
const channel = process.env.RHOMBUS_BROWSER_CHANNEL || undefined;
if (channel && !['chrome', 'msedge'].includes(channel)) {
  throw new Error('RHOMBUS_BROWSER_CHANNEL must be chrome or msedge, or unset for bundled Chromium.');
}
const browser = await chromium.launch({ headless: false, ...(channel ? { channel } : {}) });
const context = await browser.newContext({ recordHar: { path: 'artifacts/session.har', mode: 'full' } });
const page = await context.newPage();
const requests = [];
page.on('response', response => {
  const request = response.request();
  if (!['xhr', 'fetch'].includes(request.resourceType())) return;
  const url = new URL(response.url());
  // Strip query values and NEVER record headers/bodies in the shareable index.
  requests.push({ method: request.method(), origin: url.origin, path: url.pathname,
    queryKeys: [...url.searchParams.keys()], status: response.status() });
});
const readline = createInterface({ input: stdin, output: stdout });
const cancellation = new AbortController();
const cancel = () => cancellation.abort();
readline.on('SIGINT', cancel);
process.once('SIGINT', cancel);
try {
  await page.goto('https://rhombusai.com/');
  await readline.question('Sign in using a supported method, open the assessment project, and inspect its sources, schedule and logs. Do not bypass a browser or sign-in security warning. Press Enter when done, or Ctrl+C to cancel. ', { signal: cancellation.signal });
  const url = new URL(page.url());
  if (url.origin !== 'https://rhombusai.com' || !/^\/workflow\/\d+$/.test(url.pathname)) {
    throw new Error('Capture not saved: open the signed-in Rhombus assessment workflow first.');
  }
  await page.getByRole('tab', { name: 'AI Builder', exact: true }).waitFor({ state: 'visible', timeout: 15_000 });
  await context.storageState({ path: '.auth/rhombus.json', indexedDB: true });
  await writeFile('artifacts/request-index.json', JSON.stringify(requests, null, 2));
  console.log('Saved private capture. Inspect Network/HAR to configure real endpoints; redact evidence before sharing.');
} catch (error) {
  if (cancellation.signal.aborted || error.name === 'AbortError') {
    console.log('Capture cancelled; no new authentication state saved.');
    process.exitCode = 130;
  } else {
    console.error(error.message);
    process.exitCode = 1;
  }
} finally {
  process.removeListener('SIGINT', cancel);
  readline.close();
  await context.close();
  await browser.close();
}
