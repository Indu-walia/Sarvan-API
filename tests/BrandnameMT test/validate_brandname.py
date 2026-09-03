import re
import sys
import warnings
import difflib
import requests
import openpyxl
from datetime import datetime
from openpyxl.styles import PatternFill, Font

warnings.filterwarnings('ignore')

API_URL = 'https://mtaz.mox.net.in/translator/unified'
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
    match = difflib.SequenceMatcher(None, expected, out_norm).find_longest_match(0, len(expected), 0, len(out_norm))
    return (match.size / len(expected)) >= MATCH_RATIO_THRESHOLD


def check_brand_present(brand_names, output_text, tgt_lang):
    """All brand names (comma-separated) must appear (literally or transliterated) in output_text."""
    if not brand_names:
        return 'Pass', ''
    names = [n.strip() for n in str(brand_names).split(',') if n.strip()]
    missing = [n for n in names if not _name_in_output(n, output_text, tgt_lang)]
    return ('Fail' if missing else 'Pass'), ', '.join(missing)


def check_not_contains(forbidden, output_text):
    """None of the forbidden strings (comma-separated) may appear literally in output_text."""
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

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_file = f'Brandnamedata_Results_{timestamp}.xlsx'

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

        # incremental save after each language block finishes, so a long run
        # never loses completed rows if interrupted partway through. If the
        # file is open elsewhere (e.g. in Excel) the save is skipped rather
        # than aborting the whole run — the in-memory data is unaffected and
        # the next successful save will include everything so far.
        try:
            out_wb.save(out_file)
        except PermissionError:
            print(f'WARNING: {out_file} is open elsewhere — skipping this checkpoint save.')

    try:
        out_wb.save(out_file)
        print(f'\nSaved: {out_file}')
    except PermissionError:
        print(f'\nERROR: could not save {out_file} — close it if it is open in Excel, then re-run.')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
