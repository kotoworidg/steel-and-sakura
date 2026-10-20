"""Print actual table and field definitions from an RPFM RON schema file."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def matching_delimiter(text: str, start: int, opening: str, closing: str) -> int:
    depth = 0
    quoted = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return index
    raise ValueError(f"unclosed {opening!r} starting at character {start}")


def get_array(text: str, match: re.Match[str]) -> str:
    start = text.find("[", match.start())
    end = matching_delimiter(text, start, "[", "]")
    return text[start + 1 : end]


def definitions(schema: str, table: str) -> list[tuple[int, list[tuple[str, str]]]]:
    pattern = re.compile(rf'(?m)^\s*"{re.escape(table)}"\s*:\s*\[')
    match = pattern.search(schema)
    if not match:
        raise KeyError(f"table not found: {table}")
    table_block = get_array(schema, match)
    versions: list[tuple[int, list[tuple[str, str]]]] = []
    version_pattern = re.compile(r"\(\s*version:\s*(\d+)\s*,")
    version_matches = list(version_pattern.finditer(table_block))
    for index, version_match in enumerate(version_matches):
        start = version_match.start()
        end = (
            version_matches[index + 1].start()
            if index + 1 < len(version_matches)
            else len(table_block)
        )
        version_block = table_block[start:end]
        fields_match = re.search(r"fields\s*:\s*\[", version_block)
        if not fields_match:
            versions.append((int(version_match.group(1)), []))
            continue
        fields_text = get_array(version_block, fields_match)
        fields = re.findall(
            r'name\s*:\s*"([^"\r\n]+)"\s*,\s*field_type\s*:\s*([A-Za-z0-9_]+)',
            fields_text,
        )
        versions.append((int(version_match.group(1)), fields))
    return versions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema", type=Path)
    parser.add_argument("tables", nargs="+", help="Exact schema table names")
    args = parser.parse_args()
    text = args.schema.read_text(encoding="utf-8")

    for table in args.tables:
        print(f"[{table}]")
        for version, fields in definitions(text, table):
            print(f"version {version}: {len(fields)} fields")
            for name, field_type in fields:
                print(f"  {name}: {field_type}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
