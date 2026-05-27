#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from collections import defaultdict

DECL_RE = re.compile(r"^(?:pub\s+)?(fn|const)\s+([A-Za-z_][A-Za-z0-9_]*)\b")

DEFAULT_FILES = (
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/string.zig",
    "tools/lib/rbtree.zig",
)


def top_level_declarations(text: str) -> list[tuple[int, str, str]]:
    declarations: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.startswith((" ", "\t")):
            continue
        match = DECL_RE.match(line)
        if match:
            declarations.append((lineno, match.group(1), match.group(2)))
    return declarations


def duplicate_report(path: pathlib.Path) -> list[str]:
    seen: dict[str, list[int]] = defaultdict(list)
    for lineno, _kind, name in top_level_declarations(path.read_text(encoding="utf-8")):
        seen[name].append(lineno)

    problems: list[str] = []
    for name, lines in sorted(seen.items()):
        if len(lines) > 1:
            rendered = ", ".join(str(line) for line in lines)
            problems.append(f"{path}: duplicate top-level declaration `{name}` at lines {rendered}")
    return problems


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect duplicate top-level Zig helper declarations in Phase 1 host-side helper files."
    )
    parser.add_argument("paths", nargs="*", help="Files to scan. Defaults to the Phase 1 helper set.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw_paths = args.paths or list(DEFAULT_FILES)
    paths = [pathlib.Path(path) for path in raw_paths]

    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        for path in missing:
            print(f"missing file: {path}", file=sys.stderr)
        return 2

    problems: list[str] = []
    for path in paths:
        problems.extend(duplicate_report(path))

    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1

    print(f"ok: scanned {len(paths)} Phase 1 helper file(s) with no duplicate top-level declarations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
