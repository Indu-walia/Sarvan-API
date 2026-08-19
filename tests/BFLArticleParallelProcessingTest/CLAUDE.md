## BFL Article Parallel Processing API

**Endpoint:** `https://qa_article.mox2.net.in/Article`
**Method:** POST (JSON)
**Header:** `X-API-KEY: 7895-620F-FB0B-8853-0015-17C6-8B13-720A`

### Request Body

```json
{
    "outQuality": 0,
    "inQuality": 6,
    "JobId": 0,
    "Status": 1,
    "PublishDate": "0001-01-01T00:00:00",
    "translationLanguage": "Hindi",
    "correctionLanguage": null,
    "correctionComments": null,
    "previewUrl": "http://localhost:4503/content/dam/dsf/47/1029859/vijay-sales-in-dundigalgandimaisamma-mandal",
    "comments": [
        {
            "comment": "Translation via workflow",
            "user": "10919@partner.bajajfinserv.in",
            "timestamp": "2025-02-06T16:00:19.560+05:30"
        }
    ],
    "actionType": 1,
    "siteId": "3",
    "articleVersion": 8700000001.0,
    "articleContent": "<?xml version=\"1.0\" encoding=\"UTF-8\"?><root available-locales=\"en_US\" default-locale=\"en_US\" version=\"1.0\">...</root>",
    "articleId": "Windowss",
    "articleTitle": "Fifth Request",
    "departmentName": "7895-620F-FB0B-8853-0015-17C6-8B13-720A",
    "fileId": null,
    "requestType": "Creation",
    "requesterCode": "AEM_STAGE_98d572ee-fe51-4812-8941-1e6647857cc8",
    "articleDescription": null,
    "srcLanguage": "English"
}
```

### Key Request Fields

| Field | Description |
|---|---|
| `outQuality` / `inQuality` | Quality level codes for output/input processing |
| `translationLanguage` / `srcLanguage` | Target and source languages |
| `articleContent` | XML/CDATA payload — the actual AEM component tree with translatable `<prop>` CDATA text |
| `actionType` | 1 = Creation (per sample) |
| `requestType` | e.g. `"Creation"` |
| `articleId` | Unique identifier for the article translation job |
| `departmentName` | Set to the same value as the API key in the sample payload |
| `requesterCode` | Caller/job identifier, prefixed `AEM_STAGE_...` in QA |

### Purpose

This endpoint accepts an AEM article's XML content (with CDATA-wrapped translatable strings inside `<prop>` elements) and queues/processes it for translation. This project tests **parallel/concurrent submission** of multiple article requests to validate the API handles simultaneous processing correctly (no race conditions, no dropped/corrupted jobs, consistent `JobId`/response per request).

### Notes

- `articleContent` is an XML string embedded as a JSON string value — CDATA sections wrap the actual translatable text (e.g. `<prop name="consentText"><![CDATA[Open the door.]]></prop>`).
- Environment is QA (`qa_article.mox2.net.in`).
