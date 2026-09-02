## Client Cache Load Test API

**Endpoint:** `https://clienttm.moxwave.com/moxlocalization/moxtm/GetGridRecords`
**Method:** POST (JSON)
**Content-Type:** `application/json`
**AuthKey:** `8E18-265B-E3FC-9A1A-8EF9-282A-F395-3FDA`

### Request Body

```json
{
    "AuthKey": "8E18-265B-E3FC-9A1A-8EF9-282A-F395-3FDA",
    "Language": "Hindi",
    "Quality": 6,
    "SearchText": "<english source text>",
    "FieldName": "source_text",
    "PageIndex": 0,
    "RowCount": 10
}
```

| Field | Description |
|---|---|
| `AuthKey` | Client TM auth key |
| `Language` | Target language, e.g. `Hindi` |
| `Quality` | Quality level code |
| `SearchText` | English source text to look up in the client's Translation Memory cache |
| `FieldName` | Field to search against — `source_text` searches the cached source text |
| `PageIndex` / `RowCount` | Pagination |

### Response Structure

```json
{
    "total": 1,
    "records": [
        {
            "RecId": "16F3B24E9786C28651CCF0A40D9DD6FF",
            "HashKey": "556D61C6B43D2FCED82B165FD2A8224C",
            "Source_text": "<matched cached source text>",
            "Target_text": "<cached translation>",
            "Original_source_text": "<original, differently-cased/punctuated source>",
            "Original_target_text": "<original cached translation>",
            "Quality": 6,
            "TransFlag": 0,
            "Words": 46,
            "TimeStamp": "...",
            "UpdateDate": "...",
            "URL": "<source page URL the segment was cached from>",
            "TranslationSource": 10,
            "MtScore": 0.888,
            "translationStatus": 2
        }
    ]
}
```

### Key Response Fields for Validation

| Field | Description |
|---|---|
| `total` | Number of matching cache records found |
| `records[].Source_text` | Cached source text matched against `SearchText` |
| `records[].Target_text` | Cached translation returned from TM |
| `records[].HashKey` / `RecId` | Cache record identity — useful for verifying cache hit consistency across repeated/parallel lookups |
| `records[].UpdateDate` / `TimeStamp` | Last cache write time |

### Purpose

This project tests the **client Translation Memory cache** under load — repeated/parallel `GetGridRecords` lookups against known cached segments, validating that the correct `Target_text` is returned consistently (same `HashKey`/`RecId`, no stale/dropped/corrupted entries) even under concurrent access.
