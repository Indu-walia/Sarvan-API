## Tagging Automation API

**Endpoint:** `https://p9authwave.mox2.net.in/p9/reprocesslog.ashx`
**Method:** POST (JSON)
**API Key:** `3642-E582-D3CC-49FA-FC38-F64C-0EC0-BCBB`

### Request Body

```json
{
    "key": "3642-E582-D3CC-49FA-FC38-F64C-0EC0-BCBB",
    "data": [
        { "text": "<english source text>", "qual": "4", "op": "0" }
    ],
    "InputLanguage": "english",
    "lang": ["hindi"]
}
```

### Response Structure

```json
[
  {
    "srcText": "<tagged english — e.g. flexi <n1> variant>",
    "tgtText": "<tagged hindi — e.g. फ्लेक्सी <n1> वेरिएंट>",
    "outputText": "<final output text>",
    "suffix": "",
    "tokens": [
      { "srcText": "78", "context": "<n1>" }
    ]
  }
]
```

### Key Response Fields for Validation

| Field | Description |
|---|---|
| `srcText` | Tagged English source — numbers/entities replaced with `<n1>`, `<an1>` etc. |
| `tgtText` | Tagged Hindi target — same placeholders |
| `outputText` | Final output text after processing |
| `tokens` | Array of tagged tokens with `srcText` (value) and `context` (tag placeholder) |
| `suffix` | Any trailing suffix attached to the last token |

### Example

Input: `Flexi 78 variant`
→ `srcText: "flexi <n1> variant"`
→ `tgtText: "फ्लेक्सी <n1> वेरिएंट"`
→ `tokens: [{ "srcText": "78", "context": "<n1>" }]`
