# Brandname MT Test Suite

Validates brand/entity-name preservation during machine translation — checks that
required names/values survive translation (`BrandName`/`Contains`) and that
forbidden characters don't leak into the output (`NotContains`), across 5
target languages: Hindi, Tamil, Malayalam, Telugu, Marathi.

## Quick start — adding a new data file

Drop your `.xlsx` file into this folder, then run:

```
python process_new_file.py <file1.xlsx> [file2.xlsx ...]
```

This does everything in one command:
1. Auto-detects the `Sno` / text / `Contains` / `NotContains` columns from the
   file's header row (see **Input file format** below).
2. Builds `<file>_LangWise.xlsx` — one row per (test case × language).
3. Runs the validation and saves `<file>_LangWise_Results_<timestamp>.xlsx`.

Pass as many files as you want in one command — each is processed fully
before moving to the next.

## Input file format

Your source file needs a header row with (in any column order):

| Header (case-insensitive) | Required | Meaning |
|---|---|---|
| contains `sno` | yes | Row/test-case number |
| `text`, `input text`, or contains `sentence`/`title` | yes | The English sentence to translate |
| exactly `contains` | yes | Comma-separated values that **must** survive translation → becomes `BrandName` |
| contains `not contains` | no | Comma-separated values that must **not** appear in the output |

If detection fails or is ambiguous, `process_new_file.py` prints the headers
it found instead of guessing — check your column names against the table
above.

## Re-running an existing `_LangWise.xlsx` file directly

If you've already generated a language-wise file (or hand-edited one to set
different `BrandName`/`NotContains` per language), skip the auto-detect step
and run the validator directly:

```
python validate_brandname.py <file>_LangWise.xlsx
```

With no argument, it defaults to `Brandnamedata.xlsx`.

## Output

Each results file has one sheet, **Results**, in this layout — one row per
(test case, language), grouped by test case:

`Sno | text | Language | BrandName | NotContains | output text | Result`

`Result` is `Pass` or `Fail (...)`, with the reason inline
(`Missing: X` for a dropped required name, `Found forbidden: X` for a
`NotContains` violation).

## Files in this folder

- `validate_brandname.py` — the validation engine (API calls + pass/fail logic)
- `process_new_file.py` — one-shot: auto-detect columns → build `_LangWise` → run validation
- `CLAUDE.md` — API endpoint/request-response documentation
- `*_LangWise.xlsx` — generated per-language input files (safe to hand-edit
  per-language `BrandName`/`NotContains` values before re-running)
- `*_Results_<timestamp>.xlsx` — generated output, one per run

## Switching environments (UAT / other domain)

`API_URL` at the top of `validate_brandname.py` controls which endpoint gets
hit. Known values used in this project:

- UAT: `https://bfluat.mox.net.in/translator/unified`
- Dev: `https://mtaz.mox.net.in/translator/unified`

Edit that line directly to point at a different environment.

## Gotchas

- **"Permission denied" on save**: the output (or source) `.xlsx` is open in
  Excel. Close it and re-run — the script does not overwrite a locked file
  silently, it warns and retries at the end.
- **502 / connection errors**: the UAT server occasionally has brief outages
  or local network blips. Re-running usually clears it; check a couple of the
  failing rows before assuming it's a real translation defect.
- **Symbols/digits in `Contains`** (e.g. `yd²`, `###`, model codes): these are
  checked as an exact literal match, not fuzzy-matched — a dropped/altered
  character (e.g. `yd²` → `YD2`, `°C` → `° C`) is a genuine fail, not a script bug.
- **Curly vs straight quotes**: only the literal curly/smart quote characters
  you list in `NotContains` are flagged; a straight-quote rendering of the
  same punctuation is accepted.
