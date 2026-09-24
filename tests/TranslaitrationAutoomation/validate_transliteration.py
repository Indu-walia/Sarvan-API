import re
import sys
import time
import warnings
import requests
import openpyxl
from datetime import datetime
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.styles import PatternFill, Font

warnings.filterwarnings('ignore')


def xl_safe(value):
    """Strip characters Excel/openpyxl can't store (e.g. control chars some
    API responses slip in) so a single bad response can't crash the save."""
    return ILLEGAL_CHARACTERS_RE.sub('', str(value)) if value else value

API_URL = 'https://dev-moxwave.mox2.net.in/p9/reprocesslog.ashx'
API_KEY = '0E02-6C33-62CA-2F8B-A35F-FA41-D4E2-1FE2'

# Full set of language pairs configured in Language Management
# (from "transliteration language pair.xlsx": input language, output
# language, engine for transliteration, note). Pairs are listed in the same
# order as that sheet so english->hindi / english->punjabi run before the
# hindi-> / punjabi-> pairs that depend on their output as source text.
PAIRS = [
    ('english', 'santali',             'none', None),
    ('english', 'santhali',            'none', None),
    ('english', 'bengali',             'NMT',  None),
    ('english', 'assamese',            'NMT',  None),
    ('english', 'oriya',               'NMT',  None),
    ('english', 'gujarati',            'NMT',  None),
    ('english', 'hindi',               'NMT',  None),
    ('english', 'punjabi',             'NMT',  None),
    ('english', 'tamil',               'NMT',  None),
    ('english', 'telugu',              'NMT',  None),
    ('english', 'urdu',                'NMT',  None),
    ('english', 'malayalam',           'NMT',  None),
    ('english', 'kannada',             'none', None),
    ('english', 'bodo',                'none', None),
    ('english', 'konkani',             'none', None),
    ('english', 'maithili',            'none', None),
    ('english', 'manipuri',            'none', None),
    ('english', 'nepali',              'none', None),
    ('english', 'sanskrit',            'none', None),
    ('english', 'sindhi',              'none', None),
    ('english', 'dogri',               'none', None),
    ('english', 'chinese traditional', 'none', None),
    ('english', 'rajasthani',          'none', 'not available target language'),
    ('english', 'arabic',              'NMT',  None),
    ('hindi',   'bangla',              'none', None),
    ('hindi',   'bengali',             'none', None),
    ('hindi',   'english',             'NMT',  None),
    ('hindi',   'gujarati',            'none', None),
    ('hindi',   'kashmiri',            'none', 'not available target language'),
    ('hindi',   'oriya',               'none', None),
    ('hindi',   'santhali',            'none', 'not available target language'),
    ('hindi',   'urdu',                'none', None),
    ('punjabi', 'english',             'NMT',  None),
]

GREEN = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
RED   = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
BOLD  = Font(bold=True)


def call_api(text, src_lang, tgt_lang, op):
    payload = {
        'key': API_KEY,
        'data': [{'text': text, 'qual': '4', 'op': op}],
        'InputLanguage': src_lang,
        'lang': [tgt_lang]
    }
    resp = requests.post(API_URL, json=payload, timeout=30, verify=False)
    resp.raise_for_status()
    data = resp.json()
    return data[0] if isinstance(data, list) and data else {}


def word_pairs(api_result):
    """(srcText, tgtText) for every real word token, skipping Space entries."""
    return [
        (t.get('srcText', ''), t.get('tgtText', ''))
        for t in api_result.get('tokens', [])
        if t.get('type') == 'word'
    ]


def check_transliteration_result(output_text, input_text, api_result):
    """op=1 (transliteration): every source word must have produced a non-empty
    target rendering (word-level tokens are available), and the full output must
    not be identical to the input (would mean nothing was transliterated)."""
    dropped = [src for src, tgt in word_pairs(api_result) if not tgt.strip()]
    if dropped:
        return 'Fail', f'Dropped: {", ".join(dropped)}'
    if output_text.strip() == input_text.strip():
        return 'Fail', 'Not coming: output identical to source'
    return 'Pass', ''


def check_translation_result(output_text, input_text, api_result):
    """op=0 (translation): no per-word tokens are returned, so this only checks
    the sentence-level output — Fail if empty or left identical to the input."""
    if not output_text.strip():
        return 'Fail', 'Not coming: empty output'
    if output_text.strip() == input_text.strip():
        return 'Fail', 'Not coming: output identical to source'
    return 'Pass', ''


def main():
    src_wb = openpyxl.load_workbook('TransliterationData.xlsx')
    src_ws = src_wb.active

    records = []
    for r in range(2, src_ws.max_row + 1):
        text = src_ws.cell(r, 2).value or ''
        if not str(text).strip():
            continue
        records.append((src_ws.cell(r, 1).value, text))

    out_wb = openpyxl.Workbook()
    ws_translit = out_wb.active
    ws_translit.title = 'Transliteration_Op1'
    ws_translate = out_wb.create_sheet('Translation_Op0')
    headers = ['Sno', 'Pair', 'Input Text', 'Output', 'Result', 'Note']
    for ws in (ws_translit, ws_translate):
        for c, header in enumerate(headers, start=1):
            ws.cell(1, c, header).font = BOLD

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_file = f'TransliterationData_Results_{timestamp}.xlsx'

    def save():
        try:
            out_wb.save(out_file)
            return True
        except PermissionError:
            print(f'WARNING: {out_file} is open elsewhere — skipping this checkpoint save.')
            return False

    english_text = {sno: text for sno, text in records}
    # op=0 output produced for a source language other than english, keyed by
    # (lang, sno) — used as the real source text for pairs whose source isn't
    # english (e.g. hindi->urdu needs actual Hindi text, not the English one).
    translated_text = {}

    row_translit = 2
    row_translate = 2

    for src_lang, tgt_lang, engine, note in PAIRS:
        pair_label = f'{src_lang.title()}-{tgt_lang.title()}'
        print(f'--- {pair_label} (engine={engine}) ---')

        for sno, _ in records:
            if src_lang == 'english':
                input_text = english_text[sno]
            else:
                input_text = translated_text.get((src_lang, sno))
                if input_text is None:
                    print(f'  Sno={sno} skipped: no {src_lang} source text available yet')
                    continue

            try:
                try:
                    api_result0 = call_api(input_text, src_lang, tgt_lang, '0')
                    output0 = api_result0.get('outputText', '')
                    result0, reason0 = check_translation_result(output0, input_text, api_result0)
                except Exception as e:
                    output0, result0, reason0 = f'ERROR: {e}', 'Fail', 'API error'

                if tgt_lang != 'english':
                    translated_text[(tgt_lang, sno)] = output0

                ws_translate.cell(row_translate, 1, sno)
                ws_translate.cell(row_translate, 2, pair_label)
                ws_translate.cell(row_translate, 3, xl_safe(input_text))
                ws_translate.cell(row_translate, 4, xl_safe(output0))
                cell0 = ws_translate.cell(row_translate, 5, f'{result0} ({reason0})' if reason0 else result0)
                cell0.fill = GREEN if result0 == 'Pass' else RED
                ws_translate.cell(row_translate, 6, note or '')
                row_translate += 1

                time.sleep(0.15)

                try:
                    api_result1 = call_api(input_text, src_lang, tgt_lang, '1')
                    output1 = api_result1.get('outputText', '')
                    result1, reason1 = check_transliteration_result(output1, input_text, api_result1)
                except Exception as e:
                    output1, result1, reason1 = f'ERROR: {e}', 'Fail', 'API error'

                ws_translit.cell(row_translit, 1, sno)
                ws_translit.cell(row_translit, 2, pair_label)
                ws_translit.cell(row_translit, 3, xl_safe(input_text))
                ws_translit.cell(row_translit, 4, xl_safe(output1))
                cell1 = ws_translit.cell(row_translit, 5, f'{result1} ({reason1})' if reason1 else result1)
                cell1.fill = GREEN if result1 == 'Pass' else RED
                ws_translit.cell(row_translit, 6, note or '')
                row_translit += 1

                print(f'Sno={sno} {pair_label} translate={result0} translit={result1}', flush=True)
            except Exception as e:
                # Never let one bad record (e.g. an unwritable Excel cell)
                # take down the whole multi-hundred-call run.
                print(f'Sno={sno} {pair_label} SKIPPED due to unexpected error: {e}', flush=True)

            time.sleep(0.15)

        save()

    if save():
        print(f'\nSaved: {out_file}')
    else:
        # The primary file is locked (e.g. open in Excel) and every retry above
        # failed too — fall back to a fresh filename so the full run's data
        # (all pairs, both ops, both sheets) is never silently lost.
        fallback_file = f'TransliterationData_Results_{timestamp}_final.xlsx'
        out_wb.save(fallback_file)
        print(f'\n{out_file} stayed locked throughout — saved complete results to: {fallback_file}')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
