# Session Summary — Parallel Article Upload (Anuvaad + Bajaj Mall)

## Goal
Submit all JSON payload files in `Test data parallel processing/` (6 Anuvaad + 6 bajajmall files) to the BFL Article API at once, in parallel.

## Bug found & fixed
`submit_parallel.py` had a result-recording bug in the parallel branch: the
code that builds each report row and appends it to `records` was indented
**outside** the `for future in as_completed(futures):` loop. All 12 requests
were still sent, but only the *last* completed result was ever written to the
Excel report / printed to console — the other 11 were silently dropped.

Fix: re-indented the record-building block back inside the `for` loop
([submit_parallel.py](submit_parallel.py#L362-L381)), so every completed
request now produces its own report row.

## Root cause of the 409 "already exists" errors
First two runs returned `409` on all 12 files, e.g.:
```
{"message":"Article Anuvaad (1786083404293) already exists in [Hindi]."}
```
Clearing Elasticsearch indices (`--es-keys` for both configured keys — both
404'd, nothing to delete) and clearing the client cache did **not** resolve
it. That's because the dedup check lives in a separate backend store, keyed
on `articleId` + `articleVersion` + `translationLanguage` — not in ES and not
in any client-side cache. The `articleVersion` field in the test files is an
epoch-millisecond timestamp left over from a prior run, so resubmitting the
same files always collides.

**Fix:** bumped `articleVersion` in all 12 payload files to fresh, unique
epoch-ms values before resubmitting. Result: **12/12 succeeded (200)**.

## Commands used

Run the full folder in parallel:
```powershell
cd "d:\Sarvam API\tests\BFLArticleParallelProcessingTest"
python submit_parallel.py --input-dir "Test data parallel processing" --output-prefix "report_name"
```

Only Anuvaad or only mall files, sequentially:
```powershell
python submit_parallel.py --input-dir "Test data parallel processing" --filter-name "anuvaad" --sequential --output-prefix "report_anuvaad"
python submit_parallel.py --input-dir "Test data parallel processing" --filter-name "mall" --sequential --output-prefix "report_mall"
```

Skip the ES pre-clear step:
```powershell
python submit_parallel.py --input-dir "Test data parallel processing" --output-prefix "report_name" --no-pre-clear
```

## Reports produced this session
| File | Result |
|---|---|
| `report_anuvaad_mall.xlsx` | 12/12 → 409 (stale articleVersion) |
| `report_anuvaad_mall_run2.xlsx` | 12/12 → 409 (ES + cache clear did not help — confirms root cause) |
| `report_anuvaad_mall_run3.xlsx` | 12/12 → **200 success**, after bumping articleVersion |

## Takeaway for next time
Before re-running the same payload files, bump `articleVersion` (and/or
`articleId`) to a value that hasn't been submitted before — ES/cache clearing
alone will not avoid a 409 on identical `articleId` + `articleVersion` +
language.
