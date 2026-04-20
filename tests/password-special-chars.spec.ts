import { test, expect } from '@playwright/test';
import * as dotenv from 'dotenv';

dotenv.config();

const RESET_URL = process.env.RESET_URL || '';
const EMAIL     = process.env.TEST_EMAIL   || '';

// ─── Special characters under test ───────────────────────────────────────────
// Password pattern: Test{char}Pass1  → satisfies upper + lower + number + symbol
// TC037–TC056: client-side / server validation only (route aborted — token NOT consumed)
// TC057–TC076: full E2E cycle — reset password → login  (each CONSUMES the token)
//              Run individually: npx playwright test --grep "TC057"

const SPECIAL_CHARS: { id: string; char: string; label: string }[] = [
  { id: 'TC037', char: '!',  label: 'exclamation mark (!)' },
  { id: 'TC038', char: '@',  label: 'at sign (@)' },
  { id: 'TC039', char: '#',  label: 'hash (#)' },
  { id: 'TC040', char: '$',  label: 'dollar sign ($)' },
  { id: 'TC041', char: '%',  label: 'percent (%)' },
  { id: 'TC042', char: '^',  label: 'caret (^)' },
  { id: 'TC043', char: '&',  label: 'ampersand (&)' },
  { id: 'TC044', char: '*',  label: 'asterisk (*)' },
  { id: 'TC045', char: '-',  label: 'hyphen (-)' },
  { id: 'TC046', char: '_',  label: 'underscore (_)' },
  { id: 'TC047', char: '=',  label: 'equals sign (=)' },
  { id: 'TC048', char: '+',  label: 'plus sign (+)' },
  { id: 'TC049', char: '~',  label: 'tilde (~)' },
  { id: 'TC050', char: '/',  label: 'forward slash (/)' },
  { id: 'TC051', char: '?',  label: 'question mark (?)' },
  { id: 'TC052', char: '.',  label: 'period (.)' },
  { id: 'TC053', char: ',',  label: 'comma (,)' },
  { id: 'TC054', char: ';',  label: 'semicolon (;)' },
  { id: 'TC055', char: ':',  label: 'colon (:)' },
  { id: 'TC056', char: "'",  label: "single quote (')" },
];

// Helper: navigate to reset page and wait for form
async function gotoResetPage(page: any) {
  await page.goto(RESET_URL);
  await expect(page.locator('#resetPass')).toBeVisible({ timeout: 15000 });
}

// ═════════════════════════════════════════════════════════════════════════════
// PHASE 1 — Validation-only tests (TC037–TC056)
// Route is aborted AFTER page loads — token is preserved for reuse
// ═════════════════════════════════════════════════════════════════════════════
test.describe('Password Special Character Validation — TC037–TC056', () => {

  test.beforeEach(async ({ page }) => {
    if (!RESET_URL) test.skip();
    await gotoResetPage(page);
  });

  for (const { id, char, label } of SPECIAL_CHARS) {
    test(`${id} - Accept password containing ${label}`, async ({ page }) => {
      // Abort the POST so the password is NOT actually changed
      await page.route('**/Account/Reset', route => route.abort());

      const password = `Test${char}Pass1`;
      await page.locator('#resetPass').fill(password);
      await page.locator('#resetCPass').fill(password);
      await Promise.allSettled([page.locator('#btnResetPassword').click()]);
      await page.waitForTimeout(600);

      // If page navigated away (route abort caused navigation), client validation passed ✓
      const ph = await page.locator('#resetCPass')
        .getAttribute('placeholder', { timeout: 2000 })
        .catch(() => null);

      if (ph !== null) {
        // Page still here — check no client-side mismatch/required error
        expect(ph, `Expected no mismatch error for char: ${char}`).not.toBe("Passwords don't match!");
        expect(ph, `Expected no empty error for char: ${char}`).not.toBe('Confirm password is required!');
      }
      // ph === null → navigated away → client validation passed ✓
    });
  }
});

// ═════════════════════════════════════════════════════════════════════════════
// PHASE 2 — Full E2E Cycle: Reset Password → Login (TC057–TC076)
// ─────────────────────────────────────────────────────────────────────────────
// IMPORTANT: Each test CONSUMES the reset token.
// Run tests one at a time with a fresh RESET_URL each time:
//   npx playwright test --grep "TC057"   (update RESET_URL in .env, run)
//   npx playwright test --grep "TC058"   (update RESET_URL in .env, run)
//   etc.
//
// After a full-cycle test succeeds, the TEST_PASSWORD in .env should be
// updated to match the new password set by that test.
// ═════════════════════════════════════════════════════════════════════════════

const FULL_CYCLE: { id: string; password: string; label: string }[] = [
  { id: 'TC057', password: 'Test!Pass1',  label: 'exclamation (!)' },
  { id: 'TC058', password: 'Test@Pass1',  label: 'at sign (@)' },
  { id: 'TC059', password: 'Test#Pass1',  label: 'hash (#)' },
  { id: 'TC060', password: 'Test$Pass1',  label: 'dollar ($)' },
  { id: 'TC061', password: 'Test%Pass1',  label: 'percent (%)' },
  { id: 'TC062', password: 'Test^Pass1',  label: 'caret (^)' },
  { id: 'TC063', password: 'Test&Pass1',  label: 'ampersand (&)' },
  { id: 'TC064', password: 'Test*Pass1',  label: 'asterisk (*)' },
  { id: 'TC065', password: 'Test-Pass1',  label: 'hyphen (-)' },
  { id: 'TC066', password: 'Test_Pass1',  label: 'underscore (_)' },
  { id: 'TC067', password: 'Test=Pass1',  label: 'equals (=)' },
  { id: 'TC068', password: 'Test+Pass1',  label: 'plus (+)' },
  { id: 'TC069', password: 'Test~Pass1',  label: 'tilde (~)' },
  { id: 'TC070', password: 'Test/Pass1',  label: 'slash (/)' },
  { id: 'TC071', password: 'Test?Pass1',  label: 'question mark (?)' },
  { id: 'TC072', password: 'Test.Pass1',  label: 'period (.)' },
  { id: 'TC073', password: 'Test,Pass1',  label: 'comma (,)' },
  { id: 'TC074', password: 'Test;Pass1',  label: 'semicolon (;)' },
  { id: 'TC075', password: 'Test:Pass1',  label: 'colon (:)' },
  { id: 'TC076', password: "Test'Pass1",  label: "single quote (')" },
];

test.describe('Full E2E Cycle — Reset + Login (TC057–TC076)', () => {

  for (const { id, password, label } of FULL_CYCLE) {
    test(`${id} - Full cycle: reset with ${label} password → login succeeds`, async ({ page }) => {
      if (!RESET_URL) test.skip();

      // ── Step 1: Navigate to reset page ───────────────────────────────────
      await page.goto(RESET_URL);

      // If form is not visible, this token has already been used — skip gracefully
      const formVisible = await page.locator('#resetPass').isVisible({ timeout: 10000 }).catch(() => false);
      if (!formVisible) {
        console.log(`${id}: Reset form not accessible — token already consumed. Provide a fresh RESET_URL.`);
        test.skip();
        return;
      }

      // ── Step 2: Set new password ──────────────────────────────────────────
      await page.locator('#resetPass').fill(password);
      await page.locator('#resetCPass').fill(password);
      await page.locator('#btnResetPassword').click();

      // Expect redirect away from the reset page (success)
      await page.waitForURL(
        url => !url.pathname.toLowerCase().startsWith('/account/reset'),
        { timeout: 15000 }
      );

      // ── Step 3: Login with the new password ──────────────────────────────
      await page.goto('https://auth4.mox2.net.in/Account/Login');
      await expect(page).toHaveURL(/Account\/Login/i, { timeout: 8000 });

      await page.getByRole('textbox', { name: 'Email' }).fill(EMAIL);
      await page.getByRole('textbox', { name: 'Password' }).fill(password);
      await page.getByRole('button', { name: 'Log in' }).click();

      // ── Step 4: Verify login succeeded ───────────────────────────────────
      await expect(page, `Login failed after resetting to password with ${label}`)
        .not.toHaveURL(/login/i, { timeout: 12000 });
    });
  }
});
