import re
import sys
import warnings
import difflib
import requests
import openpyxl
from datetime import datetime
from openpyxl.styles import PatternFill, Font

warnings.filterwarnings('ignore')

API_URL = 'https://bfluat.mox.net.in/translator/unified'
SRC_LANG = 'english'
TARGET_LANGS = ['hindi', 'tamil', 'malayalam', 'telugu', 'marathi']

MATCH_RATIO_THRESHOLD = 0.6  # min overlap between output and the name's native-script transliteration

GREEN = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
RED   = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
BOLD  = Font(bold=True)

_translit_cache = {}


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
    if not expected:
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


def main():
    wb = openpyxl.load_workbook('Brandnamedata.xlsx')
    ws = wb.active

    start_col = ws.max_column + 1
    col_map = {}
    col_idx = start_col
    for lang in TARGET_LANGS:
        for suffix in ('Output', 'Result'):
            header = f'{lang.capitalize()}_{suffix}'
            ws.cell(1, col_idx, header).font = BOLD
            col_map[(lang, suffix)] = col_idx
            col_idx += 1
    overall_col = col_idx
    ws.cell(1, overall_col, 'Overall_Result').font = BOLD

    for row in range(2, ws.max_row + 1):
        sno        = ws.cell(row, 1).value
        src_text   = ws.cell(row, 2).value or ''
        brand_name = ws.cell(row, 4).value or ''

        if not str(src_text).strip():
            continue

        print(f'Row {row} (Sno={sno})...', end=' ', flush=True)

        row_results = []
        for lang in TARGET_LANGS:
            try:
                output_text = call_api(src_text, lang)
                result, missing = check_brand_present(brand_name, output_text, lang)
            except Exception as e:
                output_text, result, missing = f'ERROR: {e}', 'Fail', 'API error'

            ws.cell(row, col_map[(lang, 'Output')], output_text)
            ws.cell(row, col_map[(lang, 'Result')], result)
            ws.cell(row, col_map[(lang, 'Result')]).fill = GREEN if result == 'Pass' else RED
            row_results.append(result)
            print(f'{lang}={result}', end=' ', flush=True)

        overall = 'Pass' if all(r == 'Pass' for r in row_results) else 'Fail'
        cell = ws.cell(row, overall_col, overall)
        cell.fill = GREEN if overall == 'Pass' else RED
        print(f'-> {overall}')

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_file = f'Brandnamedata_Results_{timestamp}.xlsx'
    wb.save(out_file)
    print(f'\nSaved: {out_file}')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
