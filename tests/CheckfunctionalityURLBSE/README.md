# Check Functionality URL (BSE / Hindi page testing)

Tests a Hindi-language page's functionality (links, buttons/tabs, dropdown menus) and produces an
Excel report. Driven entirely by an input Excel file — change the URL there, re-run one command.

## Prerequisites

- Python 3.8+ with `openpyxl` installed: `pip install openpyxl`
- `playwright-cli` on PATH: `npm install -g @playwright/cli@latest`
- Google Chrome installed (the suite drives real Chrome, not headless Chromium)

## Step 1 — Set the URL(s) to test

Open `CheckfunctionalityURLBSEData.xlsx` and fill in/edit rows:

| Column | Meaning |
|---|---|
| Sno | Row number |
| Description | What this page is (for your reference) |
| Language | e.g. `Hindi` |
| EnglishURL | The English version of the page (for reference; not currently tested) |
| LanguageURL | **The URL that gets tested** — this is what the suite runs against |

Add more rows to test more pages in one run — the suite processes every row that has a `LanguageURL`.

## Step 2 — Run it

From the repo root (`d:\Sarvam API`):

```powershell
python tests/CheckfunctionalityURLBSE/run_suite.py
```

This does everything automatically, for each row:
1. Opens the URL in Chrome and checks every link on the page resolves (HTTP status check).
2. Clicks every button/tab/dropdown-toggle on the page, recording Pass/Fail/Warning + any new console errors.
3. Opens every top-nav dropdown menu (if present) and confirms it reveals real content.
4. Checks that internal links/navigations keep the language path segment (e.g. `/hindi`) rather than silently dropping into another language.
5. Builds an Excel report: `CheckfunctionalityURLBSE_Hindi_Results_<slug>.xlsx`, where `<slug>` is derived from the tested URL so different pages don't overwrite each other's reports.

A full run takes a few minutes per row (checking 400+ links is the slow part).

## Output

Open `CheckfunctionalityURLBSE_Hindi_Results_<slug>.xlsx`. Sheets:

| Sheet | Content |
|---|---|
| Summary | Headline counts |
| Links (urlwise) | Every link found, HTTP status, Pass/Fail |
| Functionality | Every button/tab tested — Status, Reason (if Fail/Warning), console issues, untranslated-text flag |
| Hindi Path Check | Whether internal links/navigations keep the language path segment |
| Dropdown Menus | Top-nav dropdown menus opened and verified |
| Console Error Samples | Distinct browser console errors seen during the run |

**Status colors:** green = Pass, red = Fail (confirmed defect), yellow = Warning (couldn't be
confirmed within the test's time budget — likely a slow-loading page, not a real break; worth a
quick manual spot-check, not a confirmed bug).

## If something looks off

- **Browser shows "Access Denied" / blocked**: the site has bot protection (Akamai). `.playwright/cli.config.json`
  (repo root) already disables Chromium's automation flag to get past this — make sure that file exists.
- **A row's probe returns all-zero counts**: the open→run-code handoff occasionally races and the
  page loads blank. Just re-run that row (re-run the whole script — already-completed rows are fast
  to redo since each row is independent).
- **Dropdown Menus sheet shows "N/A" for most rows**: that's expected on non-BSE pages — those 10
  specific dropdown checks (Equity/Derivatives/Debt/etc.) are BSE's top-nav menu items and won't
  exist on other sites. Not a failure.
- **Excel file save fails with a permission error**: the previous report is still open in Excel
  (including in the background — check Task Manager for a lingering `EXCEL.exe`). Close it and re-run.

## Files in this folder

| File | Purpose |
|---|---|
| `CheckfunctionalityURLBSEData.xlsx` | Input — edit this to choose what gets tested |
| `run_suite.py` | **Main entry point** — run this |
| `bse_functional_probe.js` | Playwright script: link health + button/tab/popup sweep (generic, works on any site) |
| `bse_dropdown_probe.js` | Playwright script: opens top-nav dropdown menus (BSE-specific item list, degrades gracefully elsewhere) |
| `extract_json.py` | Converts raw probe output into JSON for the report builder |
| `build_report.py` | Builds the Excel report from the JSON + dropdown results |
| `CheckfunctionalityURLBSE_Hindi_Results_*.xlsx` | Output reports (one per tested page) |
