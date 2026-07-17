"""Small TOML loader fallback for Skills Master registry files on Python 3.9+."""

import ast
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - depends on interpreter version
    tomllib = None


def _strip_comment(line):
    quote = None
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\" and quote:
            escaped = True
            continue
        if char in {'"', "'"}:
            quote = None if quote == char else (char if quote is None else quote)
            continue
        if char == "#" and quote is None:
            return line[:index]
    return line


def _parse_value(raw):
    value = raw.strip()
    if value == "true":
        return True
    if value == "false":
        return False
    if value.startswith("["):
        return ast.literal_eval(value)
    if value.startswith(('"', "'")):
        return ast.literal_eval(value)
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Unsupported TOML value: {value}") from exc


def _nested_table(document, dotted_name):
    table = document
    for part in dotted_name.split("."):
        table = table.setdefault(part, {})
    return table


def parse_registry_toml(text):
    """Parse the deterministic TOML subset used by skill registry v2."""
    document = {}
    current = document
    for line_number, original in enumerate(text.splitlines(), start=1):
        line = _strip_comment(original).strip()
        if not line:
            continue
        if line.startswith("[[") and line.endswith("]]" ):
            name = line[2:-2].strip()
            collection = document.setdefault(name, [])
            if not isinstance(collection, list):
                raise ValueError(f"Line {line_number}: {name} is already a table")
            current = {}
            collection.append(current)
            continue
        if line.startswith("[") and line.endswith("]"):
            current = _nested_table(document, line[1:-1].strip())
            continue
        if "=" not in line:
            raise ValueError(f"Line {line_number}: expected key = value")
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Line {line_number}: empty key")
        current[key] = _parse_value(raw_value)
    return document


def load_toml(path):
    path = Path(path)
    if tomllib is not None:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    return parse_registry_toml(path.read_text(encoding="utf-8"))
