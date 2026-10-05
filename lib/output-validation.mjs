import { execFile } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { promisify } from 'node:util';

const run = promisify(execFile);

// A single downloaded output can establish data correctness, but cannot establish
// determinism or bind that file to a particular scheduled run. Keep those gaps.
export function requireBaselineData(report) {
  if (report.scenario !== 'baseline' || report.error || report.outputs?.length !== 1) {
    throw new Error('Expected one actual baseline output and a valid validation report.');
  }
  const required = ['source_fixture_identity', 'source_schema', 'outputs_present',
    'output_1.schema', 'output_1.row_count', 'output_1.unique_ids',
    'output_1.sorted_ids', 'output_1.business_correctness', 'output_1.cleaning_rules'];
  const failures = required.filter(name => report.checks?.find(check => check.check === name)?.passed !== true);
  if (failures.length) throw new Error(`Downloaded baseline failed: ${failures.join(', ')}`);
  return report.checks.filter(check => !check.passed);
}

export async function validateBaselineDownload({ source, output, reportPath }) {
  try {
    await run(process.env.PYTHON || 'python', ['data-validation/validate.py',
      '--scenario', 'baseline', '--input', source, '--output', output, '--report', reportPath],
    { timeout: 30_000, windowsHide: true });
  } catch (error) {
    // Exit 1 includes determinism coverage gaps. Inspect each data check below;
    // never treat exit 1 itself as success. Exit 2/process failures remain errors.
    if (error.code !== 1) throw error;
  }
  const report = JSON.parse(await readFile(reportPath, 'utf8'));
  const remainingCoverage = requireBaselineData(report);
  return { report, remainingCoverage };
}
