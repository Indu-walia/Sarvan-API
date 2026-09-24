"""
One-shot workflow for a newly added data file in this folder:

    python process_new_file.py <new_file.xlsx>

It auto-detects the Sno / text / Contains (/ NotContains) columns from the
file's header row, builds a language-wise version (<name>_LangWise.xlsx —
one row per test case x per TARGET_LANGS language), then immediately runs
validate_brandname.py against that generated file.

Column detection is header-based (case-insensitive), not position-based, so
it works across differently-shaped input files:
  Sno column        -> header contains "sno"
  Contains column   -> header is exactly "contains" (-> BrandName)
  NotContains column -> header contains "not" and "contains" (optional)
  text column       -> header is "text"/"input text", else contains
                        "sentence" or "title"
If detection is ambiguous, it prints the headers it found and stops rather
than guessing wrong.
"""
import re
import sys
import subprocess
import openpyxl
from openpyxl.styles import Font

TARGET_LANGS = ['Hindi', 'Tamil', 'Malayalam', 'Telugu', 'Marathi']


def find_column(headers, patterns):
    for pattern in patterns:
        for idx, h in enumerate(headers, start=1):
            if h and pattern.search(str(h)):
                return idx
    return None


def build_langwise(src_path):
    src_wb = openpyxl.load_workbook(src_path)
    src_ws = src_wb.worksheets[0]

    headers = [src_ws.cell(1, c).value for c in range(1, src_ws.max_column + 1)]

    sno_col = find_column(headers, [re.compile(r'sno', re.I)])
    contains_col = find_column(headers, [re.compile(r'^\s*contains\s*$', re.I)])
    notcontains_col = find_column(headers, [re.compile(r'not\s*contains', re.I)])
    text_col = find_column(headers, [
        re.compile(r'^\s*(input\s*)?text\s*$', re.I),
        re.compile(r'sentence', re.I),
        re.compile(r'title', re.I),
    ])

    if not sno_col or not contains_col or not text_col:
        print(f'Could not auto-detect required columns in {src_path!r}. Headers found:')
        for i, h in enumerate(headers, start=1):
            print(f'  col {i}: {h!r}')
        print(f'Detected -> Sno: {sno_col}, text: {text_col}, '
              f'Contains: {contains_col}, NotContains: {notcontains_col}')
        sys.exit(1)

    print(f'Detected columns -> Sno: col {sno_col} ({headers[sno_col-1]!r}), '
          f'text: col {text_col} ({headers[text_col-1]!r}), '
          f'Contains: col {contains_col} ({headers[contains_col-1]!r}), '
          f'NotContains: {"col " + str(notcontains_col) + " (" + repr(headers[notcontains_col-1]) + ")" if notcontains_col else "none found"}')

    rows = []
    for r in range(2, src_ws.max_row + 1):
        text = src_ws.cell(r, text_col).value
        if not text or not str(text).strip():
            continue
        rows.append((
            src_ws.cell(r, sno_col).value,
            text,
            src_ws.cell(r, contains_col).value,
            src_ws.cell(r, notcontains_col).value if notcontains_col else None,
        ))

    out_wb = openpyxl.Workbook()
    ws = out_wb.active
    ws.title = 'Data'
    out_headers = ['Sno', 'text', 'Language', 'BrandName', 'NotContains']
    for c, h in enumerate(out_headers, start=1):
        ws.cell(1, c, h).font = Font(bold=True)

    row_idx = 2
    for sno, text, brand_name, not_contain in rows:
        for lang in TARGET_LANGS:
            ws.cell(row_idx, 1, sno)
            ws.cell(row_idx, 2, text)
            ws.cell(row_idx, 3, lang)
            ws.cell(row_idx, 4, brand_name)
            ws.cell(row_idx, 5, not_contain)
            row_idx += 1

    stem = src_path.rsplit('.', 1)[0]
    out_path = f'{stem}_LangWise.xlsx'
    out_wb.save(out_path)
    print(f'Wrote {row_idx - 2} rows ({len(rows)} items x {len(TARGET_LANGS)} languages) to {out_path}')
    return out_path


def main():
    if len(sys.argv) < 2:
        print('Usage: python process_new_file.py <file1.xlsx> [file2.xlsx ...]')
        sys.exit(1)

    for src_path in sys.argv[1:]:
        print(f'\n===== {src_path} =====')
        langwise_path = build_langwise(src_path)

        print(f'\nRunning validate_brandname.py against {langwise_path} ...\n')
        subprocess.run([sys.executable, 'validate_brandname.py', langwise_path], check=True)


if __name__ == '__main__':
    main()
