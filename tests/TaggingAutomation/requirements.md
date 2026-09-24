# Tagging Automation – Requirements

## 1. Purpose

Validate that the P9 AuthWave reprocess-log API correctly identifies and tags named entities (numbers, alphanumerics, HTML elements, placeholders, URLs, etc.) in English source text, and that tagged tokens are faithfully preserved or omitted in the translated output.

---

## 2. API

| Property | Value |
|---|---|
| Endpoint | `https://p9authwave.mox2.net.in/p9/reprocesslog.ashx` |
| Method | POST (JSON) |
| API Key | `3642-E582-D3CC-49FA-FC38-F64C-0EC0-BCBB` |
| Input language | `english` |
| Output language | `hindi` |

**Request payload shape:**
```json
{
  "key": "<API_KEY>",
  "data": [{ "text": "<source_text>", "qual": "4", "op": "0" }],
  "InputLanguage": "english",
  "lang": ["hindi"]
}
```

**Response fields used per object:**

| Field | Used for |
|---|---|
| `srcText` | Actual tagged source text (ActualEnglishText); also token source values |
| `tgtText` | Tagged target/translated text |
| `outputText` | Final rendered output text (for NotContains check) |
| `tokens[]` | Array of tagged token objects (`context`, `srcText`) |
| `suffix` | Optional trailing suffix appended to the last token |

A response can contain multiple objects. Objects whose `srcText` matches `<br\s*/?>` are **br separator objects**; all others are **sentence objects**.

---

## 3. Input File Specification

File: `TaggingAutomationData.xlsx` — must be in the same directory as the script.

| Col | Header | Description |
|-----|---|---|
| A (1) | Sno | Row identifier |
| B (2) | Description | Human-readable test case description (not sent to API) |
| C (3) | Souce Text | English text sent to the API |
| D (4) | ExpectedIntgtText | Expected tag placeholders in the **translated** (target) text |
| E (5) | ExpectedInsrcText | Expected tag placeholders in the **source** text |
| F (6) | ExpectedInoutputText | Expected token output values (comma- or pipe-separated) |
| G (7) | ExpectedInOutputText Not Contains | Values that must NOT appear (or `#{...}#` values that MUST appear) in `outputText` |

> **Note:** The Description column (B) is for documentation only. The script reads source text from column C.

---

## 4. Validation Rules

Four independent checks are performed per row. Overall result is **Pass** only when all four pass.

### 4.1 IntgtText

Extracts all tag placeholder names (e.g. `an1`, `b1`, `span1`) from the `tgtText` of every sentence object and compares their **ordered list** against the expected value from column D.

- Tags are extracted with the regex `<(/?[a-zA-Z]+\d*)\s*/?>` (case-insensitive).
- `<br>` variants are excluded from this list.
- Pass condition: `tag_name_list(expected) == tag_name_list(actual)` (order and count must match exactly).

### 4.2 InsrcText

Same logic as IntgtText but applied to `srcText` of every sentence object, compared against column E.

### 4.3 InoutputText

Validates that each expected token value from column F matches the actual token `srcText` values returned by the API.

**Separator mode:**

| Separator | Trigger | Behaviour |
|---|---|---|
| `,` | Default | All tokens from all sentence objects are combined and matched sequentially |
| `\|` | `\|` present in expected value | Per-sentence mode: each `\|`-separated segment is matched against a separate sentence object |

**Per-token matching rules (in order):**

| Expected part | Match rule |
|---|---|
| `<br />`, `<br>`, `<br/>` | Space-before the `<br>` in source must equal space-before in the API br object |
| `<an1>`, `<n2>`, `<b1>` etc. (tag placeholder) | Compared against `token.context` (case-insensitive) |
| HTML content (e.g. `<span class="x"></span>`) | Compared against `token.srcText`; adjacent HTML parts split by comma are re-merged |
| Number stored as integer by Excel (e.g. `17000` for `17,000`) | Formatting commas are stripped from both sides before comparing |
| Plain text | Compared against `token.srcText` after HTML-entity decoding and whitespace collapse; if unmatched, checked against source text as a literal (contextual prefix/suffix — does not consume a token slot) |

All comparisons use **normalized values**: HTML entities decoded, backslash-escaped quotes resolved, whitespace collapsed.

### 4.4 NotContains

Checks the concatenated `outputText` of all sentence objects against column G.

| Value pattern | Requirement |
|---|---|
| `#{...}#` | The placeholder **must be present** in `outputText` (absent → Fail) |
| Anything else (tag placeholder, plain text) | The value **must NOT be present** in `outputText` (present → Fail) |

Empty column G → Pass (check skipped).

---

## 5. Output File Specification

A timestamped file is written to the same directory:
```
TaggingAutomationData_Results_YYYYMMDD_HHMMSS.xlsx
```

Nine columns are appended to the original sheet starting after the last input column:

| Column | Name | Description |
|---|---|---|
| +1 | ActualEnglishText | `srcText` from the first sentence object |
| +2 | ActualIntgtText | Comma-joined tag list from all `tgtText` values |
| +3 | IntgtText_Result | Pass / Fail |
| +4 | ActualInsrcText | Comma-joined tag list from all `srcText` values |
| +5 | InsrcText_Result | Pass / Fail |
| +6 | ActualInoutputText | Comma-joined `srcText` from all non-br tokens |
| +7 | InoutputText_Result | Pass / Fail |
| +8 | NotContains_Result | Pass / Fail |
| +9 | Overall_Result | Pass only when all four checks are Pass |

Pass cells are filled **green** (`#C6EFCE`); Fail cells are filled **red** (`#FFC7CE`).

---

## 6. Test Case Catalogue

### 6.1 Standard Entities

| Sno | Description | Source Text | Expected IntgtText | Expected InsrcText | Expected Output | Not Contains |
|---|---|---|---|---|---|---|
| 1 | Email Address and URL | `New company email rajput@process9.com and url https://gmt1.mox2.net.in/` | `<an1>,<an2>` | `<an1>,<an2>` | `rajput@process9.com,https://gmt1.mox2.net.in/` | `<an1>,<an2>` |
| 2 | Mixed Alphanumeric Model Number and Standalone Numbers | `HP Victus, AMD Ryzen 9-8945HS, 8GB NVIDIA GeForce RTX 4060 AI Gaming Laptop` | `<an1>, <n1>,<n2>` | `<an1>, <n1>,<n2>` | `9-8945HS,8,4060` | `<an1>, <n1>,<n2>` |
| 4 | Date | `Your message was received on 12-November-2005.` | `<n1>,<n2>` | `<n1>,<n2>` | `"12-November-2005"` | `<n1>,<n2>` |
| 7 | Phone number | `Phone no: 022-27595666, 022-27595415, 022-27523516).` | `<an1>, <an2>, <an3>` | `<an1>, <an2>, <an3>` | `022-27595666, 022-27595415, 022-27523516` | `<an1>, <an2>, <an3>` |
| 9 | Date + URL (multi-sentence) | `...FATF on June 13, 2025...https://www.fatf-gafi.org/...` | `<n1>,<n2>\|<an1>` | `<n1>,<n2>\|<an1>` | `13,2025\|https://www.fatf-gafi.org/...` | `<n1>,<n2>\|<an1>` |
| 15 | URL | `visit https://www.paytmbank.com/ratescharges/` | `<an1>` | `<an1>` | `https://www.paytmbank.com/ratescharges/` | `/` |

### 6.2 Currency and Amounts

| Sno | Description | Source Text | Expected IntgtText | Expected Output | Not Contains |
|---|---|---|---|---|---|
| 10 | Amount with comma separator | `...chimneys under Rs. 17,000.` | `<n1>,<n2>` | `"17,000"` | `<n1>,<n2>` |
| 11 | Amount in anchor tag | `...chimneys under Rs. 15,000</a>...` | `<a1>,₹, <n1>,<n2>,</a1>` | `<a href="...">,₹, 15,000,</a>` | `<a1>, <n1>,<n2>,</a1>` |
| 33 | Currency ₹ with curly-brace variables | `EMI ₹{emi_amount_monthly} approved for {approvedLimitValue}` | `₹,<an2>,<an1>` | `₹,{emi_amount_monthly},{approvedLimitValue}` | `<an2>,<an1>` |
| 35 | Currency $ with curly-brace variables | `EMI ${emi_amount_monthly} approved for {approvedLimitValue}` | `$,<an2>,<an1>` | `$,{emi_amount_monthly},{approvedLimitValue}` | `<an2>,<an1>` |

### 6.3 HTML Tags

| Sno | Description | Source Text | Expected IntgtText | Expected Output | Not Contains |
|---|---|---|---|---|---|
| 3 | HTML tag with attributes + number | `<span class="label">Company Name:</span> Process9<br>` | `<span1></span1>,<n1>` | `<span class="label"></span>,9` | `<span1></span1>,<n1>` |
| 5 | `<a>` and `<img>` tags | `<a href="...">This is a sample</a> and <img src="..." ...>` | `<a1>,</a1>,<img2>` | `<a href="...">,</a>,<img src="..." ...>` | `<a1>,</a1>,<img2>` |
| 8 | Self-closing `<br />` with number | `...security for 20 Rs...<br /> <br /> The Royal Enfield...` | `<n1>` | `<n1>\|<br />\|<br />` | `<n1>` |
| 12 | Multiple `<b>` / `</b>` tags | `<b>Nifty</b> Smallcap 100...<b>comprises</b>...100...<b>companies.</b>` | `<b1>,</b1>,<n1>,<b2>,</b2>,<n2>,<b3>,</b3>` | `<b>,</b>,100,<b>,</b>,100,<b>,</b>` | `<b1>,</b1>,<n1>,<b2>,</b2>,<n2>,<b3>,</b3>` |
| 17 | HTML-encoded tags (`&lt;b&gt;`) | `&lt;b&gt;zero mdr charges...&lt;/b&gt;&lt;br&gt;...` | `<b1>,</b1><br2>,<br3>` | `&lt;b&gt;,&lt;/b&gt;&lt;br&gt;,&lt;br&gt;` | `<b1>,</b1><br2>,<br3>` |

### 6.4 Non-Curly Placeholders

| Sno | Description | Source Text | Expected IntgtText | Expected Output | Not Contains |
|---|---|---|---|---|---|
| 6 | `%$$...$$%` placeholders | `...%$$SDPmindepositSDP$$%...%$$FD-Interest-Amount-Banner$$%` | `<an1>,<an2>` | `%$$SDPmindepositSDP$$%,%$$FD-Interest-Amount-Banner$$%` | `<an1>,<an2>` |
| 13 | `#{...}#` template placeholder | `Go to the #{mandate_management}# from the main menu.` | `<an1>` | `#{mandate_management}#` | `<an1>` |
| 14 | `%$$...$$%` single placeholder | `...%$$BOL-Flexi-EMI$$%* on EMIs...` | `<an1>` | `%$$BOL-Flexi-EMI$$%` | `<an1>` |

### 6.5 Curly-Brace Variable Placeholders `{...}`

| Sno | Description | Source Text | Expected IntgtText | Expected Output | Not Contains |
|---|---|---|---|---|---|
| 18 | Simple variable | `{amount}` | `<an1>` | `{amount}` | `<an1>` |
| 19 | Underscore variable | `{loan_id}` | `<an1>` | `{loan_id}` | `<an1>` |
| 20 | Camel-case variable | `{customerName}` | `<an1>` | `{customerName}` | `<an1>` |
| 21 | Alphanumeric variable | `{amount123}` | `<an1>` | `{amount123}` | `<an1>` |
| 22 | Variable within sentence | `Loan amount is {amount}` | `<an1>` | `{amount}` | `<an1>` |
| 23 | Multiple variables, no space between | `Bank {firstName}{lastName}` | `<an1>,<an2>` | `{firstName },{lastName}` | `<an1>,<an2>` |
| 24 | Multiple variables, character in between | `Bank {firstName}A{lastName}` | `<an1>,<an2>` | `{firstName }A{lastName}` | `<an1>,<an2>` |
| 25 | Multiple variables, comma in between | `Bank {firstName},{lastName}` | `<an1>,<an2>` | `{firstName },{lastName}` | `<an1>,<an2>` |
| 26 | Variable with space inside braces | `Bank {first Name}{lastName}` | `<an1>,<an2>` | `Bank {first Name}{lastName}` | `<an1>,<an2>` |
| 27 | Variable wrapped in `#*{...}*#` | `please #*{raise_a_request}*# with us.` | `<an1>` | `#*{raise_a_request}*#` | `<an1>` |
| 28 | Uppercase variable followed by `%` | `Foreclosure charges are {PERCENTAGE}% of outstanding amount.` | `<an1>` | `{PERCENTAGE}%` | `<an1>` |
| 29 | Uppercase variable, no suffix | `Foreclosure charges are {PERCENTAGE} of outstanding amount.` | `<an1>` | `{PERCENTAGE}` | `<an1>` |
| 30 | Dot-notation and `$`-prefix variables | `...{data.compInfo.compName} is {$PE} ratio and ${PB} ratio as of {$date}.` | `<an1>,<an2>,<an3>` | `{data.compInfo.compName},{$PE},${PB}` | `<an1>,<an2>,<an3>` |
| 31 | Variables with underscore and surrounding spaces | `Bank {first_Name } { last_Name}` | `<an1>,<an2>` | `{first_Name }, { last_Name}` | `<an1>,<an2>` |
| 32 | Long alphanumeric variable with underscores | `Approved loan amount {loan_amount_data_2025}` | `<an1>` | `{loan_amount_data_2025}` | `<an1>` |
| 34 | Broken / incomplete placeholder | `...# fixed {deposit_page` | `<an1>` | `{deposit_page` | `<an1>` |
| 36 | Space inside variable, wrapped in `#*{...}*#` | `...#*{repeat withdrawal}*# option...30 days...` | `<an1>` | `#*{repeat withdrawal}*#` | `<an1>` |

### 6.6 Complex / Mixed Patterns

| Sno | Description | Source Text | Expected IntgtText | Expected Output | Not Contains |
|---|---|---|---|---|---|
| 16 | Mixed: underscore-prefix, percent, bracket-hash, underscore-suffix | `6856_Paytm Deals_Upto 10% off on S[#]CIAL, Pop Tate's & more._DEALS` | `<an1><an2>,<n1>,<an3>,<an4>` | `6856_Paytm,Deals_Upto, 10% ,S[#]CIAL,_DEALS` | `<an1><an2>,<n1>,<an3>,<an4>` |

---

## 7. Special Handling Rules

### 7.1 `<br>` spacing
When a `<br>` appears in expected output, the validator checks whether the space **before** that `<br>` in the source text matches the space reported by the corresponding API br object. A mismatch in spacing → Fail.

### 7.2 Pipe separator (`|`)
A `|` in `ExpectedInoutputText`, `ExpectedIntgtText`, or `ExpectedInsrcText` indicates the source text spans multiple sentences. Each `|`-separated segment is matched against its corresponding sentence object from the API response. `<br>` parts do not advance the sentence index.

### 7.3 Comma-formatted numbers
Excel silently stores `17,000` as the integer `17000`. The validator detects numeric expected values and strips formatting commas from both sides before comparing.

### 7.4 HTML entity encoding
Expected values may contain HTML entities (e.g. `&lt;b&gt;`). Both expected and actual values are decoded with `html.unescape()` before comparison.

### 7.5 `#{...}#` placeholders in NotContains
The `#{...}#` pattern reverses the NotContains logic: the placeholder **must be present** in `outputText` (the API must have preserved it rather than translating it).

### 7.6 Contextual literal text
If an expected output part is not found in any token's `srcText` but IS present as a substring of the original source text (e.g. a `₹` currency prefix), it is accepted without consuming a token slot.

### 7.7 Adjacent HTML tag merging
When splitting expected or actual output by comma, adjacent parts that form a single HTML element (open tag immediately followed by close tag) are re-merged. Tag placeholders like `<an1>`, `<n2>` are never merged.

---

## 8. Running the Script

The script must be run from inside the `TaggingAutomation` folder:

```powershell
cd "d:\Sarvam API\tests\TaggingAutomation"
python validate_tagging.py
```

Python 3.8+ required. Dependencies:
```
pip install requests openpyxl
```
