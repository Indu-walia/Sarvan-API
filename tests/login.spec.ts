import { test, expect, Page } from '@playwright/test';
import * as dotenv from 'dotenv';

dotenv.config();

const EMAIL = process.env.TEST_EMAIL || '';
const PASSWORD = process.env.TEST_PASSWORD || '';

test.describe('Login Page - Process9 Platform', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/Account\/Login/i);
  });

  // TC001 - Valid Login
  // NOTE: This test requires valid/active credentials in .env
  // Current credentials in Claude.md show "Invalid login credentials" — update .env with active credentials to run this test
  test('TC001 - Valid login should redirect to dashboard', async ({ page }) => {
    await page.getByRole('textbox', { name: 'Email' }).fill(EMAIL);
    await page.getByRole('textbox', { name: 'Password' }).fill(PASSWORD);
    await page.getByRole('button', { name: 'Log in' }).click();

    // After valid login, page should redirect away from login
    await expect(page).not.toHaveURL(/login/i, { timeout: 10000 });
  });

  // TC002 - Invalid Login
  test('TC002 - Invalid login should show error message', async ({ page }) => {
    await page.getByRole('textbox', { name: 'Email' }).fill(EMAIL);
    await page.getByRole('textbox', { name: 'Password' }).fill('WrongPassword123');
    await page.getByRole('button', { name: 'Log in' }).click();

    await expect(page.getByText('Invalid login credentials')).toBeVisible();
  });

  // TC003 - Empty Fields Validation
  test('TC003 - Empty fields should trigger validation on submit', async ({ page }) => {
    await page.getByRole('button', { name: 'Log in' }).click();

    // Browser HTML5 native validation prevents submit — email field gets focused
    const emailInput = page.getByRole('textbox', { name: 'Email' });
    await expect(emailInput).toBeFocused();

    // Page must remain on the login URL (form was not submitted)
    await expect(page).toHaveURL(/Account\/Login/i);
  });

  // TC004 - Forgot Password without email
  // Uses page.on('dialog') because alert() fires synchronously in onclick — must accept immediately to unblock the click
  test('TC004 - Forgot password without email shows alert', async ({ page }) => {
    let capturedMessage = '';
    page.on('dialog', async dialog => {
      capturedMessage = dialog.message();
      await dialog.accept();
    });
    await page.getByRole('link', { name: 'Forgot your password?' }).click();
    expect(capturedMessage).toBe('Please enter registered email id !!!');
  });

  // TC005 - Forgot Password with valid email
  test('TC005 - Forgot password with registered email sends reset link', async ({ page }) => {
    await page.getByRole('textbox', { name: 'Email' }).fill(EMAIL);

    const dialogPromise = page.waitForEvent('dialog');
    await page.getByRole('link', { name: 'Forgot your password?' }).click();

    const dialog = await dialogPromise;
    expect(dialog.message()).toBe(
      'If the email is registered, you will receive a password reset link'
    );
    await dialog.accept();
  });

});
