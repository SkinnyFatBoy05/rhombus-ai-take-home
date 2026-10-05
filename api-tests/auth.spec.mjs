import { test, expect } from '@playwright/test';

// Both endpoints were observed in actual browser fetch traffic on 2026-09-30.
// See observations/evidence/api-discovery.md. No invented endpoint or mock server.
const backend = 'https://api.rhombusai.com';
test.use({ storageState: { cookies: [], origins: [] } });

for (const path of ['/api/accounts/users/profile', '/api/accounts/users/project-limit']) {
  test(`unauthenticated GET ${path} rejects access without returning account data`, async ({ request }) => {
    const response = await request.get(backend + path, { maxRedirects: 0 });
    expect(response.status()).toBe(401);
    expect(response.headers()['content-type']).toContain('application/json');
    expect(await response.json()).toEqual({ detail: 'Unauthorized' });
  });
}

test('invalid bearer token cannot read the user profile', async ({ request }) => {
  const response = await request.get(`${backend}/api/accounts/users/profile`, {
    headers: { Authorization: 'Bearer deliberately-invalid-assessment-token' }, maxRedirects: 0,
  });
  expect(response.status()).toBe(401);
  expect(response.headers()['content-type']).toContain('application/json');
  expect(await response.json()).toEqual({ detail: 'Unauthorized' });
});

test('unauthenticated output download cannot disclose assessment data', async ({ request }) => {
  // Observed XHR during the real output-download attempt on 5 October.
  // This tests access control only; it cannot diagnose an authenticated export.
  const response = await request.get(`${backend}/api/dataset/analyzer/v2/projects/0/nodes/output-download`, {
    params: { node_name: 'output_40ec5f2cb904bb2f4fa10c284d282375', format: 'csv', custom_filename: 'orders-clean' },
    maxRedirects: 0,
  });
  expect(response.status()).toBe(401);
  expect(response.headers()['content-type']).toContain('application/json');
  expect(await response.json()).toEqual({ detail: 'Unauthorized' });
});
