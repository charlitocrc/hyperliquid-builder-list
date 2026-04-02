import json
import re
from pathlib import Path

from eth_utils import is_address, to_checksum_address

# Matches a 42-char hex address string (any casing) for path validation.
_ADDRESS_STEM = re.compile(r"^0x[0-9a-fA-F]{40}$")


def eip55_address_stem_issue(stem: str) -> str | None:
    """
    Return an error message if `stem` is not a valid EIP-55 checksummed address,
    or None if it is valid.
    """
    if not _ADDRESS_STEM.fullmatch(stem):
        return "must be `0x` followed by exactly 40 hexadecimal characters"
    if not is_address(stem):
        return "is not a valid EVM address"
    expected = to_checksum_address(stem)
    if stem != expected:
        return f"must be EIP-55 checksummed (expected {expected})"
    return None


class Schema:
    def __init__(self, root: Path):
        self.root = root
        with (root / "blank.json").open(encoding="utf-8") as f:
            blank = json.load(f)
        with (root / "categories.json").open(encoding="utf-8") as f:
            self.valid_categories = set(json.load(f))
        self.allowed_top_keys = set(blank.keys())
        self.social_keys = set(blank["socials"].keys())
        self.hex_color = re.compile(r"^#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$")

    def is_non_empty_str(self, value):
        return isinstance(value, str) and value.strip() != ""

    def valid_socials(self, value):
        if value is None:
            return True
        if not isinstance(value, dict):
            return False
        if not set(value.keys()) <= self.social_keys:
            return False
        return all(v is None or isinstance(v, str) for v in value.values())

    def valid_brand_color(self, value):
        if value is None:
            return True
        if not isinstance(value, str):
            return False
        return bool(self.hex_color.fullmatch(value))

    def entry_issues(self, raw):
        issues = []
        if not isinstance(raw, dict):
            return ["root must be a JSON object"]
        extra = set(raw.keys()) - self.allowed_top_keys
        if extra:
            issues.append(f"unknown keys: {sorted(extra)}")
        for key in ("id", "category", "name", "description", "url"):
            if key not in raw or not self.is_non_empty_str(raw[key]):
                issues.append(f"missing or empty {key!r}")
        if raw.get("category") not in self.valid_categories:
            issues.append(f"invalid category {raw.get('category')!r}")
        if "socials" in raw and not self.valid_socials(raw["socials"]):
            issues.append("invalid socials (wrong keys or non-string values)")
        if "brand_color" in raw and not self.valid_brand_color(raw["brand_color"]):
            issues.append("invalid brand_color (expected null or #RGB / #RRGGBB hex)")
        return issues

    def valid_entry(self, raw):
        return len(self.entry_issues(raw)) == 0


def aggregate_builders(root: Path, schema: Schema):
    data_dir = root / "data"
    assets_dir = root / "assets"
    builders = {}
    seen_ids = set()
    for path in sorted(data_dir.glob("*.json")):
        address = path.stem
        asset_dir = assets_dir / address
        logo_png = asset_dir / "logo.png"
        logo_svg = asset_dir / "logo.svg"
        if not (logo_png.is_file() or logo_svg.is_file()):
            continue
        with path.open(encoding="utf-8") as f:
            raw = json.load(f)
        if not schema.valid_entry(raw):
            continue
        builder_id = raw["id"]
        if builder_id in seen_ids:
            continue
        seen_ids.add(builder_id)
        builders[address] = raw
    return builders


def validate_repo(root: Path):
    schema = Schema(root)
    errors = []
    data_dir = root / "data"
    assets_dir = root / "assets"
    id_to_rel = {}
    for path in sorted(data_dir.glob("*.json")):
        address = path.stem
        rel = path.relative_to(root)
        stem_issue = eip55_address_stem_issue(address)
        if stem_issue:
            errors.append(f"{rel}: filename {stem_issue}")
        asset_dir = assets_dir / address
        has_logo = (asset_dir / "logo.png").is_file() or (asset_dir / "logo.svg").is_file()
        if not has_logo:
            errors.append(f"{rel}: missing assets/{address}/logo.png or logo.svg")
        try:
            with path.open(encoding="utf-8") as f:
                raw = json.load(f)
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}: invalid JSON ({exc})")
            continue
        for line in schema.entry_issues(raw):
            errors.append(f"{rel}: {line}")
        if not isinstance(raw, dict) or not schema.valid_entry(raw):
            continue
        bid = raw["id"]
        if bid in id_to_rel:
            errors.append(f"{rel}: duplicate id {bid!r} (also in {id_to_rel[bid]})")
        else:
            id_to_rel[bid] = str(rel)
    if assets_dir.is_dir():
        for child in sorted(assets_dir.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            name = child.name
            if not _ADDRESS_STEM.fullmatch(name):
                continue
            issue = eip55_address_stem_issue(name)
            if issue:
                rel = child.relative_to(root)
                errors.append(f"{rel}: directory name {issue}")
    expected = aggregate_builders(root, schema)
    output_path = root / "builders.json"
    try:
        with output_path.open(encoding="utf-8") as f:
            actual = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"builders.json: cannot read ({exc})")
        return errors
    if actual != expected:
        errors.append("builders.json is out of date; run: python3 aggregate.py")
    return errors
