import { readFileSync } from 'node:fs';
import { expect } from '@playwright/test';

export function validateConfig(config) {
  const url = new URL(config.projectUrl);
  if (url.origin !== 'https://rhombusai.com' || !/^\/workflow\/\d+$/.test(url.pathname) || url.search || url.hash || url.username || url.password) {
    throw new Error('Expected an exact Rhombus workflow URL.');
  }
  if (config.projectConfirmed !== true) throw new Error('Confirm this is the disposable assessment project before enabling writes.');
  if (!['local_download', 's3'].includes(config.destinationProvider)) throw new Error('Only the candidate-approved local_download or S3 deviation is supported.');
  for (const key of ['projectName', 'sourceName', 's3Bucket', 's3RegionLabel', 'sourcePrefix', 'sourceObject', 'storageState', 'builderPrompt', 'sourceSnapshot']) {
    if (typeof config[key] !== 'string' || !config[key].trim()) throw new Error(`Missing configuration: ${key}`);
  }
  if (!config.sourceObject.startsWith(config.sourcePrefix)) throw new Error('Source object must be within its configured prefix.');
  if (config.destinationProvider === 's3') {
    if (config.destinationBucket !== config.s3Bucket) throw new Error('S3 output must use the same dedicated assessment bucket.');
    if (config.outputFilename !== 'orders-clean' || config.outputKey !== 'orders-clean.csv') {
      throw new Error('S3 output must use the reviewed single orders-clean.csv object; the UI rejects folder paths.');
    }
    if (config.destinationProvisioned !== true) throw new Error('Provision and verify the S3 destination before running this suite; it never creates or handles cloud credentials.');
    if (typeof config.awsReadProfile !== 'string' || !config.awsReadProfile.trim()) throw new Error('S3 verification needs a separately authorized named read-only AWS profile.');
  }
  if (config.scheduleCron !== '*/5 * * * *') throw new Error('This bounded test uses the observed five-minute schedule only.');
  return config;
}

export function loadLive(path = 'config/live.json') {
  let config;
  try { config = JSON.parse(readFileSync(path, 'utf8')); }
  catch { throw new Error('Live setup incomplete: create ignored config/live.json from the example and capture .auth/rhombus.json.'); }
  return validateConfig(config);
}

export const chatInput = page => page.locator('textarea[data-rcb-element="chat-input-textarea"]');

export async function connectSource(page, config) {
  await page.getByRole('tab', { name: 'AI Builder', exact: true }).click();
  // Observed unnamed attachment control; avoid nth-child/coordinate selectors.
  await page.locator('button.workflow-composer-control[aria-haspopup="menu"]').filter({ hasText: /^$/ }).click();
  await page.getByRole('menuitem', { name: 'Third party sources', exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Third Party Data', exact: true });
  const existing = dialog.getByRole('heading', { name: config.sourceName, exact: true });
  await expect.poll(async () => (await existing.count()) + (await dialog.getByRole('button', { name: 'Add Data Sources', exact: true }).count()), { timeout: 30_000 }).toBeGreaterThan(0);
  if (await existing.count()) {
    const browse = dialog.getByRole('button', { name: 'Browse files', exact: true });
    if (await browse.count()) {
      // Refuse an ambiguous multi-source account rather than picking by position.
      await expect(browse).toHaveCount(1);
      await browse.click();
    }
  } else {
    await dialog.getByRole('button', { name: 'Add Data Sources', exact: true }).click();
    await dialog.getByRole('heading', { name: 'Amazon S3', exact: true }).click();
    await dialog.getByRole('textbox', { name: 'Bucket*', exact: true }).fill(config.s3Bucket);
    await dialog.getByRole('combobox', { name: 'Region*', exact: true }).click();
    await page.getByRole('option', { name: config.s3RegionLabel, exact: true }).click();
    await dialog.getByRole('button', { name: 'Optional settings Folder, source name, and KMS encryption', exact: true }).click();
    await dialog.getByPlaceholder('analytics/q1/', { exact: true }).fill(config.sourcePrefix);
    await dialog.getByPlaceholder('Q1 analytics', { exact: true }).fill(config.sourceName);
    // Bucket-policy access must already be provisioned outside this suite.
    await dialog.getByRole('button', { name: 'Connect S3 source', exact: true }).click();
  }
  await expect(dialog.getByRole('heading', { name: config.sourceName, exact: true })).toBeVisible({ timeout: 90_000 });
  await expect(dialog.getByText('Connected', { exact: true })).toBeVisible();
  await expect(dialog.getByRole('row').filter({ hasText: config.sourceObject })).toHaveCount(1);
  await expect(dialog).toContainText(`s3://${config.s3Bucket}/${config.sourcePrefix}`);
  await dialog.getByRole('button', { name: 'Cancel', exact: true }).click();
}

export const outputNodeName = config => config.destinationProvider === 's3'
  ? `Data Output Data Output Export to ${config.destinationBucket} (csv)`
  : 'Data Output Export to Download Locally (csv)';

export async function buildAndConfigureOutput(page, config) {
  const input = chatInput(page);
  const prompt = readFileSync(config.builderPrompt, 'utf8');
  const clearCommand = page.getByRole('button', { name: 'Clear active command', exact: true });
  if (await clearCommand.count()) await clearCommand.click();
  await input.fill('/');
  await page.getByRole('button', { name: 'Pipeline /pipeline Focus this turn on pipeline and canvas work', exact: true }).click();
  await input.fill(prompt);
  await input.press('Enter');
  await expect(input).toBeDisabled();
  await expect(input).toBeEditable({ timeout: 8 * 60_000 });
  // A generated message is not the assertion: inspect the actual canvas/output.
  await page.getByRole('tab', { name: 'Canvas', exact: true }).click();
  await page.getByRole('button', { name: /^Data Output / }).click();
  const panel = page.getByRole('complementary');
  if (config.destinationProvider === 's3') {
    await panel.getByRole('button', { name: `Amazon S3 ${config.destinationBucket}`, exact: true }).click();
  } else {
    await panel.getByRole('button', { name: /^Download Locally Skip cloud upload/ }).click();
  }
  await panel.getByPlaceholder('RhombusAI_output', { exact: true }).fill(config.outputFilename || 'orders-clean');
  await panel.getByRole('button', { name: 'Apply', exact: true }).click();
  await expect(page.getByRole('button', { name: outputNodeName(config), exact: true })).toBeVisible();
}

export async function assessmentScheduleCard(page, config) {
  const panel = page.getByRole('complementary');
  // The app currently provides no schedule-card role/test id. These classes
  // identify the observed card header; recurrence prevents selecting a second
  // diagnostic schedule in the same project.
  const card = panel.locator('div.flex.items-center.justify-between.gap-4.p-4.pl-5')
    .filter({ hasText: `Custom: ${config.scheduleCron}` })
    .filter({ hasText: config.projectName });
  await expect(card).toHaveCount(1);
  return card;
}

export async function openHistory(page, config) {
  await page.getByRole('tab', { name: 'Schedule', exact: true }).click();
  const card = await assessmentScheduleCard(page, config);
  const history = card.getByRole('button').filter({ has: page.locator('svg.lucide-history') });
  await expect(history).toHaveCount(1);
  await history.click();
  await expect(page.getByRole('tab', { name: 'Executions', exact: true })).toHaveAttribute('aria-selected', 'true');
}

export async function executionRows(page) {
  const table = page.getByRole('table');
  await expect(table.getByRole('columnheader', { name: 'Execution', exact: true })).toBeVisible();
  const rows = await table.locator('tbody tr').evaluateAll(elements => elements.map(row => [...row.querySelectorAll('td')].map(cell => cell.textContent.trim())));
  return rows.filter(cells => cells.length === 6).map(cells => ({ id: cells[0], started: cells[1], duration: cells[2], status: cells[3], failedNode: cells[4], completedNodes: cells[5] }));
}

export function newSuccessfulExecution(rows, priorIds) {
  // No generic toast or historical badge can satisfy this check.
  return rows.find(row => row.id && !priorIds.has(row.id) && /^(completed|success|succeeded)$/i.test(row.status) && /^(—|-|none|n\/a|)$/i.test(row.failedNode) && /^4(?:\s*\/\s*4)?$/.test(row.completedNodes));
}

export async function disableAssessmentSchedule(page, config) {
  await page.getByRole('tab', { name: 'Schedule', exact: true }).click();
  const card = await assessmentScheduleCard(page, config);
  const active = card.getByRole('switch', { name: 'Deactivate schedule', exact: true });
  if (await active.count()) await active.click();
  await expect(card.getByRole('switch', { name: 'Activate schedule', exact: true })).toHaveAttribute('aria-checked', 'false', { timeout: 30_000 });
}
