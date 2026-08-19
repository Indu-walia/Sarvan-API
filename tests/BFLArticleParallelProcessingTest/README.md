# Article Bulk Upload — CLI Reference

This README lists the available commands and examples for managing Elasticsearch cleanup and submitting article JSON payloads using the repository tools. Commands are shown in the recommended order for a safe bulk upload workflow.

Prerequisites
- Python 3
- Dependencies: `requests`, `openpyxl` (see `requirements.txt`)

Files
- `submit_parallel.py` — main uploader and ES cleanup orchestrator
- `scripts/delete_indices_by_keys.py` — interactive index deletion helper
- `scripts/list_indices_by_keys.py` — list indices matching keys (non-destructive)
- `scripts/bump_versions.py` — bumps `articleVersion` in all 12 payload files to fresh, unique timestamps
- `scripts/bump_titles.py` — sets `articleTitle` to `"<articleId> <timestamp>"` in all 12 payload files, so uploaded articles are findable by name in the dashboard search (does not touch `articleVersion`)
- `scripts/set_language.py` — sets `translationLanguage` on all 12 payload files (defaults to `Hindi,Tamil,Malayalam,Telugu,Marathi,Kannada`)
- `scripts/loop_upload_4x.py` — repeats bump-version → upload → clear-ES N times in a row (defaults to 4 loops); non-interactive, no confirmation prompt

## Manual re-upload workflow (Command Prompt)

The real ES index naming pattern is `<key>_<language>` (e.g.
`7895-620f-fb0b-8853-0015-17c6-8b13-720a_hindi`) plus `clientbilling_<key>`.
`submit_parallel.py`'s built-in pre-clear only guesses a few exact names
(`<key>`, `articles-<key>`, ...) and will 404 on all of them — it never
matches the real indices. Use `scripts/delete_indices_by_keys.py` instead,
which matches by substring and finds them correctly.

Run these three steps in order, from the project folder, in Command Prompt:

```cmd
cd /d "d:\Sarvam API\tests\BFLArticleParallelProcessingTest"
```

**Step 1 — Clear ES** (lists matching indices, then asks you to type `YES` before deleting anything):
```cmd
python scripts\delete_indices_by_keys.py "http://20.192.26.81:9200" "929E-4237-1BE7-D479-F5D5-A39D-3B71-553C,7895-620F-FB0B-8853-0015-17C6-8B13-720A"
```

**Step 2 — Bump `articleVersion`** in all 12 payload files (avoids `409 already exists`):
```cmd
python scripts\bump_versions.py "Test data parallel processing"
```

**Step 3 — Upload the whole folder in parallel** (skip the built-in pre-clear since step 1 already handled it):
```cmd
python submit_parallel.py --input-dir "Test data parallel processing" --no-pre-clear --output-prefix "report_name"
```

Change `report_name` to whatever prefix you want for that run's `.xlsx` report.

### Multi-language upload

To request multiple translation languages in one go, set `translationLanguage`
before bumping/uploading:

```cmd
python scripts\set_language.py "Test data parallel processing" "Hindi,Tamil,Malayalam,Telugu,Marathi,Kannada"
python scripts\bump_versions.py "Test data parallel processing"
python submit_parallel.py --input-dir "Test data parallel processing" --no-pre-clear --output-prefix "report_multilang"
```

### Repeated upload loop

`scripts/loop_upload_4x.py` repeats bump → upload → clear-ES N times in a
row (default 4). It clears ES non-interactively (no `YES` prompt), so only
run it once you're comfortable with what it deletes — it targets the same
two project keys as `delete_indices_by_keys.py`. Reports are written as
`report_loop1.xlsx`, `report_loop2.xlsx`, etc.

```cmd
python scripts\loop_upload_4x.py "Test data parallel processing" 4
```

Note: translation is async, so if loops run faster than the translation
pipeline, the ES-clear step in later loops may find nothing new to delete
yet — that's expected, not a failure of the upload itself.

Recommended sequence (ordered)

1) Verify which indices match your keys (non-destructive)

```powershell
python scripts/list_indices_by_keys.py "http://<ES_HOST>:9200" "KEY1,KEY2"
```

2) (Optional) Delete indices interactively using helper

```powershell
python scripts/delete_indices_by_keys.py "http://<ES_HOST>:9200" "KEY1,KEY2"
```

3) Dry-run validation of payload files (no network requests) — produces only an Excel `.xlsx` report

```powershell
python submit_parallel.py --input-dir "Test data parallel processing" --dry-run --output-prefix "report_test"
```

4) Delete-only: run ES pre-clear (default) and delete documents, then exit

```powershell
python submit_parallel.py --input-dir "Test data parallel processing" --delete-only --delete-docs --es-url "http://<ES_HOST>:9200" --es-keys "KEY1,KEY2"
```

5) Full upload (pre-clear runs by default) — run ES cleanup then submit payloads. Produces `article_load_report.xlsx` by default.

```powershell
python submit_parallel.py --input-dir "Test data parallel processing" --output-prefix "report"
```

Upload only files for a specific department (one-by-one)

```powershell
python submit_parallel.py --input-dir "Test data parallel processing" --filter-dept "7895-620F-FB0B-8853-0015-17C6-8B13-720A" --sequential --output-prefix "report_anuvaad"
```

Upload only files by filename (case-insensitive substring match). Useful if you renamed files to include `anuvaad` or `mall`:

```powershell
python submit_parallel.py --input-dir "Test data parallel processing" --filter-name "anuvaad" --sequential --output-prefix "report_anuvaad"

python submit_parallel.py --input-dir "Test data parallel processing" --filter-name "mall" --sequential --output-prefix "report_mall"
```

6) Opt out of pre-clear (if you do NOT want automatic ES cleanup)

```powershell
python submit_parallel.py --input-dir "Test data parallel processing" --no-pre-clear --output-prefix "report"
```

7) Additional useful options
- `--url` : API endpoint (default `https://qa_article.mox2.net.in/Article`)
- `--api-key` : value for `X-API-KEY` header
- `--workers` : number of parallel threads (default 10)
- `--recursive` : recurse into subfolders to find payloads
- `--es-url` : Elasticsearch base URL (default `http://20.192.26.81:9200`)
- `--es-keys` : comma-separated list of keys used when clearing ES (default contains the two keys used in tests)
- `--delete-docs` : run `_delete_by_query` per index for the configured keys
- `--csv-file` : explicitly request CSV output (CSV is NOT written by default)

Example with all common flags

```powershell
python submit_parallel.py \
  --input-dir "Test data parallel processing" \
  --output-prefix "report" \
  --workers 20 \
  --recursive \
  --api-key "7895-620F-FB0B-8853-0015-17C6-8B13-720A" \
  --es-url "http://<ES_HOST>:9200" \
  --es-keys "KEY1,KEY2" \
  --delete-docs
```

Notes & safety
- Pre-clear (ES cleanup) runs by default. Use `--no-pre-clear` to skip it.
- CSV files are created only if `--csv-file` is supplied explicitly.
- Destructive commands (index deletion) may be interactive in the helper script; the main `submit_parallel.py` requires explicit flags for deletions.

Support
If you want the pre-clear behavior reverted to opt-in, or additional audit logging for ES deletions, open an issue or ask in the repo.
# BFL Article Parallel Processing

This script loads all JSON payload files from the `Test data parallel processing` folder and submits them concurrently to the article API endpoint.

## Files

- `submit_parallel.py` - Python script that finds JSON files in a folder, sends them in parallel, and writes an Excel report.
- `requirements.txt` - Python dependencies: `requests` and `openpyxl`.
- `Test data parallel processing/` - folder containing JSON payloads for both Anuvaad and Bajaj Mall.

## Setup

Install dependencies in your Python environment:

```bash
python -m pip install -r "d:/Sarvam API/tests/BFLArticleParallelProcessingTest/requirements.txt"
```

## Run

Run the script from the test folder or provide the folder path explicitly:

```bash
cd "d:/Sarvam API/tests/BFLArticleParallelProcessingTest"
python submit_parallel.py --input-dir "Test data parallel processing" --output-file "article_load_report.xlsx"
```

### Options

- `--input-dir` - Directory containing payload files. Defaults to `Test data parallel processing`.
- `--url` - API endpoint URL. Defaults to `https://qa_article.mox2.net.in/Article`.
- `--api-key` - Header `X-API-KEY` value. Defaults to the sample key.
- `--workers` - Number of parallel threads. Defaults to `10`.
- `--recursive` - Search subdirectories recursively.
-- `--output-prefix` - Output filename prefix for the Excel report. Defaults to `article_load_report`.
- `--output-file` - Excel report output file. Defaults to `<prefix>.xlsx`.
-- `--csv-file` - CSV report output file. Provide only if you want an additional CSV export (CSV is not created by default).
- `--dry-run` - Validate JSON payload files only and write a report without sending requests.
- `--clear-es` - Delete Elasticsearch indices that match the keys in `--es-keys` before submitting. Use with caution.
- `--es-url` - Elasticsearch base URL. Defaults to `http://20.192.26.81:9200`.
- `--es-keys` - Comma-separated list of keys (index names or identifiers) to clear/delete. Defaults to the two sample keys used in this project.
- `--delete-docs` - Run an Elasticsearch `_delete_by_query` using each key to remove matching documents across indices.

## Example

```bash
python submit_parallel.py --input-dir "Test data parallel processing" --workers 20 --output-prefix "report"
```

This creates `report.xlsx`.

### Elasticsearch cleanup (optional)

You can clear ES indices or delete documents that match the keys before submitting articles. These operations are destructive — double-check the `--es-keys` and `--es-url` values before running.

Examples:

Delete matching indices for the configured keys, then submit:

```bash
python submit_parallel.py --input-dir "Test data parallel processing" --clear-es --es-url "http://20.192.26.81:9200" --es-keys "929E-4237-1BE7-D479-F5D5-A39D-3B71-553C,7895-620F-FB0B-8853-0015-17C6-8B13-720A"
```

Run `_delete_by_query` to remove documents that contain the key across indices:

```bash
python submit_parallel.py --input-dir "Test data parallel processing" --delete-docs --es-url "http://20.192.26.81:9200" --es-keys "929E-4237-1BE7-D479-F5D5-A39D-3B71-553C"
```

Note: `--dry-run` skips network calls and only validates payload files; it does not perform ES deletions.

The script will produce an Excel report with one row per article file, including `status_code`, `elapsed_ms`, and a response preview.

### Troubleshooting: 409 "already exists"

If every file returns `409` with a body like `Article <id> (<version>) already exists in [<language>]`, the conflict is coming from the target article store's own dedup check on `articleId` + `articleVersion` + `translationLanguage` — it is **not** an Elasticsearch conflict, so `--clear-es` / `--delete-docs` / the default pre-clear will not fix it. The default pre-clear only guesses a handful of exact index names and always 404s; it never matches the real indices (see "Manual re-upload workflow" above).

To force a clean submission, use the 3-step manual workflow above (clear ES with `scripts/delete_indices_by_keys.py`, bump versions with `scripts/bump_versions.py`, then upload with `--no-pre-clear`).

### Troubleshooting: dashboard search finds nothing

The dashboard's Search box and "Article" column match against `articleTitle`,
not `articleId`. The sample test payloads carry unrelated real-world titles
(e.g. `"Usha Desert Air Coolers"`, `"Best Rado Watches..."`), so searching
for `anuvaad` or `mall` on the dashboard won't find them even after a
successful upload. Run `scripts/bump_titles.py` before uploading to set
`articleTitle` to `"<articleId> <timestamp>"` so the articles are searchable
by name.
Step1
python scripts\set_language.py "Test data parallel processing" "Hindi,Tamil,Malayalam,Telugu,Marathi,Kannada"
Step2
python scripts\bump_versions.py "Test data parallel processing"
step3
python submit_parallel.py --input-dir "Test data parallel processing" --no-pre-clear --output-prefix "report_multilang"
