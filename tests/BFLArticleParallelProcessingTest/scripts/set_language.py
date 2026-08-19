#!/usr/bin/env python3
import json
import sys
from pathlib import Path

FILES = [
    "Anuvaad.json", "Anuvaad_2.json", "Anuvaad_3.json", "Anuvaad_4.json", "Anuvaad_5.json", "Anuvaad_6.json",
    "bajajmall-site", "bajajmall-site_2", "bajajmall-site_3", "bajajmall-site_4", "bajajmall-site_5", "bajajmallsite_6.json",
]

DEFAULT_LANGUAGES = "Hindi,Tamil,Malayalam,Telugu,Marathi,Kannada"


def main() -> None:
    if len(sys.argv) < 2:
        print(f'Usage: python set_language.py "<InputDir>" ["<comma,separated,languages>"]')
        print(f'Default languages if omitted: {DEFAULT_LANGUAGES}')
        return
    input_dir = Path(sys.argv[1])
    languages = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_LANGUAGES
    for name in FILES:
        path = input_dir / name
        if not path.exists():
            print(f"SKIP (not found): {path}")
            continue
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        old_lang = data.get("translationLanguage")
        data["translationLanguage"] = languages
        with path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
        print(f"{name}: {old_lang!r} -> {languages!r}")


if __name__ == "__main__":
    main()
