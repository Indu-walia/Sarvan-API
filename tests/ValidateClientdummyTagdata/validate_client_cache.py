import sys
import warnings
import requests
import openpyxl
from datetime import datetime
from openpyxl.styles import PatternFill, Font

warnings.filterwarnings('ignore')

API_URL  = 'https://p9clientcacheapi.mox2.net.in/moxlocalization/moxtm/QAUpdateData'
AUTH_KEY = '3642-E582-D3CC-49FA-FC38-F64C-0EC0-BCBB'

GREEN = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
RED   = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
BOLD  = Font(bold=True)


def call_api(source_text, target_text, language, quality):
    payload = {
        'AuthKey': AUTH_KEY,
        'InLanguage': 'English',
        'Language': language,
        'Data': {
            'source_text': source_text,
            'target_text': target_text,
            'classification': 'Translation',
            'subClassification': 'Translation',
            'userName': 'pooja admin',
            'quality': int(quality) if quality else 1,
            'transFlag': 0
        }
    }
    resp = requests.post(API_URL, json=payload, timeout=30, verify=False)
    resp.raise_for_status()
    return resp.json()


def compare_text(expected, actual):
    """Full text comparison."""
    if expected is None or str(expected).strip() == '':
        return 'Pass'
    return 'Pass' if str(expected).strip() == str(actual).strip() else 'Fail'


def compare_quality(expected, actual):
    """Compare input quality vs response quality."""
    if expected is None:
        return 'Pass'
    try:
        return 'Pass' if int(expected) == int(actual) else 'Fail'
    except (TypeError, ValueError):
        return 'Fail'


def check_not_contains(not_contain_val, text):
    """Return Fail if any listed value IS found in text."""
    if not not_contain_val:
        return 'Pass'
    values = [v.strip() for v in str(not_contain_val).split(',') if v.strip()]
    for val in values:
        if val in str(text):
            return 'Fail'
    return 'Pass'


def main():
    # Input columns:
    # 1=Sno, 2=Description, 3=SourceText, 4=TargetText,
    # 5=Language, 6=InputQuality, 7=ExpectedOutputQuality,
    # 8=ExpectedSrcText, 9=ExpectedTgtText,
    # 10=ExpectedOriginalSrcNotContains, 11=ExpectedOriginalTgtNotContains

    in_wb = openpyxl.load_workbook('ClientCache_Input.xlsx', read_only=True)
    in_ws = in_wb.active

    out_wb = openpyxl.Workbook()
    out_ws = out_wb.active

    input_headers = [
        'Sno', 'Description',
        'SourceText', 'TargetText',
        'Language', 'InputQuality', 'ExpectedOutputQuality',
        'ExpectedSrcText', 'ExpectedTgtText',
        'ExpectedOriginalSrcNotContains', 'ExpectedOriginalTgtNotContains'
    ]
    result_headers = [
        'ActualSrcText',      'SrcText_Result',
        'ActualTgtText',      'TgtText_Result',
        'InputQuality',       'ResponseQuality',     'Quality_Result',
        'ActualOriginalSrc',  'OriginalSrc_NC_Result',
        'ActualOriginalTgt',  'OriginalTgt_NC_Result',
        'Overall_Result',     'FailReason'
    ]

    for col, h in enumerate(input_headers + result_headers, 1):
        cell = out_ws.cell(1, col, h)
        cell.font = BOLD

    result_start = len(input_headers) + 1

    for in_row, row_data in enumerate(in_ws.iter_rows(min_row=2, values_only=True), start=2):
        sno              = row_data[0]
        src_text         = (row_data[2] or '').strip().replace('\xa0', ' ').strip()
        tgt_text         = (row_data[3] or '').strip().replace('\xa0', ' ').strip()
        language         = row_data[4] or 'hindi'
        input_quality    = row_data[5]
        exp_out_quality  = row_data[6]
        exp_src_text     = row_data[7]
        exp_tgt_text     = row_data[8]
        exp_orig_src_nc  = row_data[9]
        exp_orig_tgt_nc  = row_data[10]

        if not src_text and not tgt_text:
            continue

        # Copy input columns to output
        for col, val in enumerate(row_data[:11], 1):
            out_ws.cell(in_row, col, val)

        print(f'Processing row {in_row} (Sno={sno})...', end=' ', flush=True)

        try:
            result = call_api(src_text, tgt_text, language, input_quality)
        except Exception as e:
            out_ws.cell(in_row, result_start, f'ERROR: {e}')
            print('ERROR')
            continue

        data = result.get('Data', {})

        actual_src_text     = data.get('Source_text', '')
        actual_tgt_text     = data.get('Target_text', '')
        actual_quality      = data.get('Quality', '')
        actual_original_src = data.get('Original_source_text', '')
        actual_original_tgt = data.get('Original_target_text', '')

        # 1. Full text match: Source_text
        src_result          = compare_text(exp_src_text, actual_src_text)

        # 2. Full text match: Target_text
        tgt_result          = compare_text(exp_tgt_text, actual_tgt_text)

        # 3. Quality: InputQuality sent vs Quality returned
        #    Hindi mismatch → Q5, Korean/Chinese mismatch → Q6
        quality_result      = compare_quality(exp_out_quality, actual_quality)

        # 4. Original_source_text must NOT contain <n1> (originals are never tagged)
        orig_src_nc_result  = check_not_contains(exp_orig_src_nc, actual_original_src)

        # 5. Original_target_text must NOT contain <n1>
        orig_tgt_nc_result  = check_not_contains(exp_orig_tgt_nc, actual_original_tgt)

        overall = 'Pass' if all(r == 'Pass' for r in [
            src_result, tgt_result, quality_result,
            orig_src_nc_result, orig_tgt_nc_result
        ]) else 'Fail'

        # Build fail reason
        reasons = []
        if src_result == 'Fail':
            reasons.append(f'SrcText: expected "{exp_src_text}" | actual "{actual_src_text}"')
        if tgt_result == 'Fail':
            reasons.append(f'TgtText: expected "{exp_tgt_text}" | actual "{actual_tgt_text}"')
        if quality_result == 'Fail':
            reasons.append(f'Quality: expected {exp_out_quality} | actual {actual_quality}')
        if orig_src_nc_result == 'Fail':
            reasons.append(f'OriginalSrc contains "{exp_orig_src_nc}"')
        if orig_tgt_nc_result == 'Fail':
            reasons.append(f'OriginalTgt contains "{exp_orig_tgt_nc}"')
        fail_reason = ' | '.join(reasons) if reasons else ''

        result_values = [
            actual_src_text,     src_result,
            actual_tgt_text,     tgt_result,
            input_quality,       actual_quality,    quality_result,
            actual_original_src, orig_src_nc_result,
            actual_original_tgt, orig_tgt_nc_result,
            overall,             fail_reason
        ]
        for idx, val in enumerate(result_values):
            cell = out_ws.cell(in_row, result_start + idx, val)
            if val in ('Pass', 'Fail'):
                cell.fill = GREEN if val == 'Pass' else RED

        print(f'Src={src_result}, Tgt={tgt_result}, Quality={quality_result}, '
              f'OrigSrc={orig_src_nc_result}, OrigTgt={orig_tgt_nc_result} → {overall}')

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_file = f'ClientCache_Results_{timestamp}.xlsx'
    out_wb.save(out_file)
    print(f'\nSaved: {out_file}')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
