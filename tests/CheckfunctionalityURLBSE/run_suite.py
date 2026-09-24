"""
Runs the full Hindi-page functionality test suite (links, buttons/tabs, dropdown menus) against
every row in CheckfunctionalityURLBSEData.xlsx, then builds one Excel report per row.

Usage:
    python tests/CheckfunctionalityURLBSE/run_suite.py

To test a different page: open CheckfunctionalityURLBSEData.xlsx, edit/add a row's LanguageURL
column, save, and re-run this script - no code changes needed.

Requires playwright-cli on PATH and .playwright/cli.config.json (repo root) to exist - that config
disables Chromium's AutomationControlled flag, needed because some sites (e.g. bseindia.com) block
plain automated browsers via Akamai bot detection.
"""
import subprocess
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
DIR = Path(__file__).resolve().parent
CONFIG = str(ROOT / ".playwright" / "cli.config.json")
INPUT_XLSX = DIR / "CheckfunctionalityURLBSEData.xlsx"


def run(cmd, **kwargs):
    print(f"  $ {' '.join(cmd)}")
    # playwright-cli is an npm-installed .cmd shim on Windows; subprocess can't exec that directly
    # without going through the shell.
    return subprocess.run(cmd, cwd=str(ROOT), shell=(sys.platform == "win32"), **kwargs)


def run_probe(url, script_name, out_path, timeout):
    run(["playwright-cli", "close-all"])
    try:
        opened = run(["playwright-cli", "open", "--browser=chrome", "--headed", f"--config={CONFIG}", url], timeout=60)
    except subprocess.TimeoutExpired:
        print("  Timed out opening the page.")
        return False
    if opened.returncode != 0:
        return False
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            result = run(
                ["playwright-cli", "run-code", f"--filename={DIR / script_name}"],
                stdout=f, stderr=subprocess.STDOUT, timeout=timeout,
            )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        # Checking hundreds of links can occasionally exceed the budget on slower sites; the partial
        # output already written to out_path is discarded by the caller (no usable JSON without the
        # final "### Result" marker), so just report and let the caller skip this row.
        print(f"  Timed out after {timeout}s. This site may have more/slower links than budgeted for - "
              f"try increasing the timeout in run_suite.py if this keeps happening.")
        return False


def read_url_rows():
    wb = openpyxl.load_workbook(INPUT_XLSX)
    ws = wb.active
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[4]:
            continue
        rows.append({"sno": row[0], "description": row[1], "language": row[2], "english_url": row[3], "hindi_url": row[4]})
    return rows


def main():
    rows = read_url_rows()
    if not rows:
        print(f"No rows with a LanguageURL found in {INPUT_XLSX}")
        sys.exit(1)

    for row in rows:
        url = row["hindi_url"]
        print(f"\n=== Row {row['sno']}: {row['description']} ===")
        print(f"URL: {url}")

        print("[1/3] Functional probe (links + buttons/tabs)...")
        ok = run_probe(url, "bse_functional_probe.js", DIR / "hindi_probe_result.txt", timeout=900)
        if not ok:
            print("  Functional probe failed (page may have loaded blank - this happens occasionally; re-run this row).")
            continue

        print("[2/3] Dropdown-menu probe...")
        run_probe(url, "bse_dropdown_probe.js", DIR / "hindi_dropdown_result.txt", timeout=600)
        run(["playwright-cli", "close-all"])

        print("[3/3] Building Excel report...")
        run([sys.executable, str(DIR / "extract_json.py")], check=True)
        run([sys.executable, str(DIR / "build_report.py")], check=True)

    print("\nDone.")


if __name__ == "__main__":
    main()
