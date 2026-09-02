# Client Cache Load Test

Validates the client Translation Memory (TM) cache under load by running repeated `GetGridRecords` lookups against known cached segments, and confirms the correct `Target_text` is returned consistently.

## Endpoint

- **URL:** `https://clienttm.moxwave.com/moxlocalization/moxtm/GetGridRecords`
- **Method:** POST (JSON)
- **Language:** Hindi
- **Quality:** 6

## Requirements

```
pip install requests openpyxl
```

## Input

`CCSearchloadtest.xlsx` — column A (from row 2 onward) contains the English source text to search for in the TM cache.

## Run

```
python validate_cache_search.py
```

## Output

For each row, the script appends these columns to the input sheet:

| Column | Description |
|---|---|
| `Searched` | `Yes` if a cache match was found, `No` otherwise (green/red highlighted) |
| `TimeTaken_ms` | API response time in milliseconds |
| `MatchCount` | Number of matching records (`total` from the API response) |
| `Target_text` | Cached translation returned for the first match |

Results are saved to a timestamped file: `CCSearchloadtest_Results_<YYYYMMDD>_<HHMMSS>.xlsx`
