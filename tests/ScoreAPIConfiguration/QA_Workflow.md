# QA Workflow — Score API Configuration Testing

## Objective
To check, for each client, language, and quality level, whether the system gives back the correct score and the correct quality level — and, when quality level 7 is requested, whether it correctly decides if the sentence should go to MoxEdit for human review or not.

## Step 1 — Get the Correct Expected Value First
Before checking anything, find out what the "correct" score is supposed to be for the language and quality level you're testing. This comes from the configuration that has been set up for that client — it is not something to guess or assume. If someone has recently changed a setting (for example, a client's threshold for a language), make sure you're using the updated value, not an old one.

## Step 2 — Test Each Case
For each language, quality level, and sentence you're testing:
1. Send the sentence for translation, asking for the specific quality level you want to test.
2. Note down what score comes back, and what quality level comes back.
3. Compare both of these to what you expected, using the rules below.

## Step 3 — How to Decide Pass or Fail

**Checking the Score:**
If the score that comes back is equal to or higher than the expected score, that part is a **Pass**. If it's lower, it's a **Fail**.

**Checking the Quality Level that comes back:**
The quality level you get back should match what's expected, based on whether the score check above passed or failed:

| Quality Level Requested | If Score Check Passed | If Score Check Failed |
|---|---|---|
| 7 | Expect quality level 7 | Expect quality level 6 |
| 6 | Expect quality level 6 | Expect quality level 6 |
| 1 | Expect quality level 1 | Expect quality level 4 |
| 2 | Expect quality level 2 | Expect quality level 4 |

In simple terms: if the score check passes, the system should give back the same quality level you asked for. If it fails, the system should "step down" — level 6 stays at 6, levels 1 and 2 drop to 4, and level 7 drops to 6.

**If quality level 7 was requested, also check MoxEdit routing:**
- Quality level came back as **7** → the sentence should **not** be sent to MoxEdit.
- Quality level came back as **6** → the sentence **should** be sent to MoxEdit for a person to review.

**Overall Result:**
Only mark the test case as a full **Pass** if both the score check and the quality-level check pass. If either one fails, mark it as a **Fail**.

## Step 3a — Edit Tool (MoxEdit) Scenarios to Walk Through

When testing quality level 7, don't just check one case — walk through these scenarios to make sure the Edit Tool routing decision is correct in every situation:

| # | Scenario | What Should Happen |
|---|---|---|
| 1 | Score comes back comfortably above the client's threshold | Quality level 7, **not** sent to Edit Tool |
| 2 | Score comes back comfortably below the threshold | Quality level 6, **sent** to Edit Tool |
| 3 | Score comes back exactly equal to the threshold | Quality level 7, **not** sent to Edit Tool (equal counts as passing) |
| 4 | Score comes back just barely below the threshold | Quality level 6, **sent** to Edit Tool (just below counts as failing) |
| 5 | Threshold is set very high (close to 100%) | Almost every sentence should end up going to the Edit Tool |
| 6 | Threshold is set very high, and the score is also very high (near-perfect) | That sentence should still come back as quality level 7 and skip the Edit Tool |
| 7 | Threshold is set very low (close to 0%) | Almost every sentence should skip the Edit Tool |
| 8 | Threshold is set to 0%, and the score is also 0% | Should still count as passing (0% score meets a 0% threshold) — skips the Edit Tool |
| 9 | Threshold is set to the absolute maximum (100%) | Only a perfect score would skip the Edit Tool; any normal score should be sent to the Edit Tool |
| 10 | Same sentence and language tested under two different clients, each with a different threshold | Each client's result should follow their own threshold — one may go to the Edit Tool while the other doesn't |
| 11 | A client hasn't set up their own threshold for a language | The system should fall back to the Default threshold for that language, and route accordingly |
| 12 | Same client, but two different languages with different thresholds | Each language's result should follow its own threshold, even for the same sentence |

The point of walking through all of these is to confirm that the Edit Tool routing isn't just working for one "easy" case, but is behaving correctly at every boundary, every extreme, and every override situation.

Quality level 6 needs a much simpler check: no matter what the score is, it should always come back as quality level 6 and always be sent to the Edit Tool. If you ever see a quality-level-6 case skip the Edit Tool, or come back as anything other than 6, that's a problem.

## Step 4 — What to Do When Something Fails
1. Double-check that you're comparing against the current, correct expected value — not an outdated one. If the configuration was changed recently, get the latest value and re-check before treating it as a real problem.
2. If the score is only a little bit lower than expected, check whether this is a genuine issue or just a very close boundary case.
3. If the quality level that comes back doesn't make sense at all (for example, a number that isn't a valid quality level), treat it as suspicious and re-test that same case again on its own before reporting it as a defect — sometimes a single check can behave oddly and give a one-off wrong answer.

## Step 5 — Re-test After Any Configuration Change
Whenever a client's configuration is changed (for example, their threshold for a language is updated), make sure to update the expected value you're comparing against, and test that case again — don't rely on results from before the change.

## Things to Keep in Mind
- Not every quality level behaves the same way for every client. For some clients, a quality level that's "supposed to" always give a score of zero doesn't actually do so — so always compare the score directly against what's expected, rather than assuming certain quality levels are a special case.
- A quality level of 5 (or any number outside 1, 2, 3, 4, 6, 7) is never a valid answer — if you ever see that, it's a sign something went wrong with that particular check, not a real result.

## Quick Reference — What We're Testing

| Client Setup | What It Represents |
|---|---|
| Client | This client's own configuration |
| BFL | BFL's own configuration |
| Default | The fallback configuration used when a client hasn't set up their own |

Languages covered: Assamese, Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi, Oriya, Punjabi, Tamil, Telugu, Urdu
Quality levels covered: 1, 2, 3, 4, 6, 7 (for the Default setup); 1, 2, 6, 7 (for Client/BFL setups)

## Related Docs
- `BRD.md` / `BRD.docx` — full background and reasoning behind these rules
- `TestCases_QL6_QL7.md` / `TestCases_QL6_QL7.xlsx` — detailed, scenario-by-scenario test cases for quality levels 6 and 7
