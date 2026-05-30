#!/usr/bin/env python3
"""Guard the Phase 1 string strsep() helper anchors against review drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2]
STRING_HELPER_REL = Path("tools/lib/string.zig")


EXPECTED_STRSEP_ANCHORS = [
    "pub fn strsep(cursor: *?[]u8, delimiters: []const u8) ?[]u8 {",
    'test "strsep splits mutable C strings and preserves empty tokens"',
    'test "strsep respects C-string delimiter and source boundaries"',
    'test "strsep with an empty delimiter set returns the remaining C string once"',
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    helper_path = root / STRING_HELPER_REL
    if not helper_path.exists():
        return [f"missing_file:{STRING_HELPER_REL.as_posix()}"]

    helper_text = helper_path.read_text(encoding="utf-8")
    failures: list[str] = []
    for anchor in EXPECTED_STRSEP_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"string_strsep:{anchor}", anchor))
    return failures


def sample_helper_source() -> str:
    return "\n".join(EXPECTED_STRSEP_ANCHORS) + "\n"


def run_self_test() -> int:
    cases = [
        "missing_file:tools/lib/string.zig",
        'string_strsep:pub fn strsep(cursor: *?[]u8, delimiters: []const u8) ?[]u8 {:expected=1:actual=0',
        'string_strsep:test "strsep splits mutable C strings and preserves empty tokens":expected=1:actual=0',
        'string_strsep:test "strsep respects C-string delimiter and source boundaries":expected=1:actual=0',
        'string_strsep:test "strsep with an empty delimiter set returns the remaining C string once":expected=1:actual=0',
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_string_strsep_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        if cases[0] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-strsep:self-test:missing_helper_file")

        helper_path = tmp_root / STRING_HELPER_REL
        helper_path.parent.mkdir(parents=True)
        helper_path.write_text(sample_helper_source(), encoding="utf-8")
        if collect_failures(tmp_root):
            raise SystemExit("phase1-string-strsep:self-test:baseline")

        for index, expected in enumerate(cases[1:]):
            helper_path.write_text(sample_helper_source().replace(EXPECTED_STRSEP_ANCHORS[index] + "\n", "", 1), encoding="utf-8")
            if expected not in collect_failures(tmp_root):
                raise SystemExit(f"phase1-string-strsep:self-test:anchor_{index}")

    print("PHASE1_STRING_STRSEP_ANCHORS_SELF_TEST=pass")
    print(f"PHASE1_STRING_STRSEP_ANCHORS_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-string-strsep-anchors:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
