import { readFileSync } from 'node:fs';
import { loadLive } from '../lib/journey.mjs';

try {
  const config = loadLive();
  let state;
  try { state = JSON.parse(readFileSync(config.storageState, 'utf8')); }
  catch { throw new Error('Authenticated CLI session missing. Use npm run capture with a supported login; do not bypass a sign-in security warning. The inbuilt browser session is separate.'); }
  if (!Array.isArray(state.cookies) || !Array.isArray(state.origins) || state.cookies.length + state.origins.length === 0) {
    throw new Error('Storage state is empty or invalid; an actual supported Rhombus login is required.');
  }
  readFileSync(config.builderPrompt, 'utf8');
  readFileSync(config.sourceSnapshot); // Actual downloaded S3 baseline, not an output fixture.
  if (process.env.RHOMBUS_ALLOW_LIVE_WRITES !== '1') throw new Error('Set RHOMBUS_ALLOW_LIVE_WRITES=1 only for this authorized assessment project.');
  console.log('UI prerequisites present; authentication validity will be checked by the real workflow test.');
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
