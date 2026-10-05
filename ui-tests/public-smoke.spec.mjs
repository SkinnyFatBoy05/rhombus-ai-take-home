import { test, expect } from '@playwright/test';

// Locators observed on the actual signed-out page on 29 and 30 September 2026.
// This is supplemental evidence, NOT the required authenticated pipeline journey.
test('signed-out visitor sees authentication requirement and usable entry controls', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle('Rhombus AI');
  await expect(page.getByText('Please log in to access projects', { exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Log In', exact: true })).toBeEnabled();
  await expect(page.getByRole('button', { name: 'Create a project', exact: true })).toBeVisible();
});
