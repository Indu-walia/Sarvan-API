# Business Requirements Document — Score API Configuration Testing

## 1. What is this about?

Whenever a piece of text is translated, our system also runs a "quality check" on it and gives back:
- a **score** (how good the translation is)
- a **quality level** (called "OutQual") that reflects how good the translation turned out to be

This document explains what we are testing, why, and how we decide whether a result is correct or not.

## 2. What are we testing?

We have three different client setups (we call them "keys"):

| Setup Name | Key |
|---|---|
| Client | 85BE-52EC-6E0A-52F2-8F17-E377-3FFC-722F |
| BFL | 2DAC-DC08-8B5F-50D3-341E-A4FE-2728-7CDB |
| Default | F08C-22B9-5A7E-974F-74E3-3A6F-8316-F33E |

For each setup, we test:
- 12 languages (Assamese, Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi, Oriya, Punjabi, Tamil, Telugu, Urdu)
- Different quality levels that can be requested (1, 2, 3, 4, 6, 7)
- A set of real, everyday sentences (loan messages, insurance messages, banking messages, etc.), not just one sample sentence

## 2a. Background: Smart Plus (Quality Level 7) and MoxEdit

Process9 launched a new translation quality option called **Smart Plus (Quality Level 7)**. Here's how it works:

- Every sentence sent for translation at Quality Level 7 is automatically scored.
- Each client has a **threshold** value (a percentage) set for each language.
- If the sentence's score is **at or above** the threshold, it is marked **Quality Level 7** and goes straight through — no human needs to look at it.
- If the sentence's score is **below** the threshold, it is marked **Quality Level 6** and is sent to **MoxEdit**, where a person reviews and corrects it.
- A **default threshold** exists for every language. Each client's setup will use this default unless the client has their own override value set up for that language.

This threshold is what lets us control how much content gets human review versus going straight through:
- Setting the threshold very high (close to 100%) means almost everything gets sent to a person for review.
- Setting the threshold very low (close to 0%) means almost nothing gets sent to a person — nearly everything goes straight through.

**Quality Level 6**, on the other hand, always goes to MoxEdit for review, no matter what the score is — there's no threshold decision involved for it.

Because of this, whenever we test Quality Level 7, we are really testing two things together:
1. Did the system return the right quality level (7 or 6) based on the score and threshold?
2. Did the sentence get routed correctly — straight through (QL7) or to MoxEdit for review (QL6)?

A full, detailed set of test cases for this Quality Level 6 / 7 behaviour (including threshold edge cases, per-client and per-language overrides, and what happens when the threshold is set to the extremes of 0% or 100%) is kept separately in `TestCases_QL6_QL7.md` and `TestCases_QL6_QL7.xlsx`, in this same folder.

## 3. Where do we get the "correct" answer from?

The "correct" score for each language and quality level comes directly from our own configuration database (the table where we set up these rules). It is **not** something we guess or calculate — it is whatever value is currently saved in that configuration for that client setup, language, and quality level.

This means: if someone changes a value in the configuration database, the "correct" answer in our test sheet also needs to be updated to match, otherwise the test will compare against an outdated number.

For Quality Level 7 specifically, this "correct" score is the client's **threshold** for that language (see §2a). If a client hasn't set up their own threshold for a language, the test should expect the **Default** threshold for that language instead — so part of what we're checking is also that this fallback-to-Default behaviour works correctly, not just the pass/fail comparison itself.

## 4. How do we decide Pass or Fail?

**Checking the Score:**
We compare the score the system actually gave us to the score we expected (from the configuration). If the actual score is equal to or higher than the expected score, it's a **Pass**. If it's lower, it's a **Fail**.

**Checking the Quality Level (OutQual):**
We expect the quality level that comes back to match the quality level we asked for. For example, if we asked for quality level 2, we expect to get quality level 2 back. If we get something else, that's a **Fail**.

**The full rule for what quality level we should expect back:**

Depending on which quality level was requested, and whether the score check above passed or failed, here is what we expect the returned quality level to be:

- If quality level **7** was requested:
  - and the score check **passed** → we expect the quality level back to be **7**
  - and the score check **failed** → we expect the quality level back to be **6**
- If quality level **6** was requested:
  - and the score check **passed** → we expect the quality level back to be **6**
  - and the score check **failed** → we expect the quality level back to be **6**
- If quality level **1** was requested:
  - and the score check **passed** → we expect the quality level back to be **1**
  - and the score check **failed** → we expect the quality level back to be **4**
- If quality level **2** was requested:
  - and the score check **passed** → we expect the quality level back to be **2**
  - and the score check **failed** → we expect the quality level back to be **4**

In plain terms: when the score check passes, the system should give back the same quality level that was asked for. When the score check fails, the system is expected to "step down" to a lower quality level instead — level 6 falls back to itself, levels 1 and 2 fall back to level 4, and level 7 falls back to level 6.

**Special case — when the expected score is set to the maximum (100%):**
Sometimes a threshold is deliberately configured at the maximum possible value (100%). In that case, only a perfect, flawless score will pass the score check — any normal, realistic score will fail it. This is an intentional configuration choice (it's how you'd set things up if you wanted virtually everything sent for human review), not a bug, so the test should still expect the usual fallback behaviour described above: quality level 7 requested with a 100% threshold and a less-than-perfect score should come back as quality level 6.

**How this ties into MoxEdit (for Quality Level 7 specifically):**
- Coming back as quality level **7** means the sentence is **not** sent to MoxEdit — it goes straight through.
- Coming back as quality level **6** (whether it was requested as 6, or it was requested as 7 but the score check failed) means the sentence **is** sent to MoxEdit for a person to review.

**Overall Result:**
A row only counts as a full **Pass** if both the score check and the quality-level check pass. If either one fails, the overall result is a **Fail**.

## 5. What information do we record for each test?

For every test we run, we keep track of:
- The language and quality level we asked for
- The sentence we tested
- What score we expected, and what score we actually got
- What quality level we expected, and what quality level we actually got
- Whether the score matched (Pass/Fail)
- Whether the quality level matched (Pass/Fail)
- The final overall result (Pass/Fail)

## 6. Problems we ran into and fixed along the way

- **Occasional errors at the very start of a test run:** When we fired off many requests at the exact same time, a few of the very first ones would fail with an error. Running those same few again by themselves always worked fine — so this was just a timing hiccup, not a real problem with the data.

- **Bad results when running too many tests too quickly:** When we ran a very large number of tests back-to-back very quickly, the system started sending back a clearly wrong "quality level" (a value that isn't even a valid option) for a lot of the later tests. This looked like the system getting overloaded rather than a real answer. Once we slowed down the testing pace, this problem went away completely and every result came back clean.

- **Some quality levels don't always give a score of zero:** We originally assumed that certain quality levels never produce a real score (they should always come back as zero). In practice, that turned out to only be true for the "Default" setup — the "Client" and "BFL" setups often do return a real score even for those same quality levels. Because of this, we now simply compare the actual score to the expected score directly, the same way, for every quality level, rather than treating some quality levels as a special case.

## 7. How the testing is run

- We use an automated script that reads all the test sentences, sends them to the system one by one (a few at a time, with small pauses in between to avoid overloading the system), and records the results in a spreadsheet.
- Each time the tests are run, a fresh results file is saved with the date and time in its name, so previous results are never overwritten.
- If a row doesn't have an expected score to compare against, it's marked as "not applicable" instead of Pass or Fail.

## 8. Related Documents

- `TestCases_QL6_QL7.md` / `TestCases_QL6_QL7.xlsx` — detailed, scenario-by-scenario test cases for Quality Level 6 and 7, including threshold boundaries, the 0%/100% extremes, per-client and per-language overrides, and the fallback-to-Default case.

## 9. Still open / needs a decision

For the **Client** setup, **Telugu**, **quality level 7**: the system is coming back with a score of 0, but we now expect a score of 1 in that case, so it always shows as a Fail. We need to confirm whether this is a real problem with the translation quality system, or whether the expected value itself needs to be adjusted.
