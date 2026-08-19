#!/usr/bin/env python3
import sys
import requests

if len(sys.argv) < 3:
    print("Usage: python list_indices_by_keys.py <es_base> <comma-separated-keys>")
    sys.exit(2)

es = sys.argv[1].rstrip('/')
keys = [k.strip().lower() for k in sys.argv[2].split(',') if k.strip()]
try:
    r = requests.get(f"{es}/_cat/indices?format=json", timeout=30)
    r.raise_for_status()
    indices = r.json()
except Exception as e:
    print("Error querying ES:", e)
    sys.exit(1)

matches = [idx['index'] for idx in indices if any(k in idx['index'].lower() for k in keys)]
if not matches:
    print("No indices matched the keys.")
else:
    print(f"Found {len(matches)} matching indices:")
    for m in matches:
        print(' -', m)
