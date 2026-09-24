## Score API Configuration Management (Quality + Language with Client Overrides)

**Endpoint:** `https://p9authwave.mox2.net.in/p9/reprocesslog.ashx`
**Method:** POST (JSON)

### API Keys

| Key Name | API Key | Config Type |
|---|---|---|
| Key1 | `85BE-52EC-6E0A-52F2-8F17-E377-3FFC-722F` | Client |
| Key2 | `2DAC-DC08-8B5F-50D3-341E-A4FE-2728-7CDB` | BFL |
| Key3 | `F08C-22B9-5A7E-974F-74E3-3A6F-8316-F33E` | Default |

### Request Body

```json
{
    "key": "<api-key>",
    "data": [{ "text": "<source text>", "qual": "<quality 1-7>", "op": "0" }],
    "InputLanguage": "english",
    "lang": ["hindi"]
}
```

### Score Validation Rule (Key Response Field)

| Field | Description |
|---|---|
| `score` | Raw quality score from scoring API. `0` = scoring skipped (weight=1). `>0` = scoring was invoked (weight<1). |
| `dataQuality` | Effective quality after scoring (97 when skipped, 50 when invoked for qual=7). |
| `inQual` | Requested quality level. |
| `outQual` | Resolved output quality level. |

### Quality Levels and Score Behaviour

| Quality | Label | Config Weight | Expected score in Response |
|---|---|---|---|
| 1 | - | 1 | 0 (scoring skipped) |
| 2 | - | 1 | 0 (scoring skipped) |
| 3 | - | 1 | 0 (scoring skipped) |
| 4 | - | 1 | 0 (scoring skipped) |
| 6 | Mox Smart | 1.0 | 0 (scoring skipped) |
| 7 | Mox Smart Plus | < 1 (0.9 default / 0.95 client override) | > 0 (scoring invoked) |

### Configuration Structure

**Default Config** — Applied when no client override exists:
```json
{
  "Default": [{
    "inlanguage": "english",
    "Language": "Hindi",
    "ScoreData": [
      { "Quality": 1, "score": 1,   "scoreapi": "https://tl.mox.net.in/api/v1/scores/calculate-batch-scores/" },
      { "Quality": 2, "score": 1,   "scoreapi": "https://tl.mox.net.in/api/v1/scores/calculate-batch-scores/" },
      { "Quality": 3, "score": 1,   "scoreapi": "https://tl.mox.net.in/api/v1/scores/calculate-batch-scores/" },
      { "Quality": 4, "score": 1,   "scoreapi": "https://tl.mox.net.in/api/v1/scores/calculate-batch-scores/" },
      { "Quality": 6, "score": 1.0, "scoreapi": "https://tl.mox.net.in/api/v1/scores/calculate-batch-scores/" },
      { "Quality": 7, "score": 0.9, "scoreapi": "https://tl.mox.net.in/api/v1/scores/calculate-batch-scores/" }
    ]
  }]
}
```

**Client Override Config** — Overrides default for specific languages:
```json
{
  "ClientKey": [{
    "inlanguage": "english",
    "Language": "Hindi",
    "ScoreData": [
      { "Quality": 7, "score": 0.95, "scoreapi": "https://mtaz.mox.net.in/api/v1/scores/calculate-batch-scores/" }
    ]
  }]
}
```

### Merge Rules

| Rule | Condition | Effective Config |
|---|---|---|
| Rule 1 | Language exists in client config | Use client config |
| Rule 2 | Language NOT in client config | Fall back to default config |
| Rule 3 | Client specifies different weight for a language | Client config overrides entire language entry |

### Resolution Priority
Client Config → Default Config → System Fallback

### Supported Languages
Assamese, Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi, Oriya, Punjabi, Tamil, Telugu, Urdu
