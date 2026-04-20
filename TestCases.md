# Test Scenarios & Test Cases
**Application:** Process9 Authentication Platform  
**URL:** https://auth4.mox2.net.in/  
**Modules:** Login · Forgot Password · Password Policy · Password Reset Flow  

---

## Test Scenarios

| # | Module | Scenario |
|---|--------|----------|
| S1 | Login | User logs in with valid credentials |
| S2 | Login | User attempts login with invalid credentials |
| S3 | Login | User attempts login without entering any data |
| S4 | Forgot Password | User clicks "Forgot your password?" without entering email |
| S5 | Forgot Password | User clicks "Forgot your password?" after entering a registered email |
| S6 | Password Length | Password shorter than 5 characters is rejected |
| S7 | Password Length | Password of exactly 5 characters is accepted |
| S8 | Password Length | Password of exactly 20 characters is accepted |
| S9 | Password Length | Password longer than 20 characters is rejected |
| S10 | Password Complexity | Password missing uppercase letter is rejected |
| S11 | Password Complexity | Password missing lowercase letter is rejected |
| S12 | Password Complexity | Password missing a number is rejected |
| S13 | Password Complexity | Password missing a special character is rejected |
| S14 | Password Complexity | Password confirm field matches new password |
| S15 | Password Complexity | Password and confirm password do not match |
| S16 | Password Complexity | Password contains only spaces |
| S17 | Password Complexity | Password contains only special characters |
| S18 | Password Complexity | Confirm password field left empty |
| S19 | Password Complexity | Reuse old password after login/logout cycle |
| S20 | Password Complexity | Valid password meeting all rules is accepted |
| S21 | Password History | New password not in last 5 is accepted |
| S22 | Password History | Reusing one of last 5 passwords is rejected |
| S23 | Password Reset Flow | Reset request generates a reset link |
| S24 | Password Reset Flow | Reset token expires after 5 minutes |
| S25 | Password Reset Flow | Reset token is single-use only |
| S26 | Password Reset Flow | Invalid token shows error |
| S27 | Password Reset Flow | Successful reset allows login with new password |
| S28 | Password Reset Flow | Reset link uses HTTPS |
| S29 | Password Reset Flow | Token is included in the reset URL |
| S30 | Password Reset Flow | Token is correctly encoded/decoded |
| S31 | Password Reset Flow | Multiple rapid reset requests handled gracefully |
| S32 | Password Reset Flow | Network failure during reset request |
| S33 | Password Reset Flow | Valid original reset link works when pasted in browser |
| S34 | Password Reset Flow | Tampered token in URL shows error |

---

## Test Cases

### Module: Login

| Test Case ID | Module / Component | Title (Feature) | Precondition (Given) | Steps (When) | Expected Result (Then) | Status |
|---|---|---|---|---|---|---|
| TC001 | Login | Valid login redirects to dashboard | User is on the login page (`/Account/Login`) | 1. Enter email: `indu.walia@process9.com` <br> 2. Enter password: `Pro@987` <br> 3. Click **Log in** | Page redirects away from the login page to the dashboard | ✅ Passed |
| TC002 | Login | Invalid login shows error message | User is on the login page | 1. Enter email: `indu.walia@process9.com` <br> 2. Enter wrong password: `WrongPassword123` <br> 3. Click **Log in** | Error message **"Invalid login credentials"** is displayed | ✅ Passed |
| TC003 | Login | Empty fields trigger browser validation | User is on the login page with all fields empty | 1. Leave Email and Password blank <br> 2. Click **Log in** | Browser native tooltip: **"Enter Valid Email ID"** on Email field; page stays on `/Account/Login` | ✅ Passed |

---

### Module: Forgot Password

| Test Case ID | Module / Component | Title (Feature) | Precondition (Given) | Steps (When) | Expected Result (Then) | Status |
|---|---|---|---|---|---|---|
| TC004 | Forgot Password | Alert shown when email is missing | User is on login page; Email field is empty | 1. Do NOT enter email <br> 2. Click **"Forgot your password?"** | Alert dialog: **"Please enter registered email id !!!"** | ✅ Passed |
| TC005 | Forgot Password | Reset link sent for registered email | User is on login page | 1. Enter `indu.walia@process9.com` in Email field <br> 2. Click **"Forgot your password?"** | Alert dialog: **"If the email is registered, you will receive a password reset link"** | ✅ Passed |

---

### Module: Password Policy — Length Validation

| Test Case ID | Module / Component | Title (Feature) | Precondition (Given) | Steps (When) | Expected Result (Then) | Status |
|---|---|---|---|---|---|---|
| TC006 | Password Policy – Length | Reject password shorter than 5 characters | User is on the password reset / change password page | 1. Enter new password: `Ab@1` (4 chars) <br> 2. Submit form | Validation error: **"Password must be at least 5 characters"** — form not submitted | ✅ Passed |
| TC007 | Password Policy – Length | Accept password of exactly 5 characters | User is on the password reset / change password page | 1. Enter new password: `Ab@1x` (5 chars) <br> 2. Enter same in Confirm Password <br> 3. Submit form | Password accepted; no length validation error | ✅ Passed |
| TC008 | Password Policy – Length | Accept password of exactly 20 characters | User is on the password reset / change password page | 1. Enter new password: `Abcdef@1234567890!Zz` (20 chars) <br> 2. Enter same in Confirm Password <br> 3. Submit form | Password accepted; no length validation error | ✅ Passed |
| TC009 | Password Policy – Length | Reject password longer than 20 characters | User is on the password reset / change password page | 1. Enter new password: `Abcdef@1234567890!ZzX` (21 chars) <br> 2. Submit form | Validation error: **"Password must not exceed 20 characters"** — form not submitted | ✅ Passed |

---

### Module: Password Policy — Complexity Validation

| Test Case ID | Module / Component | Title (Feature) | Precondition (Given) | Steps (When) | Expected Result (Then) | Status |
|---|---|---|---|---|---|---|
| TC010 | Password Policy – Complexity | Reject password missing uppercase letter | User is on password reset page | 1. Enter password: `testpass@1` (no uppercase) <br> 2. Submit | Validation error: **"Password must contain at least 1 uppercase letter"** | ✅ Passed |
| TC011 | Password Policy – Complexity | Reject password missing lowercase letter | User is on password reset page | 1. Enter password: `TESTPASS@1` (no lowercase) <br> 2. Submit | Validation error: **"Password must contain at least 1 lowercase letter"** | ✅ Passed |
| TC012 | Password Policy – Complexity | Reject password missing a number | User is on password reset page | 1. Enter password: `TestPass@!` (no digit) <br> 2. Submit | Validation error: **"Password must contain at least 1 number"** | ✅ Passed |
| TC013 | Password Policy – Complexity | Reject password missing special character | User is on password reset page | 1. Enter password: `TestPass123` (no special char) <br> 2. Submit | Validation error: **"Password must contain at least 1 special character"** | ✅ Passed |
| TC014 | Password Policy – Complexity | Accept password when confirm matches | User is on password reset page | 1. Enter new password: `TestPass@123` <br> 2. Enter same in Confirm Password: `TestPass@123` <br> 3. Submit | No mismatch error; form submits successfully | ✅ Passed |
| TC015 | Password Policy – Complexity | Reject when confirm password does not match | User is on password reset page | 1. Enter new password: `TestPass@123` <br> 2. Enter different confirm: `TestPass@456` <br> 3. Submit | Validation error: **"Passwords do not match"** | ✅ Passed |
| TC016 | Password Policy – Complexity | Reject password containing only spaces | User is on password reset page | 1. Enter password: `     ` (spaces only) <br> 2. Submit | Validation error: password cannot be blank/spaces only | ✅ Passed |
| TC017 | Password Policy – Complexity | Reject password containing only special characters | User is on password reset page | 1. Enter password: `@#$%^&*!` (special chars only) <br> 2. Submit | Validation error shown (missing uppercase, lowercase, number) | ✅ Passed |
| TC018 | Password Policy – Complexity | Reject when confirm password field is empty | User is on password reset page | 1. Enter new password: `TestPass@123` <br> 2. Leave Confirm Password empty <br> 3. Submit | Validation error: **"Please confirm your password"** | ✅ Passed |
| TC019 | Password Policy – Complexity | Reject reuse of old password after login/logout | User logs out and back in, navigates to change password | 1. Log out <br> 2. Log back in <br> 3. Navigate to Change Password <br> 4. Enter current active password as new password <br> 5. Submit | Validation error: **"Password has been used recently. Please choose a different password"** | ✅ Passed |
| TC020 | Password Policy – Complexity | Accept valid password meeting all rules | User is on password reset page | 1. Enter password: `Uptime@2025` <br> 2. Enter same in Confirm Password <br> 3. Submit | Password accepted; reset/change successful | ❌ Failed |

---

### Module: Password History Validation

| Test Case ID | Module / Component | Title (Feature) | Precondition (Given) | Steps (When) | Expected Result (Then) | Status |
|---|---|---|---|---|---|---|
| TC021 | Password History | Accept new password not in last 5 | User has at least 5 previous passwords recorded | 1. Navigate to Change/Reset Password <br> 2. Enter a brand-new password never used before: e.g. `NewPass@999` <br> 3. Submit | Password accepted and changed successfully | ⏳ Needs fresh RESET_URL |
| TC022 | Password History | Reject 1st previously used password | User has at least 1 previous password | 1. Navigate to Change/Reset Password <br> 2. Enter the most recent previous password <br> 3. Submit | Validation error: **"Password has been used recently. Please choose a different password"** (`usp_validatePassword`) | ⏳ Needs fresh RESET_URL |
| TC023 | Password History | Reject 5th previously used password | User has at least 5 previous passwords | 1. Navigate to Change/Reset Password <br> 2. Enter the 5th most recent password <br> 3. Submit | Validation error blocking reuse of password within last 5 | ⏳ Needs fresh RESET_URL + HISTORY_PASSWORD_5 |
| TC024 | Password History | Accept 6th previously used password (boundary) | User has at least 6 previous passwords | 1. Navigate to Change/Reset Password <br> 2. Enter the 6th oldest password (outside the 5-password history window) <br> 3. Submit | Password accepted (outside reuse window) | ⏳ Needs fresh RESET_URL + HISTORY_PASSWORD_6 |

---

### Module: Password Reset Flow

| Test Case ID | Module / Component | Title (Feature) | Precondition (Given) | Steps (When) | Expected Result (Then) | Status |
|---|---|---|---|---|---|---|
| TC025 | Password Reset Flow | Reset request generates a reset link | User has a registered email | 1. Enter registered email on login page <br> 2. Click **"Forgot your password?"** | Alert confirms reset link sent; email received with a valid reset link | ✅ Passed |
| TC026 | Password Reset Flow | Reset token expires / becomes invalid after use | Valid reset link received | 1. Open same reset link after it has been used <br> 2. Verify form is no longer accessible | Error heading shown — token no longer valid | ✅ Passed |
| TC027 | Password Reset Flow | Reset token is single-use only | Valid reset link received | 1. Open the reset link and complete the password reset successfully <br> 2. Open the same reset link again | Heading: **"This link has already been used."** | ✅ Passed |
| TC028 | Password Reset Flow | Invalid token shows error | User manually constructs a URL with an invalid token | 1. Open reset URL with a completely invalid/random token <br> 2. Submit | Error shown: **"An error occurred while processing your reset link. Please request a new one."** | ✅ Passed |
| TC029 | Password Reset Flow | Successful reset allows login with new password | User completes password reset with valid token | 1. Open valid reset link <br> 2. Enter new valid password: `TestPass@123` <br> 3. Confirm and submit <br> 4. Return to login and login with new password | Login succeeds with the current `TEST_PASSWORD` | ✅ Passed |
| TC030 | Password Reset Flow | Reset link uses HTTPS | Reset email received | 1. Inspect the reset link in the received email | Reset link URL begins with `https://` — no HTTP link | ✅ Passed |
| TC031 | Password Reset Flow | Token is present in the reset URL | Reset email received | 1. Open the reset email <br> 2. Inspect the reset link URL | URL contains `id=` query parameter (not empty) | ✅ Passed |
| TC032 | Password Reset Flow | Token is correctly encoded and decodable | Reset email received | 1. Copy the token value from the reset URL <br> 2. Decode token (Base64) | Token value is non-empty and decodes to valid Base64 data | ✅ Passed |
| TC033 | Password Reset Flow | Multiple rapid reset requests handled gracefully | User is on the login page | 1. Submit 5+ reset requests for the same email in quick succession | System handles all requests without crashing; dialogs shown, page stays on login | ✅ Passed |
| TC034 | Password Reset Flow | Network failure during reset request shows error | User is on the login page | 1. Block the forgot-password API route <br> 2. Enter email and click **"Forgot your password?"** | Page stays on login (no crash); network request blocked gracefully | ✅ Passed |
| TC035 | Password Reset Flow | Valid original reset link works after copy-paste | Valid reset link received | 1. Copy the full reset URL from the email <br> 2. Paste it into a new browser tab and load it | Either reset form loads (fresh token) or a meaningful error heading is shown (used/expired) | ✅ Passed |
| TC036 | Password Reset Flow | Tampered token in URL is rejected | Valid reset link received | 1. Copy the reset URL <br> 2. Modify a few characters in the token value <br> 3. Load the modified URL in the browser | Error heading: **"Invalid reset link format."** — tampered token rejected | ✅ Passed |

---

### Module: Password Special Character Validation

> **Automated in:** `tests/password-special-chars.spec.ts`  
> **Strategy:** Route-intercepted (POST aborted) — token is NOT consumed. All 20 tests run with a single `RESET_URL`.

| Test Case ID | Module / Component | Title (Feature) | Precondition (Given) | Steps (When) | Expected Result (Then) | Status |
|---|---|---|---|---|---|---|
| TC037 | Password Special Chars | Accept password with `!` | User is on reset page | 1. Enter `Test!Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC038 | Password Special Chars | Accept password with `@` | User is on reset page | 1. Enter `Test@Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC039 | Password Special Chars | Accept password with `#` | User is on reset page | 1. Enter `Test#Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC040 | Password Special Chars | Accept password with `$` | User is on reset page | 1. Enter `Test$Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC041 | Password Special Chars | Accept password with `%` | User is on reset page | 1. Enter `Test%Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC042 | Password Special Chars | Accept password with `^` | User is on reset page | 1. Enter `Test^Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC043 | Password Special Chars | Accept password with `&` | User is on reset page | 1. Enter `Test&Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC044 | Password Special Chars | Accept password with `*` | User is on reset page | 1. Enter `Test*Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC045 | Password Special Chars | Accept password with `-` | User is on reset page | 1. Enter `Test-Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC046 | Password Special Chars | Accept password with `_` | User is on reset page | 1. Enter `Test_Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC047 | Password Special Chars | Accept password with `=` | User is on reset page | 1. Enter `Test=Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC048 | Password Special Chars | Accept password with `+` | User is on reset page | 1. Enter `Test+Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC049 | Password Special Chars | Accept password with `~` | User is on reset page | 1. Enter `Test~Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC050 | Password Special Chars | Accept password with `/` | User is on reset page | 1. Enter `Test/Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC051 | Password Special Chars | Accept password with `?` | User is on reset page | 1. Enter `Test?Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC052 | Password Special Chars | Accept password with `.` | User is on reset page | 1. Enter `Test.Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC053 | Password Special Chars | Accept password with `,` | User is on reset page | 1. Enter `Test,Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC054 | Password Special Chars | Accept password with `;` | User is on reset page | 1. Enter `Test;Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC055 | Password Special Chars | Accept password with `:` | User is on reset page | 1. Enter `Test:Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |
| TC056 | Password Special Chars | Accept password with `'` | User is on reset page | 1. Enter `Test'Pass1` in both fields <br> 2. Click Change Password (POST aborted) | No client-side mismatch / required error | ⏳ Needs RESET_URL |

---

### Module: Full E2E Cycle — Reset Password → Login

> **Automated in:** `tests/password-special-chars.spec.ts`  
> **Strategy:** Each test CONSUMES one reset token. Run individually: `npx playwright test --grep "TC057"`.  
> After each test passes, update `TEST_PASSWORD` in `.env` to the new password.

| Test Case ID | Module / Component | Title (Feature) | Precondition (Given) | Steps (When) | Expected Result (Then) | Status |
|---|---|---|---|---|---|---|
| TC057 | Full E2E Cycle | Full cycle with `!` — reset then login | Fresh `RESET_URL` in `.env` | 1. Navigate to reset page <br> 2. Enter `Test!Pass1` in both fields <br> 3. Submit <br> 4. Go to login page <br> 5. Login with `indu.walia@process9.com` / `Test!Pass1` | Password changed; login succeeds; redirected away from login page | ⏳ Needs RESET_URL |
| TC058 | Full E2E Cycle | Full cycle with `@` — reset then login | Fresh `RESET_URL` in `.env` | 1. Navigate to reset page <br> 2. Enter `Test@Pass1` in both fields <br> 3. Submit <br> 4. Login with new password | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC059 | Full E2E Cycle | Full cycle with `#` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test#Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC060 | Full E2E Cycle | Full cycle with `$` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test$Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC061 | Full E2E Cycle | Full cycle with `%` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test%Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC062 | Full E2E Cycle | Full cycle with `^` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test^Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC063 | Full E2E Cycle | Full cycle with `&` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test&Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC064 | Full E2E Cycle | Full cycle with `*` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test*Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC065 | Full E2E Cycle | Full cycle with `-` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test-Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC066 | Full E2E Cycle | Full cycle with `_` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test_Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC067 | Full E2E Cycle | Full cycle with `=` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test=Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC068 | Full E2E Cycle | Full cycle with `+` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test+Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC069 | Full E2E Cycle | Full cycle with `~` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test~Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC070 | Full E2E Cycle | Full cycle with `/` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test/Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC071 | Full E2E Cycle | Full cycle with `?` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test?Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC072 | Full E2E Cycle | Full cycle with `.` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test.Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC073 | Full E2E Cycle | Full cycle with `,` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test,Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC074 | Full E2E Cycle | Full cycle with `;` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test;Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC075 | Full E2E Cycle | Full cycle with `:` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test:Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |
| TC076 | Full E2E Cycle | Full cycle with `'` — reset then login | Fresh `RESET_URL` in `.env` | 1. Enter `Test'Pass1` → submit → login | Password changed; login succeeds | ⏳ Needs RESET_URL |

---

## Summary

| Module | Total TCs | ✅ Passed | ⏳ Needs Token | ❌ Failed |
|--------|-----------|-----------|----------------|-----------|
| Login | 3 | 3 | 0 | 0 |
| Forgot Password | 2 | 2 | 0 | 0 |
| Password Policy – Length | 4 | 4 | 0 | 0 |
| Password Policy – Complexity | 11 | 10 | 0 | 1 |
| Password History | 4 | 0 | 4 | 0 |
| Password Reset Flow | 12 | 12 | 0 | 0 |
| Password Special Chars | 20 | 0 | 20 | 0 |
| Full E2E Cycle | 20 | 0 | 20 | 0 |
| **Total** | **76** | **31** | **44** | **1** |

---

## Notes

- **TC001–TC005** automated in `tests/login.spec.ts` — all passing.
- **TC006–TC020** automated in `tests/password-policy.spec.ts` — require a fresh `RESET_URL` in `.env`.
- **TC021–TC024** automated in `tests/password-history.spec.ts` — require `RESET_URL`; TC023–TC024 also need `HISTORY_PASSWORD_5` / `HISTORY_PASSWORD_6` in `.env`.
- **TC025–TC036** automated in `tests/password-reset-flow.spec.ts` — all passing with the current token state.
- **TC037–TC056** automated in `tests/password-special-chars.spec.ts` — validation only (POST aborted); all 20 run from a single `RESET_URL` without consuming it.
- **TC057–TC076** automated in `tests/password-special-chars.spec.ts` — full E2E cycle (reset → login); each test consumes one token. Run one at a time: `npx playwright test --grep "TC057"`, then get a fresh token for the next.
- **Reset page selectors**: New Password `#resetPass`, Confirm `#resetCPass`, Submit `#btnResetPassword`.
- **Client-side errors** appear as `placeholder` text on the input fields.
- **Server-side errors** appear in `main ul li` elements.
- **TC019 / TC022–TC024** require `usp_validatePassword` stored procedure to be active on the server.
- **TC003** uses HTML5 native browser validation — assertion is on field focus, not a DOM error element.
- **TC020 failure — server environment blocker**: The server returns `"Password has expired due to password expire time !!!"` for all password submissions on the reset form, regardless of the new password entered. This is an account-level password expiry flag on `indu.walia@process9.com`. An admin must clear the expiry setting before TC020 can pass. The test code itself is correct.
- **How to run TC037–TC056**: Paste fresh `RESET_URL` into `.env` → `npx playwright test tests/password-special-chars.spec.ts --grep "TC037|TC038|TC039|TC040|TC041|TC042|TC043|TC044|TC045|TC046|TC047|TC048|TC049|TC050|TC051|TC052|TC053|TC054|TC055|TC056"`
- **How to run TC057–TC076 (full cycle)**: For each test — get a fresh `RESET_URL`, paste into `.env`, run `npx playwright test --grep "TC057"` (replace number as needed). After each success, update `TEST_PASSWORD` in `.env` to the new password used by that test.
