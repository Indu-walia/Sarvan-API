#!/usr/bin/env python3
"""Upload the 12 test articles (6 languages each) N times in a row.

Each iteration: bump articleTitle only (articleVersion is left untouched
across all iterations) -> upload all 12 files -> clear the matching ES
indices for the two project keys, so the next iteration starts from a
clean state.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import requests

FILES = [
    "Anuvaad.json", "Anuvaad_2.json", "Anuvaad_3.json", "Anuvaad_4.json", "Anuvaad_5.json", "Anuvaad_6.json",
    "bajajmall-site", "bajajmall-site_2", "bajajmall-site_3", "bajajmall-site_4", "bajajmall-site_5", "bajajmallsite_6.json",
]

ES_URL = "http://20.192.26.81:9200"
ES_KEYS = [
    "929e-4237-1be7-d479-f5d5-a39d-3b71-553c",
    "7895-620f-fb0b-8853-0015-17c6-8b13-720a",
]


def bump_titles(input_dir: Path, loop_num: int) -> None:
    stamp = int(time.time() * 1000)
    for name in FILES:
        path = input_dir / name
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        article_id = data.get("articleId", path.stem)
        data["articleTitle"] = f"{article_id} loop{loop_num} {stamp}"
        with path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
    print(f"  Titles bumped (loop{loop_num}, stamp={stamp}); articleVersion left untouched")


def clear_es() -> None:
    for key in ES_KEYS:
        r = requests.get(f"{ES_URL}/_cat/indices/*{key}*?format=json", timeout=30)
        r.raise_for_status()
        for item in r.json():
            index = item["index"]
            docs = item.get("docs.count")
            resp = requests.delete(f"{ES_URL}/{index}", timeout=30)
            print(f"  Deleted {index} (had {docs} docs): {resp.status_code}")


def main() -> None:
    input_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Test data parallel processing")
    loops = int(sys.argv[2]) if len(sys.argv) > 2 else 4

    for loop_num in range(1, loops + 1):
        print(f"\n=== Loop {loop_num}/{loops} ===")

        print("Step 1: bump articleTitle")
        bump_titles(input_dir, loop_num)

        print("Step 2: upload")
        result = subprocess.run(
            [
                sys.executable, "submit_parallel.py",
                "--input-dir", str(input_dir),
                "--no-pre-clear",
                "--output-prefix", f"report_titleloop{loop_num}",
            ],
            check=False,
        )
        if result.returncode != 0:
            print(f"  Upload step exited with code {result.returncode}")

        print("Step 3: clear ES")
        clear_es()

    print(f"\nDone: {loops} loops completed.")


if __name__ == "__main__":
    main()
