# Test Cases — Quality Level 6 & 7 (Smart Plus Threshold)

## Purpose

These test cases check that when a client asks for **Quality Level 7 (Smart Plus)**, the system correctly compares the translation score against the client's configured threshold, and:
- gives back the right quality level (7 or 6), and
- correctly decides whether the sentence should be sent to **MoxEdit** for a human to check, or not.

They also check that **Quality Level 6** always behaves the same way regardless of score.

## Background (for context)

- Every sentence sent for translation at Quality Level 7 is scored automatically.
- Each client ("Wave key") has a **threshold** value, set per language.
- If the score is at or above the threshold → the sentence is marked **QL7** and is **not** sent for human review.
- If the score is below the threshold → the sentence is marked **QL6** and **is** sent to MoxEdit for human review.
- A default threshold exists for every language; a client can override this default for their own key.

## Rule Being Tested

| Requested Quality | Score Result | Expected OutQual | Goes to MoxEdit? |
|---|---|---|---|
| 7 | Pass (score >= threshold) | 7 | No |
| 7 | Fail (score < threshold) | 6 | Yes |
| 6 | Pass | 6 | Yes |
| 6 | Fail | 6 | Yes |

Quality Level 6 always ends up at OutQual 6 and always goes to MoxEdit, no matter what the score is.

## Test Cases

### A. Requested Quality = 7

| TC ID | Scenario | Threshold | Actual Score | Expected OutQual | Expected MoxEdit Routing | Expected Result |
|---|---|---|---|---|---|---|
| TC-Q7-01 | Score comfortably above threshold | 90% | 95% | 7 | Not sent to MoxEdit | Pass |
| TC-Q7-02 | Score comfortably below threshold | 90% | 80% | 6 | Sent to MoxEdit | Pass (fallback correctly triggered) |
| TC-Q7-03 | Score exactly equal to threshold | 90% | 90% | 7 | Not sent to MoxEdit | Pass (boundary: equal counts as passing) |
| TC-Q7-04 | Score just one point below threshold | 90% | 89% | 6 | Sent to MoxEdit | Pass (boundary: just below counts as failing) |
| TC-Q7-05 | Threshold set to 99% (almost everything should go to MoxEdit) | 99% | 95% | 6 | Sent to MoxEdit | Pass |
| TC-Q7-06 | Threshold set to 99%, score is a near-perfect 99% or above | 99% | 99% | 7 | Not sent to MoxEdit | Pass |
| TC-Q7-07 | Threshold set to 0% (nothing should go to MoxEdit) | 0% | 1% | 7 | Not sent to MoxEdit | Pass |
| TC-Q7-08 | Threshold set to 0%, score is also 0% | 0% | 0% | 7 | Not sent to MoxEdit | Pass (boundary: equal to 0% threshold still passes) |
| TC-Q7-09 | Same sentence/language, different Wave key with a different (overridden) threshold | Key A: 90%, Key B: 70% | 80% | Key A → 6 (sent to MoxEdit); Key B → 7 (not sent to MoxEdit) | Differs by key | Pass (confirms per-key override works) |
| TC-Q7-10 | Client key has no override for a language → should fall back to the Default threshold | Default: 90% (no override for this key) | 85% | 6 | Sent to MoxEdit | Pass (confirms fallback to Default works) |
| TC-Q7-11 | Same language, different threshold per language for the same key | Hindi: 90%, Tamil: 80% | 85% | Hindi → 6 (sent to MoxEdit); Tamil → 7 (not sent to MoxEdit) | Differs by language | Pass (confirms per-language threshold works) |
| TC-Q7-12 | Threshold set to the maximum, 100% (Expected Score = 1) — a normal, realistic score will almost never be a perfect 100%, so this should send everything to MoxEdit | 100% | 95% | 6 | Sent to MoxEdit | Pass (confirms a 100% threshold behaves as "send everything for review") |
| TC-Q7-13 | Threshold set to the maximum, 100% (Expected Score = 1), and the score that comes back is also a perfect 100% | 100% | 100% | 7 | Not sent to MoxEdit | Pass (boundary: only a perfect score passes a 100% threshold) |

### B. Requested Quality = 6

| TC ID | Scenario | Actual Score | Expected OutQual | Expected MoxEdit Routing | Expected Result |
|---|---|---|---|---|---|
| TC-Q6-01 | High score | 95% | 6 | Sent to MoxEdit | Pass |
| TC-Q6-02 | Low score | 10% | 6 | Sent to MoxEdit | Pass |
| TC-Q6-03 | Score of exactly 0% | 0% | 6 | Sent to MoxEdit | Pass |
| TC-Q6-04 | Score of 100% | 100% | 6 | Sent to MoxEdit | Pass |
| TC-Q6-05 | Expected Score set to the maximum, 100% (Expected Score = 1), with a normal actual score below that | 90% | 6 | Sent to MoxEdit | Pass (confirms Expected Score has no bearing on QL6's outcome either) |

The point of the Quality Level 6 cases is simply to confirm that the score has **no effect** on the outcome — every single case should end up as OutQual 6, sent to MoxEdit.

## Notes for Testers

- "Threshold" here refers to the configured value for that specific language, under that specific Wave key's configuration (or the Default configuration, if the key has no override).
- "Score" is the value returned by the scoring API for that sentence.
- A sentence is only ever sent to MoxEdit when the final OutQual is 6.
