import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { join, resolve, relative, isAbsolute } from 'node:path';
import { requireBaselineData, validateBaselineDownload } from '../lib/output-validation.mjs';

// These are local contract tests using synthetic golden data, not Rhombus runs.
async function removeTestFolder(folder) {
  const target = resolve(folder);
  const inside = relative(resolve('artifacts'), target);
  assert.ok(inside && !inside.startsWith('..') && !isAbsolute(inside), 'Cleanup stays inside artifacts');
  await rm(target, { recursive: true, force: true });
}

test('a correct single CSV passes data assertions while retaining determinism gaps', async () => {
  await mkdir('artifacts', { recursive: true });
  const folder = await mkdtemp('artifacts/output-contract-');
  try {
    const { report, remainingCoverage } = await validateBaselineDownload({
      source: 'datasets/baseline.csv', output: 'datasets/expected/baseline-clean.csv',
      reportPath: join(folder, 'validation.json'),
    });
    assert.equal(report.passed, false);
    assert.deepEqual(remainingCoverage.map(check => check.check), ['determinism_sample_count', 'determinism_content']);
    const missingAssertion = { ...report, checks: report.checks.filter(check => check.check !== 'output_1.business_correctness') };
    assert.throws(() => requireBaselineData(missingAssertion), /business_correctness/);
  } finally { await removeTestFolder(folder); }
});

test('a readable CSV with one corrupted amount fails despite a successful export', async () => {
  await mkdir('artifacts', { recursive: true });
  const folder = await mkdtemp('artifacts/output-contract-');
  try {
    const output = join(folder, 'corrupted.csv');
    const golden = await readFile('datasets/expected/baseline-clean.csv', 'utf8');
    assert.ok(golden.includes('120.00'));
    await writeFile(output, golden.replace('120.00', '1200.00'));
    await assert.rejects(validateBaselineDownload({ source: 'datasets/baseline.csv', output,
      reportPath: join(folder, 'validation.json') }), /business_correctness/);
  } finally { await removeTestFolder(folder); }
});
