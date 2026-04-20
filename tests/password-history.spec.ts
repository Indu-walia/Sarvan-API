import { test, expect } from '@playwright/test';
import * as dotenv from 'dotenv';

dotenv.config();

const RESET_URL = process.env.RESET_URL || '';

// Password History Validation — TC021–TC024
// These tests require the RESET_URL to be a fresh (unused, non-expired) reset link.
// The server enforces a 5-password history via usp_validatePassword.

test.describe('Password History Validation (TC021–TC024)', () => {

  test.beforeEach(async ({ page }) => {
    if (!RESET_URL) test.skip();
    await page.goto(RESET_URL);
    await expect(page.locator('#resetPass')).toBeVisible({ timeout: 10000 });
  });

  // TC021: Accept a new password not in last 5
  // NOTE: This test changes the account password. Ensure 'NewPass@999' is not in the last 5.
  test('TC021 - Accept new password not in last 5', async ({ page }) => {
    await page.locator('#resetPass').fill('NewPass@999');
    await page.locator('#resetCPass').fill('NewPass@999');
    await page.locator('#btnResetPassword').click();
    // On success: redirect away from /Account/Reset
    await page.waitForURL(url => !url.pathname.startsWith('/Account/Reset'), { timeout: 10000 })
      .catch(() => {
        return expect(page.locator('main ul li')).not.toBeVisible({ timeout: 3000 });
      });
  });

  // TC022: Reject 1st (most recent) previously used password
  test('TC022 - Reject most recently used password', async ({ page }) => {
    const recentPassword = process.env.TEST_PASSWORD || 'Pro@987';
    await page.locator('#resetPass').fill(recentPassword);
    await page.locator('#resetCPass').fill(recentPassword);
    await page.locator('#btnResetPassword').click();
    await expect(page.locator('main ul li').first()).toBeVisible({ timeout: 8000 });
    await expect(page.locator('main ul li').first()).not.toContainText('expired');
  });

  // TC023: Reject 5th previously used password (boundary of history window)
  // Precondition: account must have at least 5 previous passwords
  test('TC023 - Reject 5th previously used password', async ({ page }) => {
    // Use the 5th most recent password — update HISTORY_PASSWORD_5 in .env as needed
    const historyPassword = process.env.HISTORY_PASSWORD_5 || '';
    if (!historyPassword) test.skip();
    await page.locator('#resetPass').fill(historyPassword);
    await page.locator('#resetCPass').fill(historyPassword);
    await page.locator('#btnResetPassword').click();
    await expect(page.locator('main ul li').first()).toBeVisible({ timeout: 8000 });
    await expect(page.locator('main ul li').first()).not.toContainText('expired');
  });

  // TC024: Accept 6th previously used password (outside reuse window)
  // NOTE: This test changes the account password if accepted.
  test('TC024 - Accept 6th previously used password (outside history window)', async ({ page }) => {
    const oldPassword = process.env.HISTORY_PASSWORD_6 || '';
    if (!oldPassword) test.skip();
    await page.locator('#resetPass').fill(oldPassword);
    await page.locator('#resetCPass').fill(oldPassword);
    await page.locator('#btnResetPassword').click();
    await page.waitForURL(url => !url.pathname.startsWith('/Account/Reset'), { timeout: 10000 })
      .catch(() => {
        return expect(page.locator('main ul li')).not.toBeVisible({ timeout: 3000 });
      });
  });

});
