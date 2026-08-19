#!/usr/bin/env python3
import sys
import requests


def main():
    if len(sys.argv) < 3:
        print("Usage: python delete_indices_by_keys.py <es_base> <comma-separated-keys>")
        return
    es = sys.argv[1].rstrip('/')
    keys = [k.strip().lower() for k in sys.argv[2].split(',') if k.strip()]
    try:
        r = requests.get(f"{es}/_cat/indices?format=json", timeout=30)
        r.raise_for_status()
    except Exception as e:
        print("Failed to list indices:", e)
        return
    try:
        indices = r.json()
    except Exception:
        print("Failed to parse indices response")
        return
    matched = [idx['index'] for idx in indices if any(k in idx['index'].lower() for k in keys)]
    if not matched:
        print("No indices matched the keys.")
        return
    print(f"Found {len(matched)} indices to delete:")
    for name in matched:
        print(" -", name)
    confirm = input("Type YES to proceed with deleting these indices: ")
    if confirm.strip() != 'YES':
        print("Aborted by user.")
        return
    for name in matched:
        try:
            resp = requests.delete(f"{es}/{name}")
            print(f"Delete {name}: {resp.status_code}")
        except Exception as e:
            print(f"Delete {name} failed: {e}")
    print("Finished.")

if __name__ == '__main__':
    main()
