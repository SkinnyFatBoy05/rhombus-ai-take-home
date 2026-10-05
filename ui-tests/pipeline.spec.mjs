import { test, expect } from '@playwright/test';
import { access, writeFile } from 'node:fs/promises';
import { loadLive, connectSource, buildAndConfigureOutput, outputNodeName, openHistory, executionRows, newSuccessfulExecution, disableAssessmentSchedule, assessmentScheduleCard } from '../lib/journey.mjs';
import { validateBaselineDownload } from '../lib/output-validation.mjs';
import { witnessS3 } from '../lib/s3-output.mjs';

// Uses controls observed in the signed-in app. Execution through this CLI remains
// blocked until a supported login supplies its own private storage state.
test('S3 -> AI-built cleaning -> configured output -> new scheduled success', async ({ browser }, testInfo) => {
  test.setTimeout(22 * 60_000);
  const config = loadLive();
  if (process.env.RHOMBUS_ALLOW_LIVE_WRITES !== '1') throw new Error('Set RHOMBUS_ALLOW_LIVE_WRITES=1 only for the authorized assessment project.');
  await access(config.storageState); // Fail before opening/mutating without auth.
  await access(config.sourceSnapshot);
  const context = await browser.newContext({ storageState: config.storageState, acceptDownloads: true });
  const page = await context.newPage();
  let scheduleTouched = false;
  let scheduleActivation;
  const priorObject = testInfo.outputPath('s3-before-schedule.json');
  try {
    // Fail before browser mutations if the independent read-only profile is unavailable.
    if (config.destinationProvider === 's3') {
      await witnessS3(config, { mode: 'observe', report: testInfo.outputPath('s3-preflight.json') });
    }
    await page.goto(config.projectUrl);
    await expect(page).toHaveURL(config.projectUrl);
    await expect(page.getByRole('tab', { name: 'AI Builder', exact: true })).toBeVisible();
    await test.step('connect or verify the scoped S3 source', () => connectSource(page, config));
    await test.step('build with AI and select the configured output', () => buildAndConfigureOutput(page, config));
    const priorIds = new Set();
    await test.step('create or resume the single supervised schedule', async () => {
      // Builder/configuration can perform a manual run. Take the comparison
      // version only after those actions so it cannot count as a scheduled export.
      if (config.destinationProvider === 's3') {
        await witnessS3(config, { mode: 'observe', report: priorObject });
        await testInfo.attach('s3-before-schedule', { path: priorObject, contentType: 'application/json' });
      }
      await page.getByRole('tab', { name: 'Schedule', exact: true }).click();
      const panel = page.getByRole('complementary');
      await expect(panel.getByText('Loading schedules...', { exact: true })).toHaveCount(0);
      const switches = panel.getByRole('switch');
      if (await switches.count()) {
        const card = await assessmentScheduleCard(page, config);
        await expect(panel.getByRole('switch', { name: 'Deactivate schedule', exact: true })).toHaveCount(0);
        await expect(card.getByRole('switch', { name: 'Activate schedule', exact: true })).toBeVisible();
        await expect(card).toContainText(`Custom: ${config.scheduleCron}`);
        await expect(card.getByRole('button', { name: 'Notify on failure', exact: true })).toHaveAttribute('aria-pressed', 'false');
        await openHistory(page, config);
        for (const row of await executionRows(page)) priorIds.add(row.id);
        scheduleTouched = true;
        scheduleActivation = new Date().toISOString();
        await card.getByRole('switch', { name: 'Activate schedule', exact: true }).click();
      } else {
        await panel.getByRole('button', { name: 'Add Schedule', exact: true }).click();
        const dialog = page.getByRole('dialog', { name: 'Create Schedule', exact: true });
        await dialog.getByRole('combobox').filter({ visible: true }).click();
        await page.getByRole('option', { name: 'Custom', exact: true }).click();
        await dialog.getByLabel('Custom Cron Expression', { exact: true }).fill(config.scheduleCron);
        const notify = dialog.getByRole('button', { name: 'Notify on failure', exact: true });
        if (await notify.getAttribute('aria-pressed') === 'true') await notify.click();
        await expect(notify).toHaveAttribute('aria-pressed', 'false');
        scheduleTouched = true;
        scheduleActivation = new Date().toISOString();
        await dialog.getByRole('button', { name: 'Create', exact: true }).click();
        await expect(dialog).toBeHidden({ timeout: 30_000 });
      }
      const activeCard = await assessmentScheduleCard(page, config);
      await expect(activeCard.getByRole('switch', { name: 'Deactivate schedule', exact: true })).toHaveAttribute('aria-checked', 'true');
    });
    let observed = [];
    await test.step('require a new successful scheduled execution', async () => {
      // The observed history did not auto-refresh. Each condition-based poll
      // reloads persisted state; polling ends on evidence or a bounded timeout.
      await expect.poll(async () => {
        await page.reload();
        await openHistory(page, config);
        observed = await executionRows(page);
        return Boolean(newSuccessfulExecution(observed, priorIds));
      }, { timeout: 8 * 60_000, intervals: [5_000, 15_000, 30_000], message: 'No new successful scheduled execution appeared; a countdown is not execution evidence.' }).toBe(true);
      const record = { destinationDeviation: `${config.destinationProvider}; GCS not tested`, priorIds: [...priorIds], executions: observed };
      const evidence = testInfo.outputPath('scheduled-executions.json');
      await writeFile(evidence, JSON.stringify(record, null, 2));
      await testInfo.attach('scheduled-executions', { path: evidence, contentType: 'application/json' });
    });
    // Stop the schedule before inspecting the result so a following run cannot
    // change the preview during capture. Cleanup below also handles failures.
    await disableAssessmentSchedule(page, config);
    if (config.destinationProvider === 's3') {
      await test.step('require and validate a fresh exact S3 output version', async () => {
        const output = testInfo.outputPath('baseline-s3-output.csv');
        const metadata = testInfo.outputPath('s3-output-version.json');
        await witnessS3(config, { mode: 'capture', prior: priorObject,
          since: scheduleActivation, report: metadata, output });
        await testInfo.attach('s3-output-version', { path: metadata, contentType: 'application/json' });
        await testInfo.attach('actual-s3-csv', { path: output, contentType: 'text/csv' });
        const reportPath = testInfo.outputPath('baseline-s3-validation.json');
        try { await validateBaselineDownload({ source: config.sourceSnapshot, output, reportPath }); }
        finally {
          if (await access(reportPath).then(() => true, () => false)) {
            await testInfo.attach('s3-data-validation', { path: reportPath, contentType: 'application/json' });
          }
        }
      });
      return; // A preview download must never stand in for an S3 export.
    }
    // Live drift testing showed the in-page preview retaining a previous run's
    // data. Reload persisted state before selecting the output preview.
    await page.reload();
    await test.step('download CSV and assert its contents against the saved S3 input', async () => {
      await page.getByRole('tab', { name: 'Canvas', exact: true }).click();
      // Selecting a node only opens its settings. The Preview tab can still
      // contain the input dataset; use this output node's observed eye control.
      const outputNode = page.getByRole('button', { name: outputNodeName(config), exact: true });
      const previewOutput = outputNode.locator('button').filter({ has: page.locator('svg.lucide-eye') });
      await expect(previewOutput).toHaveCount(1);
      await previewOutput.click();
      await expect(page.getByRole('tab', { name: 'Preview', exact: true })).toHaveAttribute('aria-selected', 'true');
      await expect(page.getByRole('heading', { name: 'Node Preview', exact: true })).toBeVisible();
      await page.getByRole('button', { name: 'Download', exact: true }).click();
      const [download] = await Promise.all([
        page.waitForEvent('download', { timeout: 30_000 }),
        page.getByRole('menuitem', { name: 'Download as CSV', exact: true }).click(),
      ]);
      const output = testInfo.outputPath('baseline-output.csv');
      await download.saveAs(output);
      const reportPath = testInfo.outputPath('baseline-output-validation.json');
      // Attach the diagnostic report even when the downloaded data fails.
      try {
        await validateBaselineDownload({ source: config.sourceSnapshot, output, reportPath });
      } finally {
        await testInfo.attach('downloaded-output', { path: output, contentType: 'text/csv' });
        const reportExists = await access(reportPath).then(() => true, () => false);
        if (reportExists) await testInfo.attach('output-validation', { path: reportPath, contentType: 'application/json' });
      }
      // This is a content assertion, not proof of run-to-file provenance or
      // repeated-run determinism; those require separately captured manifests.
    });
  } finally {
    try {
      if (scheduleTouched && !page.isClosed()) {
        // Reload resolves pending create/toggle requests before checking state.
        await page.reload();
        await disableAssessmentSchedule(page, config);
      }
    } finally { await context.close(); }
  }
});
