## Brandname MT Test API

**Endpoint:** `https://bfluat.mox.net.in/translator/unified`
**Method:** POST (JSON)
**Content-Type:** `application/json`

### Request Body

```json
{
    "text": [
        "India hosted a regional education forum where Priya Nair presented research from DU"
    ],
    "srcLang": "english",
    "tgtLang": "hindi"
}
```

| Field | Description |
|---|---|
| `text` | Array of source strings to translate (supports batch — multiple strings per call) |
| `srcLang` | Source language, e.g. `english` |
| `tgtLang` | Target language, e.g. `hindi` |

### Response Structure

Plain JSON array of translated strings, in the same order as the input `text` array — no tagging metadata (`srcText`/`tgtText`/`tokens` are not present, unlike the Tagging Automation API).

```json
["भारत ने एक क्षेत्रीय शिक्षा मंच की मेज़बानी की, जहां प्रिया नायर ने डीयू से अनुसंधान प्रस्तुत किया"]
```

### Example

Input: `India hosted a regional education forum where Priya Nair presented research from DU`
→ Output: `भारत ने एक क्षेत्रीय शिक्षा मंच की मेज़बानी की, जहां प्रिया नायर ने डीयू से अनुसंधान प्रस्तुत किया`

### Purpose

This project validates **brand/entity name preservation** during machine translation — i.e. that proper nouns (person names, organization/institution names, brand names) are transliterated/handled correctly rather than mistranslated or garbled, when translated as part of a full sentence (no explicit tagging step involved, unlike the reprocesslog.ashx tagging pipeline).
