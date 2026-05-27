#!/usr/bin/env python3
"""Fail on duplicate top-level helper definitions or duplicate Zig test titles.

This script is intentionally narrow: it only scans the Phase 1 helper files that
the roadmap calls out for early host-helper parity work.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Iterable

TARGET_FILES = (
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/string.zig",
    "tools/lib/rbtree.zig",
)

TOP_LEVEL_DEF_RE = re.compile(
    r"^(pub\s+)?(?:inline\s+)?(?:extern\s+)?(?:export\s+)?"
    r"(fn|const|var)\s+([A-Za-z_][A-Za-z0-9_]*)\b"
)
TEST_RE = re.compile(r'^\s*test\s+"([^"]+)"')


def _iter_lines(path: Path) -> Iterable[tuple[int, str]]:
    with path.open("r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            yield number, line


def _scan_file(path: Path) -> list[str]:
    errors: list[str] = []
    defs: dict[str, list[int]] = defaultdict(list)
    tests: dict[str, list[int]] = defaultdict(list)
    depth = 0

    for line_number, raw_line in _iter_lines(path):
        stripped = raw_line.strip()

        if depth == 0:
            match = TOP_LEVEL_DEF_RE.match(stripped)
            if match is not None:
                kind = match.group(2)
                name = match.group(3)
                defs[f"{kind}:{name}"].append(line_number)

            test_match = TEST_RE.match(raw_line)
            if test_match is not None:
                tests[test_match.group(1)].append(line_number)

        # This is a conservative parity gate, not a full parser. Counting raw
        # braces is good enough for the targeted helper files and fixture tests.
        depth += raw_line.count("{")
        depth -= raw_line.count("}")
        if depth < 0:
            depth = 0

    for symbol, lines in sorted(defs.items()):
        if len(lines) > 1:
            errors.append(
                f"{path}: duplicate top-level definition `{symbol}` at lines "
                + ", ".join(str(line) for line in lines)
            )

    for title, lines in sorted(tests.items()):
        if len(lines) > 1:
            errors.append(
                f'{path}: duplicate test title "{title}" at lines '
                + ", ".join(str(line) for line in lines)
            )

    return errors


def scan_root(root: Path) -> list[str]:
    errors: list[str] = []
    missing: list[str] = []

    for relative in TARGET_FILES:
        target = root / relative
        if not target.exists():
            missing.append(relative)
            continue
        errors.extend(_scan_file(target))

    if missing:
        errors.append(
            "missing Phase 1 helper files: " + ", ".join(sorted(missing))
        )

    return errors


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)

        for relative in TARGET_FILES:
            _write(root / relative, "pub fn ok() void {}\n")

        clean_errors = scan_root(root)
        if clean_errors:
            print("self-test clean fixture unexpectedly failed", file=sys.stderr)
            for error in clean_errors:
                print(error, file=sys.stderr)
            return 1

        _write(
            root / "tools/lib/string.zig",
            (
                'pub fn alpha() void {}\n'
                'test "kept once" {}\n'
                'pub fn alpha() void {}\n'
                'test "kept once" {}\n'
            ),
        )

        duplicate_errors = scan_root(root)
        expected_fragments = (
            "duplicate top-level definition `fn:alpha`",
            'duplicate test title "kept once"',
        )

        for fragment in expected_fragments:
            if not any(fragment in error for error in duplicate_errors):
                print(
                    f"self-test did not observe expected fragment: {fragment}",
                    file=sys.stderr,
                )
                for error in duplicate_errors:
                    print(error, file=sys.stderr)
                return 1

    print("self-test passed")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check Zigux Phase 1 helper files for duplicate top-level helper "
            "definitions and duplicate Zig test titles."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="repository root containing tools/lib/",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run focused fixture-based self-tests",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.self_test:
        return run_self_test()

    errors = scan_root(args.root.resolve())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("Phase 1 helper duplicate scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
