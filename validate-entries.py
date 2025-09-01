import json
import sys
import os
from jsonschema import validate, ValidationError

# Load schema
with open("echoboot_schema.json", "r") as s:
    schema = json.load(s)

# Load the target JSON file
target_file = sys.argv[1] if len(sys.argv) > 1 else "debian.json"
if not os.path.exists(target_file):
    print(f"[ERROR] File not found: {target_file}")
    sys.exit(1)

with open(target_file, "r") as f:
    entries = json.load(f)

# Validate each entry
for i, entry in enumerate(entries):
    try:
        validate(instance=entry, schema=schema)
    except ValidationError as ve:
        print(f"[FAIL] Entry {i+1}: {ve.message}")
    else:
        print(f"[OK] Entry {i+1}: {entry['label']}")
