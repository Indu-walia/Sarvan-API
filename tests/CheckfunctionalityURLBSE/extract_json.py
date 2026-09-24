import json


def extract_json(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    start = text.index("### Result") + len("### Result")
    end = text.index("\n### ", start)
    return json.loads(text[start:end].strip())


hi = extract_json("tests/CheckfunctionalityURLBSE/hindi_probe_result.txt")
json.dump(hi, open("tests/CheckfunctionalityURLBSE/hindi_probe.json", "w", encoding="utf-8"), ensure_ascii=False)
print("extracted hindi_probe.json")
