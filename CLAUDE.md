Title: Process9 Authentication Platform — Test Automation

Description:
Automated test suite for the Process9 Authentication Platform covering login, forgot password,
password policy validation, password history, password reset flow, special character acceptance,
and full end-to-end reset → login cycles.

Application URL:
https://auth4.mox2.net.in/

Test Credentials:
Email: "indu.walia@process9.com"
Password: "Pro@987"

---

Modules Covered:
- Login (TC001–TC003)
- Forgot Password (TC004–TC005)
- Password Policy – Length Validation (TC006–TC009)
- Password Policy – Complexity Validation (TC010–TC020)
- Password History Validation (TC021–TC024)
- Password Reset Flow (TC025–TC036)
- Password Special Character Validation (TC037–TC056)
- Full E2E Cycle: Reset Password → Login (TC057–TC076)

---

Acceptance Criteria:
- Valid login should redirect to dashboard
- Invalid login should show error message "Invalid login credentials"
- Empty fields should show browser validation "Enter Valid Email ID"
- Forgot password with no email shows alert "Please enter registered email id !!!"
- Forgot password with registered email shows "If the email is registered, you will receive a password reset link"
- Password must be minimum 5 characters
- Password must not exceed 20 characters
- Password must contain uppercase, lowercase, number, and special character
- Password confirm field must match new password
- Spaces-only password must be rejected
- Password must not be reused from last 5 passwords
- Reset token must be single-use and expire after use
- Reset link must use HTTPS
- Tampered reset token must show error
- All 20 special characters (! @ # $ % ^ & * - _ = + ~ / ? . , ; : ') must be accepted in passwords
- Full cycle: reset password via link → login with new password must succeed

---

Test Files:
- tests/login.spec.ts              — TC001–TC005
- tests/password-policy.spec.ts    — TC006–TC020 (requires fresh RESET_URL in .env)
- tests/password-history.spec.ts   — TC021–TC024 (requires RESET_URL + HISTORY_PASSWORD_5/6 in .env)
- tests/password-reset-flow.spec.ts — TC025–TC036
- tests/password-special-chars.spec.ts — TC037–TC076

---

Environment Variables (.env):
- TEST_EMAIL     — login email
- TEST_PASSWORD  — current account password (update after each full-cycle test)
- RESET_URL      — full reset link from email (paste fresh link before running TC006–TC076)
- HISTORY_PASSWORD_5 — 5th most recent password (for TC023)
- HISTORY_PASSWORD_6 — 6th most recent password (for TC024)

---

Reset Page Selectors:
- New Password field:     #resetPass
- Confirm Password field: #resetCPass
- Submit button:          #btnResetPassword

Error Locations:
- Client-side errors: placeholder attribute on #resetCPass
- Server-side errors: main ul li elements

---

How to Run:
# All tests
npx playwright test --reporter=html && npx playwright show-report

# Specific test file
npx playwright test tests/login.spec.ts --reporter=html

# Specific test case
npx playwright test --grep "TC057 - Full cycle: reset with exclamation"

# Special char validation only (non-destructive, single token)
npx playwright test tests/password-special-chars.spec.ts --grep "TC037|TC038|TC039|TC040|TC041|TC042|TC043|TC044|TC045|TC046|TC047|TC048|TC049|TC050|TC051|TC052|TC053|TC054|TC055|TC056"

# Full cycle tests (one at a time, each needs fresh RESET_URL)
npx playwright test --grep "TC057 - Full cycle: reset with exclamation"

---

Known Blockers:
- TC020 and TC057–TC076 fail with "Password has expired due to password expire time !!!"
  This is a server-side account-level flag on indu.walia@process9.com.
  Admin must clear the PasswordExpired flag in the database before these tests can pass.
  The test code itself is correct — verify fix by manually changing password in browser first.

- TC021–TC024 are pending — require a fresh RESET_URL and known history passwords.

---

Token Instructions:
1. Go to https://auth4.mox2.net.in/
2. Enter email: indu.walia@process9.com
3. Click "Forgot your password?"
4. Open the reset email and copy the full reset link
5. Paste into .env as: RESET_URL=<full link>
6. Run tests immediately (token is single-use)

After a full-cycle test (TC057–TC076) passes, update TEST_PASSWORD in .env to the new password used by that test.
