# Client Cache Dummy Tag Validation

Automated test runner that validates tagging, quality, language, and original text preservation for the P9 Client Cache API. It reads test cases from an input Excel file, calls the API for each row, compares the response against expected values, and writes colour-coded Pass/Fail results to a timestamped output file.

---

## Prerequisites

Python 3.8+ with the following packages:

```
pip install requests openpyxl
```

---

## Project Files

| File | Purpose |
|---|---|
| `ClientCache_Input.xlsx` | Input file — add your test cases here |
| `validate_client_cache.py` | Script that runs the validation |
| `ClientCache_Results_YYYYMMDD_HHMMSS.xlsx` | Output file — generated each run |
| `CLAUDE.md` | API reference documentation |

---

## Step 1 — Fill the Input File

Open `ClientCache_Input.xlsx` and add test cases. Each row is one test case.

| Column | Header | What to fill |
|---|---|---|
| A | Sno | Row number (1, 2, 3 …) |
| B | Description | Short description of the test case |
| C | SourceText | English source text sent to the API |
| D | TargetText | Hindi (or other language) target text sent to the API |
| E | Language | Target language — e.g. `hindi`, `marathi` |
| F | InputQuality | Quality value sent in the request — e.g. `1` |
| G | ExpectedOutputQuality | Quality value expected back in the response |
| H | ExpectedSrcTags | Expected tags in the tagged source — e.g. `<n1>` |
| I | ExpectedTgtTags | Expected tags in the tagged target — e.g. `<n1>` |
| J | ExpectedOriginalSrc | Expected `Original_source_text` in response (usually same as SourceText) |
| K | ExpectedOriginalTgt | Expected `Original_target_text` in response (usually same as TargetText) |
| L | NotContains | Comma-separated values that must NOT appear in the tagged output |

**Example row:**

| Sno | Description | SourceText | TargetText | Language | InputQuality | ExpectedOutputQuality | ExpectedSrcTags | ExpectedTgtTags | ExpectedOriginalSrc | ExpectedOriginalTgt | NotContains |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Number tagging hindi q1 | Flexi 78 variant | फ्लेक्सी 78 वेरिएंट | hindi | 1 | 1 | `<n1>` | `<n1>` | Flexi 78 variant | फ्लेक्सी 78 वेरिएंट | |

---

## Step 2 — Run the Script

Open a terminal and navigate to this folder:

```powershell
cd "d:\Sarvam API\tests\ValidateClientdummyTagdata"
python validate_client_cache.py
```

The script prints progress for each row as it runs:

```
Processing row 2 (Sno=1)... SrcTags=Pass, TgtTags=Pass, Quality=Pass, OrigSrc=Pass, OrigTgt=Pass, Lang=Pass → Pass
Saved: ClientCache_Results_20260608_103000.xlsx
```

---

## Step 3 — Review the Output File

A timestamped output file is created in the same folder:

```
ClientCache_Results_YYYYMMDD_HHMMSS.xlsx
```

It contains all input columns plus the following result columns:

| Column | Name | Description |
|---|---|---|
| +1 | ActualSrcText | Tagged source text returned by the API |
| +2 | SrcTags_Result | Pass / Fail — source tag comparison |
| +3 | ActualTgtText | Tagged target text returned by the API |
| +4 | TgtTags_Result | Pass / Fail — target tag comparison |
| +5 | InputQuality | Quality sent in the request |
| +6 | ResponseQuality | Quality returned in the response |
| +7 | Quality_Result | Pass / Fail — quality comparison |
| +8 | ActualOriginalSrc | `Original_source_text` from response |
| +9 | OriginalSrc_Result | Pass / Fail — original source comparison |
| +10 | ActualOriginalTgt | `Original_target_text` from response |
| +11 | OriginalTgt_Result | Pass / Fail — original target comparison |
| +12 | ActualLanguage | Language used in the request |
| +13 | Language_Result | Pass / Fail — language check |
| +14 | NotContains_Result | Pass / Fail — not-contains check |
| +15 | Overall_Result | Pass only if all checks pass |

Pass cells are highlighted **green**, Fail cells are highlighted **red**.

---

## Validation Logic

| Check | What is compared |
|---|---|
| **SrcTags** | Tag names in `Data.Source_text` vs `ExpectedSrcTags` |
| **TgtTags** | Tag names in `Data.Target_text` vs `ExpectedTgtTags` |
| **Quality** | `Data.Quality` (response) vs `ExpectedOutputQuality` (input) |
| **OriginalSrc** | `Data.Original_source_text` vs `ExpectedOriginalSrc` |
| **OriginalTgt** | `Data.Original_target_text` vs `ExpectedOriginalTgt` |
| **Language** | Language sent in request appears in response |
| **NotContains** | Listed values must NOT appear in tagged source or target text |

---

## API Details

| Property | Value |
|---|---|
| Endpoint | `https://p9clientcacheapi.mox2.net.in/moxlocalization/moxtm/QAUpdateData` |
| Method | POST (JSON) |
| Auth Key | `3642-E582-D3CC-49FA-FC38-F64C-0EC0-BCBB` |
| Input Language | `English` (fixed) |
| Output Language | Set per row via `Language` column |
