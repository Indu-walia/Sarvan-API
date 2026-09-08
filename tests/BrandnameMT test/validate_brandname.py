import re
import sys
import warnings
import difflib
import requests
import openpyxl
from datetime import datetime
from openpyxl.styles import PatternFill, Font

warnings.filterwarnings('ignore')

API_URL    = 'https://mtaz.mox.net.in/translator/unified'
TOKENS_URL = 'https://mtaz.mox.net.in/translator/tokens'
SRC_LANG = 'english'
TARGET_LANGS = ['hindi', 'tamil', 'malayalam', 'telugu', 'marathi']

MATCH_RATIO_THRESHOLD = 0.6  # min overlap between output and the name's native-script transliteration

GREEN = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
RED   = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
BOLD  = Font(bold=True)

_translit_cache = {}

_NATIVE_SCRIPT_RE = re.compile(r'[ऀ-ॿ஀-௿ഀ-ൿఀ-౿]')
_LATIN_RE = re.compile(r'[A-Za-z]')


def _is_mixed_script(s):
    """True if any single whitespace-separated token mixes native-script (Devanagari/Tamil/
    Malayalam/Telugu) letters with Latin letters within itself — the signature of a broken,
    half-transliterated word (e.g. "एल'ओआरéAL"). A clean rendering like "सिट्रोन C3", where a
    fully-transliterated word sits next to a separate, fully-Latin model code, is NOT mixed:
    each token on its own is script-pure."""
    return any(_NATIVE_SCRIPT_RE.search(tok) and _LATIN_RE.search(tok) for tok in s.split())


def call_api(text, tgt_lang):
    payload = {
        'text': [text],
        'srcLang': SRC_LANG,
        'tgtLang': tgt_lang
    }
    resp = requests.post(API_URL, json=payload, timeout=30, verify=False)
    resp.raise_for_status()
    data = resp.json()
    return data[0] if isinstance(data, list) and data else ''


def _norm(s):
    return s.replace('‌', '').replace('‍', '').strip()


def _transliteration_of(name, tgt_lang):
    """Native-script rendering of a single brand name in tgt_lang, via the same API, cached."""
    key = (name.lower(), tgt_lang)
    if key not in _translit_cache:
        try:
            _translit_cache[key] = call_api(name, tgt_lang)
        except Exception:
            _translit_cache[key] = ''
    return _translit_cache[key]


def _name_in_output(name, output_text, tgt_lang):
    """A brand name counts as present if it appears literally, or if its native-script
    transliteration overlaps the output text above MATCH_RATIO_THRESHOLD (handles case
    endings / joiner differences between the standalone and in-sentence transliteration)."""
    out_norm = _norm(output_text)
    if name.lower() in out_norm.lower():
        return True

    expected = _norm(_transliteration_of(name, tgt_lang))
    if not expected or _is_mixed_script(expected):
        return False
    if not _NATIVE_SCRIPT_RE.search(expected):
        # No genuine transliteration happened - the API just echoed the name back
        # unchanged (typical for symbols/punctuation like "###" or "₹###", which
        # have no valid "phonetic spelling" in another script). Without a real
        # script conversion there's no excuse for fuzzy overlap: the literal
        # check above already failed, so this is a genuine miss, e.g. "₹###"
        # showing up as "₹##" with a character silently dropped.
        return False
    match = difflib.SequenceMatcher(None, expected, out_norm).find_longest_match(0, len(expected), 0, len(out_norm))
    return (match.size / len(expected)) >= MATCH_RATIO_THRESHOLD


def check_brand_present(brand_names, output_text, tgt_lang):
    """All brand names (comma-separated) must appear (literally or transliterated) in
    output_text, each as its own distinct occurrence. Checked longest-first, consuming
    a matched literal span before checking shorter names — otherwise a name that's a
    substring of another required name (e.g. "###" inside "₹###") would be satisfied
    by that other name's single occurrence even if its own separate occurrence in the
    source (e.g. a second, standalone "###" elsewhere in the sentence) was dropped."""
    if not brand_names:
        return 'Pass', ''
    names = [n.strip() for n in str(brand_names).split(',') if n.strip()]
    remaining = output_text
    missing = []
    for n in sorted(names, key=len, reverse=True):
        if _name_in_output(n, remaining, tgt_lang):
            idx = remaining.lower().find(n.lower())
            if idx != -1:
                remaining = remaining[:idx] + remaining[idx + len(n):]
        else:
            missing.append(n)
    return ('Fail' if missing else 'Pass'), ', '.join(missing)


_WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:['-][A-Za-zÀ-ÖØ-öø-ÿ]+)*")
HIGH_TOKEN_THRESHOLD = 4  # words tokenized into this many subwords or more are "high-risk"


def get_word_token_details(text):
    """Tokenize every word in text via /translator/tokens.
    Returns a list of (word, subword_tokens, count) for every word."""
    words = _WORD_RE.findall(text)
    if not words:
        return []
    payload = {'text': words, 'srcLang': SRC_LANG, 'tgtLang': TARGET_LANGS[0]}
    resp = requests.post(TOKENS_URL, json=payload, timeout=30, verify=False)
    resp.raise_for_status()
    data = resp.json()
    counts = data.get('counts', [])
    tokens = data.get('text tokens', [])
    return list(zip(words, tokens, counts))


def format_word_tokens(details):
    return '; '.join(f'{w}: {t} ({c})' for w, t, c in details)


def high_token_words(details):
    """Words tokenized into >= HIGH_TOKEN_THRESHOLD subwords — informational, no pass/fail."""
    return [(w, t, c) for w, t, c in details if c >= HIGH_TOKEN_THRESHOLD]


def tag_high_token_words(text, words_to_tag):
    """Wrap each occurrence of a word in words_to_tag with <NE>...</NE>, leaving
    everything else (including untagged words and punctuation) untouched.
    Returns (tagged_text, tagged_words) where tagged_words is the ordered list
    of words that got wrapped (one entry per occurrence)."""
    if not words_to_tag:
        return text, []
    out = []
    tagged_words = []
    last_end = 0
    for m in _WORD_RE.finditer(text):
        word = m.group()
        out.append(text[last_end:m.start()])
        if word in words_to_tag:
            out.append(f'<NE>{word}</NE>')
            tagged_words.append(word)
        else:
            out.append(word)
        last_end = m.end()
    out.append(text[last_end:])
    return ''.join(out), tagged_words


_NE_TAG_RE = re.compile(r'</?NE>', re.IGNORECASE)
_NE_PAIR_RE = re.compile(r'<NE>(.*?)</NE>', re.DOTALL | re.IGNORECASE)
_ALNUM_RE = re.compile(r'[^A-Za-z0-9]')


def check_ne_tags_survived(raw_output, tagged_words):
    """The translator echoes <NE>...</NE> back around whatever it produced for that
    span (occasionally with mismatched tag casing, e.g. </ne> — matched case-
    insensitively here). Tag contents are NOT paired positionally with
    tagged_words — translation frequently reorders phrases (e.g. Dravidian
    languages putting a trailing clause first), so the Nth surviving tag does
    not reliably correspond to the Nth tagged word. Instead:
      1. A Latin-script content is matched against whichever remaining tagged
         word it exactly equals (case/punctuation-insensitive) — it must be a
         faithful, uncorrupted copy of some real tagged word.
      2. Any native-script content can satisfy ANY one remaining word (spelling
         doesn't matter for genuine transliteration).
      3. Anything still unaccounted for falls back to a literal check of the
         original English word in the output before being called dropped."""
    tag_contents = [c.strip() for c in _NE_PAIR_RE.findall(raw_output) if c.strip()]
    clean_output = _NE_TAG_RE.sub('', raw_output).lower()

    native_contents = [c for c in tag_contents if _NATIVE_SCRIPT_RE.search(c)]
    latin_contents = [c for c in tag_contents if not _NATIVE_SCRIPT_RE.search(c)]

    remaining_words = list(tagged_words)
    for content in list(latin_contents):
        norm_content = _ALNUM_RE.sub('', content).lower()
        for word in remaining_words:
            if _ALNUM_RE.sub('', word).lower() == norm_content:
                remaining_words.remove(word)
                latin_contents.remove(content)
                break

    native_budget = len(native_contents)
    missing_words = []
    for word in remaining_words:
        if native_budget > 0:
            native_budget -= 1
            continue
        if word.lower() in clean_output:
            continue
        missing_words.append(word)

    if missing_words:
        return 'Fail', f'Dropped/garbled: {", ".join(missing_words)}'
    return 'Pass', ''


def check_not_contains(forbidden, output_text):
    """None of the forbidden strings (comma-separated) may appear literally in
    output_text. Smart/curly quotes (“ ” ‘ ’) are what's actually forbidden here —
    a straight quote (" ') is an acceptable, different character and must not be
    flagged, so this is an exact literal match with no quote-style normalization."""
    if not forbidden:
        return 'Pass', ''
    items = [x.strip() for x in str(forbidden).split(',') if x.strip()]
    found = [x for x in items if x in output_text]
    return ('Fail' if found else 'Pass'), ', '.join(found)


def main():
    src_wb = openpyxl.load_workbook('Brandnamedata.xlsx')
    src_ws = src_wb.active

    records = []
    for r in range(2, src_ws.max_row + 1):
        text = src_ws.cell(r, 2).value or ''
        if not str(text).strip():
            continue
        records.append((
            src_ws.cell(r, 1).value,
            text,
            src_ws.cell(r, 4).value or '',
            src_ws.cell(r, 5).value or '',
        ))

    out_wb = openpyxl.Workbook()
    ws = out_wb.active
    ws.title = 'Results'
    headers = ['Sno', 'text', 'Language', 'output text', 'BrandName', 'NotContains', 'Result']
    for c, header in enumerate(headers, start=1):
        ws.cell(1, c, header).font = BOLD

    ws2 = out_wb.create_sheet('HighTokenNE')
    headers2 = ['Sno', 'text (NE-tagged)', 'Language', 'output text', 'BrandName', 'NotContains',
                'HighTokenWords', 'Result']
    for c, header in enumerate(headers2, start=1):
        ws2.cell(1, c, header).font = BOLD

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_file = f'Brandnamedata_Results_{timestamp}.xlsx'

    details_cache = {}

    def details_for(text):
        if text not in details_cache:
            try:
                details_cache[text] = get_word_token_details(text)
            except Exception:
                details_cache[text] = []
        return details_cache[text]

    def save():
        try:
            out_wb.save(out_file)
        except PermissionError:
            print(f'WARNING: {out_file} is open elsewhere — skipping this checkpoint save.')

    row_idx = 2
    for lang in TARGET_LANGS:
        print(f'--- {lang.capitalize()} ---')
        for sno, text, brand_name, not_contain in records:
            try:
                output_text = call_api(text, lang)
                contains_result, missing = check_brand_present(brand_name, output_text, lang)
                notcontains_result, found = check_not_contains(not_contain, output_text)
                result = 'Pass' if contains_result == 'Pass' and notcontains_result == 'Pass' else 'Fail'
                reasons = []
                if missing:
                    reasons.append(f'Missing: {missing}')
                if found:
                    reasons.append(f'Found forbidden: {found}')
                reason = ' | '.join(reasons)
            except Exception as e:
                output_text, result, reason = f'ERROR: {e}', 'Fail', 'API error'

            ws.cell(row_idx, 1, sno)
            ws.cell(row_idx, 2, text)
            ws.cell(row_idx, 3, lang.capitalize())
            ws.cell(row_idx, 4, output_text)
            ws.cell(row_idx, 5, brand_name)
            ws.cell(row_idx, 6, not_contain)
            result_cell = ws.cell(row_idx, 7, f'{result} ({reason})' if reason else result)
            result_cell.fill = GREEN if result == 'Pass' else RED
            print(f'Sno={sno} {lang}={result}', flush=True)
            row_idx += 1

        save()

    print('\n--- HighTokenNE ---')
    row2_idx = 2
    for lang in TARGET_LANGS:
        for sno, text, brand_name, not_contain in records:
            high = high_token_words(details_for(text))
            if not high:
                continue
            high_words_set = {w for w, t, c in high}
            high_tokens_str = format_word_tokens(high)
            tagged_text, tagged_words = tag_high_token_words(text, high_words_set)

            try:
                raw_output = call_api(tagged_text, lang)
                clean_output = _NE_TAG_RE.sub('', raw_output)
                result, reason = check_ne_tags_survived(raw_output, tagged_words)
            except Exception as e:
                clean_output, result, reason = f'ERROR: {e}', 'Fail', 'API error'

            ws2.cell(row2_idx, 1, sno)
            ws2.cell(row2_idx, 2, tagged_text)
            ws2.cell(row2_idx, 3, lang.capitalize())
            ws2.cell(row2_idx, 4, clean_output)
            ws2.cell(row2_idx, 5, brand_name)
            ws2.cell(row2_idx, 6, not_contain)
            ws2.cell(row2_idx, 7, high_tokens_str)
            result_cell = ws2.cell(row2_idx, 8, f'{result} ({reason})' if reason else result)
            result_cell.fill = GREEN if result == 'Pass' else RED
            print(f'Sno={sno} {lang}={result}', flush=True)
            row2_idx += 1

        save()

    save()
    if row2_idx == 2:
        print(f'\nSaved: {out_file} (no rows had words with >= {HIGH_TOKEN_THRESHOLD} subword tokens)')
    else:
        print(f'\nSaved: {out_file}')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
