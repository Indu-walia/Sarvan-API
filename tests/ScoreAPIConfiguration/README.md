# ScoreAPIConfiguration

Automated validation tests for the Score API Configuration endpoint.

## Structure

| File | Description |
|---|---|
| `ScoreAPIConfigurationData.xlsx` | Test input data and expected values |
| `validate_score.py` | Automation script — calls the API and writes results |
| `CLAUDE.md` | API endpoint, key, and response field reference |

## How to Run

The script resolves its data file relative to its own location, so it can be run from either the repo root or this folder:

```bash
# from the Sarvam API repo root
python tests/ScoreAPIConfiguration/validate_score.py

# or from inside this folder
cd tests/ScoreAPIConfiguration
python validate_score.py
```

Results are saved as `ScoreAPIConfigurationData_Results_<timestamp>.xlsx` next to the script. The script calls the API concurrently (8 workers) and checkpoints the results file every 1000 rows, so a partial run still leaves usable output.

Rows with no `Expected Score` (e.g. bulk/observational text with no known ground truth) are scored as `N/A` instead of `Pass`/`Fail`.
