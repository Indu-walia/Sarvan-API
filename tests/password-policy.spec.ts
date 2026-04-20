import { test, expect } from '@playwright/test';
import * as dotenv from 'dotenv';

dotenv.config();

const RESET_URL = process.env.RESET_URL || '';

// Helper: navigate to the reset page and wait for form
async function gotoResetPage(page: any) {
  await page.goto(RESET_URL);
  await expect(page.locator('#resetPass')).toBeVisible({ timeout: 10000 });
}

// Helper: check server returned an error (ul li in main)
async function expectServerError(page: any) {
  await expect(page.locator('main ul li').first()).toBeVisible({ timeout: 8000 });
}

// Helper: check NO server error
async function expectNoServerError(page: any) {
  await expect(page.locator('main ul li')).not.toBeVisible({ timeout: 5000 });
}

test.describe('Password Policy — Length Validation (TC006–TC009)', () => {

  test.beforeEach(async ({ page }) => {
    if (!RESET_URL) test.skip();
    await gotoResetPage(page);
  });

  // TC006: Reject password shorter than 5 characters
  test('TC006 - Reject password shorter than 5 characters', async ({ page }) => {
    await page.locator('#resetPass').fill('Ab@1');        // 4 chars
    await page.locator('#resetCPass').fill('Ab@1');
    await page.locator('#btnResetPassword').click();
    // Server must reject — any ul li error qualifies
    await expectServerError(page);
  });

  // TC007: Accept password of exactly 5 characters (route-aborted — does not change password)
  test('TC007 - Accept password of exactly 5 characters', async ({ page }) => {
    // Intercept the form POST so the password is NOT actually changed
    await page.route('**/Account/Reset', route => route.abort());
    await page.locator('#resetPass').fill('Ab@1x');       // exactly 5 chars
    await page.locator('#resetCPass').fill('Ab@1x');
    // Client validation passes → form submits → route aborted (page may navigate away)
    await Promise.allSettled([page.locator('#btnResetPassword').click()]);
    await page.waitForTimeout(500);
    // If the element is still present, check no client-side error placeholder
    const ph = await page.locator('#resetCPass').getAttribute('placeholder', { timeout: 2000 }).catch(() => null);
    if (ph !== null) {
      expect(ph).not.toBe("Passwords don't match!");
      expect(ph).not.toBe('Confirm password is required!');
    }
    // ph === null means page navigated (route aborted navigation) — client validation passed
  });

  // TC008: Accept password of exactly 20 characters (route-aborted — does not change password)
  test('TC008 - Accept password of exactly 20 characters', async ({ page }) => {
    await page.route('**/Account/Reset', route => route.abort());
    await page.locator('#resetPass').fill('Abcdef@12345678!Zz01');  // exactly 20 chars
    await page.locator('#resetCPass').fill('Abcdef@12345678!Zz01');
    await Promise.allSettled([page.locator('#btnResetPassword').click()]);
    await page.waitForTimeout(500);
    const ph = await page.locator('#resetCPass').getAttribute('placeholder', { timeout: 2000 }).catch(() => null);
    if (ph !== null) {
      expect(ph).not.toBe("Passwords don't match!");
      expect(ph).not.toBe('Confirm password is required!');
    }
  });

  // TC009: Reject password longer than 20 characters
  test('TC009 - Reject password longer than 20 characters', async ({ page }) => {
    await page.locator('#resetPass').fill('Abcdef@12345678!Zz01X'); // 21 chars
    await page.locator('#resetCPass').fill('Abcdef@12345678!Zz01X');
    await page.locator('#btnResetPassword').click();
    await expectServerError(page);
  });

});

test.describe('Password Policy — Complexity Validation (TC010–TC020)', () => {

  test.beforeEach(async ({ page }) => {
    if (!RESET_URL) test.skip();
    await gotoResetPage(page);
  });

  // TC010: Reject password missing uppercase letter
  test('TC010 - Reject password missing uppercase letter', async ({ page }) => {
    await page.locator('#resetPass').fill('testpass@1');   // no uppercase
    await page.locator('#resetCPass').fill('testpass@1');
    await page.locator('#btnResetPassword').click();
    await expectServerError(page);
  });

  // TC011: Reject password missing lowercase letter
  test('TC011 - Reject password missing lowercase letter', async ({ page }) => {
    await page.locator('#resetPass').fill('TESTPASS@1');   // no lowercase
    await page.locator('#resetCPass').fill('TESTPASS@1');
    await page.locator('#btnResetPassword').click();
    await expectServerError(page);
  });

  // TC012: Reject password missing a number
  test('TC012 - Reject password missing a number', async ({ page }) => {
    await page.locator('#resetPass').fill('TestPass@!');   // no digit
    await page.locator('#resetCPass').fill('TestPass@!');
    await page.locator('#btnResetPassword').click();
    await expectServerError(page);
  });

  // TC013: Reject password missing special character
  test('TC013 - Reject password missing special character', async ({ page }) => {
    await page.locator('#resetPass').fill('TestPass123');  // no special char
    await page.locator('#resetCPass').fill('TestPass123');
    await page.locator('#btnResetPassword').click();
    await expectServerError(page);
  });

  // TC014: Client validates — confirm matches new password (no mismatch error)
  test('TC014 - No client error when confirm password matches', async ({ page }) => {
    // Abort the POST so the password is not changed; we only verify client-side behaviour
    await page.route('**/Account/Reset', route => route.abort());
    await page.locator('#resetPass').fill('TestPass@123');
    await page.locator('#resetCPass').fill('TestPass@123');
    await Promise.allSettled([page.locator('#btnResetPassword').click()]);
    await page.waitForTimeout(500);
    const ph = await page.locator('#resetCPass').getAttribute('placeholder', { timeout: 2000 }).catch(() => null);
    if (ph !== null) {
      expect(ph).not.toBe("Passwords don't match!");
    }
    // ph === null means page navigated after abort — client validation passed
  });

  // TC015: Reject when confirm password does not match
  test('TC015 - Reject mismatched confirm password', async ({ page }) => {
    await page.locator('#resetPass').fill('TestPass@123');
    await page.locator('#resetCPass').fill('TestPass@456');
    await page.locator('#btnResetPassword').click();
    // Client sets error as placeholder on #resetCPass
    await expect(page.locator('#resetCPass')).toHaveAttribute('placeholder', "Passwords don't match!");
  });

  // TC016: Reject password containing only spaces
  test('TC016 - Reject password containing only spaces', async ({ page }) => {
    await page.locator('#resetPass').fill('     ');       // 5 spaces
    await page.locator('#resetCPass').fill('     ');
    await page.locator('#btnResetPassword').click();
    await page.waitForTimeout(1000);
    // Server may reject via ul li, navigate to an error page, or remove the form
    const serverError = await page.locator('main ul li').first().isVisible().catch(() => false);
    const invalidRequest = (await page.locator('body').textContent().catch(() => '')).includes('Invalid request');
    const formGone = !(await page.locator('#resetPass').isVisible().catch(() => true));
    expect(serverError || invalidRequest || formGone).toBe(true);
  });

  // TC017: Reject password containing only special characters
  test('TC017 - Reject password containing only special characters', async ({ page }) => {
    await page.locator('#resetPass').fill('@$!%*?&@');    // special chars only, no upper/lower/number
    await page.locator('#resetCPass').fill('@$!%*?&@');
    await page.locator('#btnResetPassword').click();
    await expectServerError(page);
  });

  // TC018: Reject when confirm password field is empty
  test('TC018 - Reject when confirm password field is empty', async ({ page }) => {
    await page.locator('#resetPass').fill('TestPass@123');
    // Leave confirm empty
    await page.locator('#btnResetPassword').click();
    await expect(page.locator('#resetCPass')).toHaveAttribute('placeholder', 'Confirm password is required!');
  });

  // TC019: Reject reuse of recently used password
  // NOTE: Submits the form — consumes the reset token if server accepts another password change.
  // Run this test only when RESET_URL is fresh and the account has history data.
  test('TC019 - Reject reuse of recently used password', async ({ page }) => {
    const currentPassword = process.env.TEST_PASSWORD || 'Pro@987';
    await page.locator('#resetPass').fill(currentPassword);
    await page.locator('#resetCPass').fill(currentPassword);
    await page.locator('#btnResetPassword').click();
    await expectServerError(page);
  });

  // TC020: Valid password meeting all rules is accepted
  // NOTE: This test CHANGES the account password to Uptime@2025.
  // Update TEST_PASSWORD in .env after this test runs.
  test('TC020 - Valid password meeting all rules is accepted', async ({ page }) => {
    await page.locator('#resetPass').fill('Uptime@2025');
    await page.locator('#resetCPass').fill('Uptime@2025');
    await page.locator('#btnResetPassword').click();
    // On success: redirect away from reset page
    await page.waitForURL(url => !url.pathname.startsWith('/Account/Reset'), { timeout: 10000 });
  });

});
