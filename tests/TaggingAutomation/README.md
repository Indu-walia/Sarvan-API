# Tagging Automation Validator

Automated test runner that validates HTML/tag preservation in the P9 AuthWave reprocess-log API. It reads test cases from an Excel workbook, calls the API for each row, compares actual tagging output against expected values, and writes colour-coded Pass/Fail results to a timestamped output file.

## Prerequisites

Python 3.8+ with the following packages:

```
pip install requests openpyxl
```

## Input file

Place `TaggingAutomationData.xlsx` in the same directory as the script before running. The workbook must have these columns (in order):

| Column | Header | Description |
|--------|--------|-------------|
| A | Sno | Row number / identifier |
| B | SourceText | English source text sent to the API |
| C | InIntgtText | Expected tags in the translated (target) text |
| D | InSrcText | Expected tags preserved in the source text |
| E | InoutputText | Expected token output values (comma- or pipe-separated) |
| F | NotContains | Values that must NOT appear (or `#{...}#` placeholders that MUST be preserved) in the final outputText |

## Running

The script must be run from inside the `TaggingAutomation` folder because it looks for `TaggingAutomationData.xlsx` in the current working directory.

**Windows (PowerShell / Command Prompt):**

```powershell
cd "tests\TaggingAutomation"
python validate_tagging.py
```

**From the repo root in one line:**

```powershell
cd "d:\Sarvam API\tests\TaggingAutomation"; python validate_tagging.py
```

> `TaggingAutomationData.xlsx` must be present in the same folder as the script before running.

## Output

A timestamped Excel file is written to the same directory:

```
TaggingAutomationData_Results_YYYYMMDD_HHMMSS.xlsx
```

Nine new columns are appended to the original sheet:

| Column | Name | Description |
|--------|------|-------------|
| +1 | ActualEnglishText | Source text as received by the API |
| +2 | ActualIntgtText | Tags found in the translated text |
| +3 | IntgtText_Result | Pass / Fail comparison against expected |
| +4 | ActualInsrcText | Tags found in the source text |
| +5 | InsrcText_Result | Pass / Fail comparison against expected |
| +6 | ActualInoutputText | Token output values from the API |
| +7 | InoutputText_Result | Pass / Fail comparison against expected |
| +8 | NotContains_Result | Pass / Fail for the not-contains check |
| +9 | Overall_Result | Pass only if all four checks pass |

Pass cells are highlighted green; Fail cells are highlighted red.

## Validation logic

| Check | What is compared |
|-------|-----------------|
| **IntgtText** | Tag names in translated text vs expected tag list |
| **InsrcText** | Tag names in source text vs expected tag list |
| **InoutputText** | Token `srcText` values vs expected (supports comma-separated, pipe-separated, HTML tags, `<br>` spacing, and `#{...}#` placeholders) |
| **NotContains** | `#{...}#` values must be present in `outputText`; all other values must be absent |

Pipe (`|`) in the expected output triggers per-sentence validation mode, where each segment is matched against a separate API sentence object.
