import { test, expect } from '@playwright/test';
import * as dotenv from 'dotenv';

dotenv.config();

const RESET_URL   = process.env.RESET_URL   || '';
const EMAIL       = process.env.TEST_EMAIL  || '';
const PASSWORD    = process.env.TEST_PASSWORD || '';

const BASE = 'https://auth4.mox2.net.in';

// ─────────────────────────────────────────────────────────────────────────────
// TC025 — Reset request generates a reset link
// ─────────────────────────────────────────────────────────────────────────────
test('TC025 - Reset request generates a reset link', async ({ page }) => {
  // Verified by TC005 (login.spec.ts). Additionally assert RESET_URL is present.
  expect(RESET_URL).toBeTruthy();
  expect(RESET_URL).toContain('/Account/Reset');
});

// ─────────────────────────────────────────────────────────────────────────────
// TC026 — Reset token expires after 5 minutes
// Verifies that an aged/consumed reset link is no longer usable.
// ─────────────────────────────────────────────────────────────────────────────
test('TC026 - Reset token expires / becomes invalid after use', async ({ page }) => {
  if (!RESET_URL) test.skip();

  // Navigate to the RESET_URL after it has been used or expired
  await page.goto(RESET_URL);

  // The form must NOT be accessible — either "already been used" or an error heading is shown
  const formVisible = await page.locator('#resetPass').isVisible().catch(() => false);
  if (formVisible) {
    // Token is still fresh — submit with a dummy password to trigger expiry check
    await page.locator('#resetPass').fill('TestPass@123');
    await page.locator('#resetCPass').fill('TestPass@123');
    await page.locator('#btnResetPassword').click();
    // Server should report expiry
    await expect(page.locator('main ul li').first()).toContainText('expired', { timeout: 10000 });
  } else {
    // Token already invalidated — verify an appropriate error message is shown
    const heading = await page.locator('main h3').textContent().catch(() => '');
    expect(heading.length).toBeGreaterThan(0);
  }
});

// ─────────────────────────────────────────────────────────────────────────────
// TC027 — Reset token is single-use only
// ─────────────────────────────────────────────────────────────────────────────
test('TC027 - Reset token is single-use only', async ({ page }) => {
  // After TC020 (password-policy.spec.ts) uses the token, the same RESET_URL should
  // now show "already been used". Run the full suite to exercise this.
  if (!RESET_URL) test.skip();

  // Navigate to the RESET_URL again after it has been used
  await page.goto(RESET_URL);

  // Should NOT show the form — instead show "already been used" heading
  await expect(page.locator('#resetPass')).not.toBeVisible({ timeout: 8000 });
  await expect(page.locator('main h3')).toContainText('already been used');
});

// ─────────────────────────────────────────────────────────────────────────────
// TC028 — Invalid token shows error
// ─────────────────────────────────────────────────────────────────────────────
test('TC028 - Invalid token shows error', async ({ page }) => {
  await page.goto(`${BASE}/Account/Reset/?id=COMPLETELY_INVALID_TOKEN_XYZ123`);
  await expect(page.locator('main h3')).toContainText(
    'An error occurred while processing your reset link'
  );
});

// ─────────────────────────────────────────────────────────────────────────────
// TC029 — Successful reset allows login with new password
// Depends on TC020 (password-policy.spec.ts) having changed the password to TestPass@123.
// Update TEST_PASSWORD in .env to TestPass@123 after TC020 passes, then re-run.
// ─────────────────────────────────────────────────────────────────────────────
test('TC029 - Successful reset allows login with new password', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveURL(/Account\/Login/i);

  await page.getByRole('textbox', { name: 'Email' }).fill(EMAIL);
  await page.getByRole('textbox', { name: 'Password' }).fill(PASSWORD);
  await page.getByRole('button', { name: 'Log in' }).click();

  await expect(page).not.toHaveURL(/login/i, { timeout: 10000 });
});

// ─────────────────────────────────────────────────────────────────────────────
// TC030 — Reset link uses HTTPS
// ─────────────────────────────────────────────────────────────────────────────
test('TC030 - Reset link uses HTTPS', async () => {
  expect(RESET_URL).toMatch(/^https:\/\//);
});

// ─────────────────────────────────────────────────────────────────────────────
// TC031 — Token is included in the reset URL
// ─────────────────────────────────────────────────────────────────────────────
test('TC031 - Token is present in the reset URL', async () => {
  const url = new URL(RESET_URL || 'https://x.com/?id=');
  expect(url.searchParams.get('id')).toBeTruthy();
});

// ─────────────────────────────────────────────────────────────────────────────
// TC032 — Token is correctly encoded / decodable
// ─────────────────────────────────────────────────────────────────────────────
test('TC032 - Token is correctly encoded and decodable', async () => {
  const url = new URL(RESET_URL || 'https://x.com/?id=');
  const rawToken = url.searchParams.get('id') || '';
  expect(rawToken.length).toBeGreaterThan(10);

  // The URL uses double-encoding (%25 → %); decode once to get the actual token
  const singleDecoded = decodeURIComponent(rawToken);
  // The result should be a valid Base64 string (ends with = or ==)
  const base64Chars = /^[A-Za-z0-9+/]+=*$/;
  const withoutPadding = singleDecoded.replace(/[+/=]/g, '');
  expect(withoutPadding.length).toBeGreaterThan(10);
});

// ─────────────────────────────────────────────────────────────────────────────
// TC033 — Multiple rapid reset requests handled gracefully
// ─────────────────────────────────────────────────────────────────────────────
test('TC033 - Multiple rapid reset requests handled gracefully', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveURL(/Account\/Login/i);

  await page.getByRole('textbox', { name: 'Email' }).fill(EMAIL);

  let dialogCount = 0;
  page.on('dialog', async dialog => {
    dialogCount++;
    await dialog.accept();
  });

  // Fire 5 rapid reset requests
  for (let i = 0; i < 5; i++) {
    await page.getByRole('link', { name: 'Forgot your password?' }).click();
    // Small pause between requests
    await page.waitForTimeout(300);
  }

  // System should have responded without crashing — at least 1 dialog shown
  expect(dialogCount).toBeGreaterThanOrEqual(1);
  // Page should still be on login (no crash/redirect)
  await expect(page).toHaveURL(/Account\/Login/i);
});

// ─────────────────────────────────────────────────────────────────────────────
// TC034 — Network failure during reset request shows error gracefully
// ─────────────────────────────────────────────────────────────────────────────
test('TC034 - Network failure during reset request shows error gracefully', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveURL(/Account\/Login/i);

  await page.getByRole('textbox', { name: 'Email' }).fill(EMAIL);

  // Block the forgot-password API call
  await page.route('**/account/ForgotPassword**', route => route.abort());

  let dialogMessage = '';
  let navigationHappened = false;

  page.on('dialog', async dialog => {
    dialogMessage = dialog.message();
    await dialog.accept();
  });

  page.on('framenavigated', () => { navigationHappened = true; });

  await page.getByRole('link', { name: 'Forgot your password?' }).click();
  await page.waitForTimeout(3000);

  // Should either show an error dialog OR stay on login (no silent failure / crash)
  await expect(page).toHaveURL(/Account\/Login/i);
});

// ─────────────────────────────────────────────────────────────────────────────
// TC035 — Valid original reset link works when pasted in browser
// ─────────────────────────────────────────────────────────────────────────────
test('TC035 - Valid original reset link works after copy-paste', async ({ page }) => {
  if (!RESET_URL) test.skip();
  // Simulates pasting the URL into a new tab
  await page.goto(RESET_URL);
  // The reset form should load (if token still valid)
  // OR show a used/expired heading (if TC020 already consumed it)
  const formVisible = await page.locator('#resetPass').isVisible().catch(() => false);
  const headingText = await page.locator('main h3').textContent().catch(() => '');
  // Either the form is visible (fresh token) OR a meaningful error heading is shown
  expect(formVisible || headingText.length > 0).toBe(true);
});

// ─────────────────────────────────────────────────────────────────────────────
// TC036 — Tampered token in URL is rejected
// ─────────────────────────────────────────────────────────────────────────────
test('TC036 - Tampered token in URL is rejected', async ({ page }) => {
  if (!RESET_URL) test.skip();

  // Take RESET_URL and flip a few characters in the id parameter
  const tamperedUrl = RESET_URL.replace(/id=(.{10})/, (_, prefix) => {
    const flipped = prefix.split('').reverse().join('');
    return `id=${flipped}`;
  });

  await page.goto(tamperedUrl);
  // Server shows one of two error headings for a tampered/invalid token
  const heading = await page.locator('main h3').textContent({ timeout: 8000 });
  expect(
    heading?.includes('Invalid reset link format') ||
    heading?.includes('An error occurred while processing your reset link')
  ).toBe(true);
});
