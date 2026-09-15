"""Validate every record on both boards against the JSON schemas.

The validator in `oifmd` checks the spec's conformance list; this checks
that the published schemas agree with what the repository actually ships.
A disagreement means one of them is wrong.
"""
from __future__ import annotations

import datetime as _dt
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = {n: Draft202012Validator(json.loads((ROOT / "schema" / f"{n}.schema.json").read_text()))
           for n in ("board", "column", "issue", "comment")}
RESERVED = {"column.md", "index.md", "log.md"}


def jsonable(value):
    """Project YAML-native types onto the JSON types the schemas describe.

    An unquoted `created: 2026-09-13T05:00:00Z` parses as a datetime, not a
    string. Implementers hit the same thing, so the spec says so too.
    """
    if isinstance(value, (_dt.datetime, _dt.date)):
        return value.isoformat().replace("+00:00", "Z")
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [jsonable(v) for v in value]
    return value


def frontmatter(path: Path) -> dict | None:
    text = path.read_text()
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    return jsonable(yaml.safe_load(text[4:end]) or {}) if end > 0 else None


def main() -> int:
    errors = 0
    for board in (ROOT / "board", ROOT / "examples" / "minimal"):
        targets: list[tuple[Path, str]] = [(board / "board.md", "board")]
        targets += [(p, "column") for p in board.glob("issues/*/column.md")]
        targets += [(p, "issue") for p in board.glob("issues/*/*.md") if p.name not in RESERVED]
        targets += [(p, "comment") for p in board.glob("comments/**/*.md") if p.name not in RESERVED]
        for path, kind in targets:
            data = frontmatter(path)
            if data is None:
                print(f"error: {path.relative_to(ROOT)}: no frontmatter")
                errors += 1
                continue
            for e in SCHEMAS[kind].iter_errors(data):
                print(f"error: {path.relative_to(ROOT)}: {kind}: {e.message}")
                errors += 1
        print(f"{board.relative_to(ROOT)}: {len(targets)} record(s) checked")
    print(f"{errors} schema error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
