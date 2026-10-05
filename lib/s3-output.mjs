import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
const run = promisify(execFile);

// The profile is provisioned separately. No key appears in configuration or args.
export async function witnessS3(config, { mode, report, prior, since, output }) {
  const args = ['data-validation/s3_output.py', mode, '--bucket', config.destinationBucket,
    '--key', config.outputKey, '--aws-profile', config.awsReadProfile, '--report', report];
  if (mode === 'capture') args.push('--prior', prior, '--since', since, '--output', output);
  await run(process.env.PYTHON || 'python', args, { timeout: 90_000, windowsHide: true });
}
