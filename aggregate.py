import json
from pathlib import Path

from validation import Schema, aggregate_builders

root = Path(__file__).resolve().parent
output_path = root / "builders.json"

schema = Schema(root)
builders = aggregate_builders(root, schema)

with output_path.open("w", encoding="utf-8") as f:
    json.dump(dict(sorted(builders.items())), f, indent=4)
    f.write("\n")
