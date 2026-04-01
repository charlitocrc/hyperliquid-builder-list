#!/usr/bin/env python3
import sys
from pathlib import Path

from validation import validate_repo

root = Path(__file__).resolve().parent
errors = validate_repo(root)
for line in errors:
    print(line, file=sys.stderr)
sys.exit(1 if errors else 0)
