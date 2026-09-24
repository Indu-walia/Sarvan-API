## Client Cache Dummy Tag Validation API

**Endpoint:** `https://p9clientcacheapi.mox2.net.in/moxlocalization/moxtm/QAUpdateData`
**Method:** POST (JSON)
**Auth Key:** `3642-E582-D3CC-49FA-FC38-F64C-0EC0-BCBB`

### Request Body

```json
{
    "AuthKey": "3642-E582-D3CC-49FA-FC38-F64C-0EC0-BCBB",
    "InLanguage": "English",
    "Language": "hindi",
    "Data": {
        "source_text": "<english source text>",
        "target_text": "<hindi target text>",
        "classification": "Translation",
        "subClassification": "Translation",
        "userName": "pooja admin",
        "quality": 1,
        "transFlag": 0
    }
}
```

### Response Structure

```json
{
  "Type": "Insert",
  "Data": {
    "RecId": "...",
    "HashKey": "...",
    "Source_text": "<tagged english — e.g. flexi <n1> variant>",
    "Target_text": "<tagged hindi — e.g. फ्लेक्सी <n1> वेरिएंट>",
    "Classification": "Translation",
    "SubClassification": "Translation",
    "UserName": "pooja admin",
    "Words": 3,
    "Quality": 1,
    "TransFlag": 0,
    "Original_source_text": "<original untagged english>",
    "Original_target_text": "<original untagged hindi>"
  }
}
```

### Key Response Fields for Validation

| Field | Description |
|---|---|
| `Data.Source_text` | Tagged English source — numbers/entities replaced with `<n1>`, `<an1>` etc. |
| `Data.Target_text` | Tagged Hindi target — same placeholders |
| `Data.Original_source_text` | Original untagged English input |
| `Data.Original_target_text` | Original untagged Hindi input |

### Example

Input source: `Flexi 78 variant` + target: `फ्लेक्सी 78 वेरिएंट`
→ `Source_text: "flexi <n1> variant"`
→ `Target_text: "फ्लेक्सी <n1> वेरिएंट"`
