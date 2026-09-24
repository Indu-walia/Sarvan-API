## Transliteration Automation API

Same endpoint as the Tagging Automation project ([../TaggingAutomation/CLAUDE.md](../TaggingAutomation/CLAUDE.md)), but with `op` set to `"1"` instead of `"0"` — this switches the API from **tagging mode** (detects and tags entities/numbers) to **transliteration mode** (transliterates every word phonetically into the target script, word by word).

**Endpoint:** `https://dev-moxwave.mox2.net.in/p9/reprocesslog.ashx`
**Method:** POST (JSON)
**API Key:** `0E02-6C33-62CA-2F8B-A35F-FA41-D4E2-1FE2`

### Request Body

```json
{
    "key": "0E02-6C33-62CA-2F8B-A35F-FA41-D4E2-1FE2",
    "data": [
        { "text": "<english source text>", "qual": "4", "op": "1" }
    ],
    "InputLanguage": "english",
    "lang": ["hindi"]
}
```

`lang` takes exactly one target language per call — to test multiple languages, call the API once per language (change `lang` and re-send), not once with multiple entries.

### Response Structure

```json
[
  {
    "srcText": "<original english source text>",
    "tgtText": "<full sentence transliterated word-by-word>",
    "outputText": "<same as tgtText>",
    "category": "Transliteration,Transliteration",
    "transFlag": 1,
    "tokens": [
      { "srcText": "india", "tgtText": "इनडिया", "type": "word", ... },
      { "srcText": " ", "tgtText": " ", "type": "Space", ... },
      { "srcText": "hosted", "tgtText": "होस्टेड", "type": "word", ... }
    ]
  }
]
```

### Key Response Fields for Validation

| Field | Description |
|---|---|
| `tgtText` / `outputText` | Full sentence, every word transliterated into the target script (identical to each other in this mode) |
| `tokens` | One entry per word AND per whitespace run, in source order. `type: "word"` entries carry the real `srcText`→`tgtText` transliteration pair; `type: "Space"` entries are just spacing and carry no signal |
| `transFlag` | `1` for transliteration mode (vs `0` for plain translation, seen in tagging-mode responses) |
| `category` | `"Transliteration,Transliteration"` when the model treated the word as a transliteration; some words instead come back `"general"` (still transliterated, just not flagged as a named entity) |

Unlike tagging mode (op=0), there is no `<n1>`/`<an1>` placeholder tagging here — every single word in the sentence gets its own token with a literal transliterated form, so per-word comparison is straightforward: pair up `tokens` filtered to `type == "word"` against the words of the source sentence in order.

### Example

Input: `India hosted a regional education forum where Priya Nair presented research from DU`
→ `tgtText`: `इनडिया होस्टेड अ रेजियोनल एडुकेशैन फोरम वर प्रिया नेर प्रेसेनटेड रेसीर्च फ्रोम डु`
→ tokens (word-type only): `India→इनडिया, hosted→होस्टेड, a→अ, regional→रेजियोनल, education→एडुकेशैन, forum→फोरम, where→वर, Priya→प्रिया, Nair→नेर, presented→प्रेसेनटेड, research→रेसीर्च, from→फ्रोम, DU→डु`

### Purpose

This project validates **word-level transliteration** output — i.e. that every word in the source sentence gets a real, non-empty transliterated rendering in the target script (no word silently dropped or left untouched), across a set of target languages, cycled through one at a time.
