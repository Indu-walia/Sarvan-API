import re
import sys
import warnings
import difflib
import requests
import openpyxl
from datetime import datetime
from openpyxl.styles import PatternFill, Font

warnings.filterwarnings('ignore')

API_URL  = 'https://bfluat.mox.net.in/translator/unified'
SRC_LANG = 'english'
TARGET_LANGS = ['hindi', 'tamil', 'malayalam', 'telugu', 'marathi']

# Reprocess API - run in parallel with the main MT API above as a second,
# independent translation source for the same text/language.
REPROCESS_API_URL = 'https://dev-moxwave.mox2.net.in/p9/reprocesslog.ashx'
REPROCESS_API_KEY = '1CDE-8392-944C-1FDC-6F85-791A-C88E-A241'

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


def call_reprocess_api(text, tgt_lang):
    """Second, independent translation source for the same text/language —
    the API may split the sentence into multiple response objects, so their
    outputText fields are joined in order."""
    payload = {
        'key': REPROCESS_API_KEY,
        'data': [{'field': '', 'text': text, 'qual': '6', 'op': '0'}],
        'InputLanguage': 'English',
        'lang': [tgt_lang]
    }
    resp = requests.post(REPROCESS_API_URL, json=payload, timeout=30, verify=False)
    resp.raise_for_status()
    data = resp.json()
    return ' '.join(d.get('outputText', '') for d in data) if isinstance(data, list) else ''


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


_NON_LETTER_RE = re.compile(r"[^A-Za-zÀ-ÖØ-öø-ÿ\s'-]")


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
    if _NON_LETTER_RE.search(name):
        # Name has a digit/symbol suffix (e.g. "yd²", "Citroen C3") - require the
        # WHOLE standalone transliteration to appear verbatim, not just a partial
        # overlap. Partial overlap is unsafe here: "yd²" standalone comes back as
        # "यार्ड2" (the model translated "yd" into the real word "yard" rather
        # than transliterating it), and "यार्ड" alone then coincidentally matches
        # the word "yard" that legitimately appears elsewhere in a sentence about
        # square yards - a false positive with the digit/symbol suffix silently
        # dropped from the match. Requiring the full string (digit/symbol
        # included) closes that gap while still allowing "सिट्रोन C3" to match
        # in full when the model code genuinely survived intact.
        return match.size == len(expected)
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
    src_file = sys.argv[1] if len(sys.argv) > 1 else 'Brandnamedata.xlsx'
    src_wb = openpyxl.load_workbook(src_file)
    src_ws = src_wb.active

    # Input is language-wise: one row per (test case, language), so BrandName/
    # NotContains can differ per language instead of one value applying to all.
    # Grouped by Sno (preserving first-seen order) so the output lists all
    # languages for one test case together before moving to the next Sno.
    by_sno = {}
    sno_order = []
    for r in range(2, src_ws.max_row + 1):
        text = src_ws.cell(r, 2).value or ''
        lang = str(src_ws.cell(r, 3).value or '').strip().lower()
        if not str(text).strip() or lang not in TARGET_LANGS:
            continue
        sno = src_ws.cell(r, 1).value
        if sno not in by_sno:
            by_sno[sno] = {'text': text, 'langs': {}}
            sno_order.append(sno)
        by_sno[sno]['langs'][lang] = (
            src_ws.cell(r, 4).value or '',
            src_ws.cell(r, 5).value or '',
        )

    out_wb = openpyxl.Workbook()
    ws = out_wb.active
    ws.title = 'Results'
    headers = ['Sno', 'text', 'Language', 'BrandName', 'NotContains', 'output text', 'Result',
               'ReprocessoutputText', 'ReprocessResult']
    for c, header in enumerate(headers, start=1):
        ws.cell(1, c, header).font = BOLD

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    src_stem = src_file.rsplit('.', 1)[0]
    out_file = f'{src_stem}_Results_{timestamp}.xlsx'

    def save():
        try:
            out_wb.save(out_file)
        except PermissionError:
            print(f'WARNING: {out_file} is open elsewhere — skipping this checkpoint save.')

    row_idx = 2
    for sno in sno_order:
        text = by_sno[sno]['text']
        print(f'--- Sno={sno} ---')
        for lang in TARGET_LANGS:
            if lang not in by_sno[sno]['langs']:
                continue
            brand_name, not_contain = by_sno[sno]['langs'][lang]
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

            try:
                reprocess_output = call_reprocess_api(text, lang)
                rp_contains_result, rp_missing = check_brand_present(brand_name, reprocess_output, lang)
                rp_notcontains_result, rp_found = check_not_contains(not_contain, reprocess_output)
                reprocess_result = 'Pass' if rp_contains_result == 'Pass' and rp_notcontains_result == 'Pass' else 'Fail'
                rp_reasons = []
                if rp_missing:
                    rp_reasons.append(f'Missing: {rp_missing}')
                if rp_found:
                    rp_reasons.append(f'Found forbidden: {rp_found}')
                rp_reason = ' | '.join(rp_reasons)
            except Exception as e:
                reprocess_output, reprocess_result, rp_reason = f'ERROR: {e}', 'Fail', 'API error'

            ws.cell(row_idx, 1, sno)
            ws.cell(row_idx, 2, text)
            ws.cell(row_idx, 3, lang.capitalize())
            ws.cell(row_idx, 4, brand_name)
            ws.cell(row_idx, 5, not_contain)
            ws.cell(row_idx, 6, output_text)
            result_cell = ws.cell(row_idx, 7, f'{result} ({reason})' if reason else result)
            result_cell.fill = GREEN if result == 'Pass' else RED
            ws.cell(row_idx, 8, reprocess_output)
            reprocess_result_cell = ws.cell(row_idx, 9, f'{reprocess_result} ({rp_reason})' if rp_reason else reprocess_result)
            reprocess_result_cell.fill = GREEN if reprocess_result == 'Pass' else RED
            print(f'Sno={sno} {lang}={result} (reprocess={reprocess_result})', flush=True)
            row_idx += 1

        save()

    save()
    print(f'\nSaved: {out_file}')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
