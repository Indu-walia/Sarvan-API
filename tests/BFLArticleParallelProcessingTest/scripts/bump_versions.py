#!/usr/bin/env python3
import json
import sys
import time
from pathlib import Path

FILES = [
    "Anuvaad.json", "Anuvaad_2.json", "Anuvaad_3.json", "Anuvaad_4.json", "Anuvaad_5.json", "Anuvaad_6.json",
    "bajajmall-site", "bajajmall-site_2", "bajajmall-site_3", "bajajmall-site_4", "bajajmall-site_5", "bajajmallsite_6.json",
]


def main() -> None:
    input_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Test data parallel processing")
    base = int(time.time() * 1000)
    for i, name in enumerate(FILES):
        path = input_dir / name
        if not path.exists():
            print(f"SKIP (not found): {path}")
            continue
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        old_version = data.get("articleVersion")
        new_version = base + i
        data["articleVersion"] = new_version
        with path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
        print(f"{name}: {old_version} -> {new_version}")


if __name__ == "__main__":
    main()
