import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { loadLive, validateConfig, newSuccessfulExecution } from '../lib/journey.mjs';

const configured = () => ({ ...JSON.parse(readFileSync('config/live.example.json', 'utf8')), projectConfirmed: true });
test('unconfirmed assessment target fails before mutations', () => {
  assert.throws(() => loadLive('config/live.example.json'), /Confirm this is the disposable/);
});
test('missing configuration gives setup instructions', () => {
  assert.throws(() => loadLive('config/does-not-exist.json'), /Live setup incomplete/);
});
test('confirmed local configuration validates', () => {
  assert.equal(validateConfig(configured()).destinationProvider, 'local_download');
});

const s3Configured = () => ({ ...JSON.parse(readFileSync('config/live.s3.example.json', 'utf8')), projectConfirmed: true, destinationProvisioned: true });
test('provisioned S3 configuration uses the reviewed single output object', () => {
  assert.equal(validateConfig(s3Configured()).outputKey, 'orders-clean.csv');
});
test('S3 config refuses another bucket, unexpected key, folder filename and missing provisioning', () => {
  for (const change of [{ destinationBucket: 'unrelated' }, { outputKey: 'input/orders.csv' }, { outputFilename: 'output/orders-clean' }, { destinationProvisioned: false }, {awsReadProfile: ''}]) {
    assert.throws(() => validateConfig({ ...s3Configured(), ...change }));
  }
});
test('foreign origins, non-workflow pages and credential URLs are rejected', () => {
  for (const projectUrl of ['https://example.com/workflow/0', 'https://rhombusai.com/', 'https://user@rhombusai.com/workflow/0', 'https://rhombusai.com/workflow/0?other=1']) {
    assert.throws(() => validateConfig({ ...configured(), projectUrl }), /exact Rhombus workflow/);
  }
});
test('unauthorized destination and out-of-scope source are rejected', () => {
  assert.throws(() => validateConfig({ ...configured(), destinationProvider: 'gcs' }), /candidate-approved/);
  assert.throws(() => validateConfig({ ...configured(), sourceObject: 'other/orders.csv' }), /within its configured prefix/);
});
const successful = { id: 'new-run', started: '2026-09-30T09:00:00Z', status: 'completed', failedNode: '—', completedNodes: '4' };
test('old successful run cannot satisfy a new scheduled outcome', () => {
  assert.equal(newSuccessfulExecution([successful], new Set(['new-run'])), undefined);
});
test('failure, generic success text and partial node completion are rejected', () => {
  for (const change of [{ status: 'error' }, { status: 'Pipeline execution completed successfully.' }, { failedNode: 'orders_output' }, { completedNodes: '3' }]) {
    assert.equal(newSuccessfulExecution([{ ...successful, ...change }], new Set()), undefined);
  }
});
test('a new four-node successful execution is accepted', () => {
  assert.equal(newSuccessfulExecution([successful], new Set(['old-run'])), successful);
});
