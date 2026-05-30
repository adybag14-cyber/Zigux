#!/usr/bin/env python3
"""Guard the Phase 1 string search helper anchors against quiet drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
STRING_HELPER_REL = Path("tools/lib/string.zig")


EXPECTED_SEARCH_SYMBOLS = [
    "pub fn strstr(buf: []const u8, needle: []const u8) ?usize {",
    "pub fn strnstr(buf: []const u8, needle: []const u8, count: usize) ?usize {",
    "pub fn strchr(buf: []const u8, needle: u8) ?usize {",
    "pub fn strrchr(buf: []const u8, needle: u8) ?usize {",
    "pub fn strpbrk(buf: []const u8, accept: []const u8) ?usize {",
    "pub fn strspn(buf: []const u8, accept: []const u8) usize {",
    "pub fn strcspn(buf: []const u8, reject: []const u8) usize {",
    "pub fn strnchr(buf: []const u8, count: usize, needle: u8) ?usize {",
    "pub fn strnchrNul(buf: []const u8, count: usize, needle: u8) usize {",
    "pub fn strnchrnul(buf: []const u8, count: usize, needle: u8) usize {",
    "pub fn strchrNul(buf: []const u8, needle: u8) usize {",
    "pub fn strchrnul(buf: []const u8, needle: u8) usize {",
]


EXPECTED_SEARCH_TEST_ANCHORS = [
    'test "strstr mirrors full-length C-string substring searches"',
    'test "strnstr honors count and C-string boundaries"',
    'test "strchr mirrors full-length C-string searches"',
    'test "strrchr finds the last in-range match with C-string semantics"',
    'test "strchr and strrchr return the terminator index when searching for NUL"',
    'test "strpbrk finds the first accepted byte with C-string semantics"',
    'test "strspn counts the accepted prefix with C-string semantics"',
    'test "strcspn counts until the first rejected byte with C-string semantics"',
    'test "strnchr honors count and C-string boundaries"',
    'test "strnchr treats the NUL terminator as searchable within the count window"',
    'test "strnchrNul returns the first match, NUL, or count boundary"',
    'test "strchrNul and strchrnul return the first match or terminator boundary"',
]


SEARCH_REVIEW_MARKERS = [
    "strstr(\"abc\", &[_]u8{ 'b', 0, 'x' })",
    "strnstr(&[_]u8{ 'a', 0, 'b', 'c' }, \"bc\", 4)",
    "strnchr(\"abc\", 3, 0)",
    "strnchrNul(&[_]u8{ 'a', 0, 'b' }, 3, 'z')",
    "strchrNul(&[_]u8{ 'a', 0, 'b' }, 'z')",
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def require_once(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    helper_path = root / STRING_HELPER_REL
    if not helper_path.exists():
        return [f"missing_file:{STRING_HELPER_REL.as_posix()}"]

    helper_text = helper_path.read_text(encoding="utf-8")
    failures: list[str] = []
    for symbol in EXPECTED_SEARCH_SYMBOLS:
        failures.extend(require_once(helper_text, f"string_search_symbol:{symbol}", symbol))
    for anchor in EXPECTED_SEARCH_TEST_ANCHORS:
        failures.extend(require_once(helper_text, f"string_search_test:{anchor}", anchor))
    for marker in SEARCH_REVIEW_MARKERS:
        failures.extend(require_once(helper_text, f"string_search_review_marker:{marker}", marker))
    return failures


def sample_string_helper() -> str:
    lines = [
        "pub fn strstr(buf: []const u8, needle: []const u8) ?usize {",
        "pub fn strnstr(buf: []const u8, needle: []const u8, count: usize) ?usize {",
        "pub fn strchr(buf: []const u8, needle: u8) ?usize {",
        "pub fn strrchr(buf: []const u8, needle: u8) ?usize {",
        "pub fn strpbrk(buf: []const u8, accept: []const u8) ?usize {",
        "pub fn strspn(buf: []const u8, accept: []const u8) usize {",
        "pub fn strcspn(buf: []const u8, reject: []const u8) usize {",
        "pub fn strnchr(buf: []const u8, count: usize, needle: u8) ?usize {",
        "pub fn strnchrNul(buf: []const u8, count: usize, needle: u8) usize {",
        "pub fn strnchrnul(buf: []const u8, count: usize, needle: u8) usize {",
        "pub fn strchrNul(buf: []const u8, needle: u8) usize {",
        "pub fn strchrnul(buf: []const u8, needle: u8) usize {",
    ]
    lines.extend(EXPECTED_SEARCH_TEST_ANCHORS)
    lines.extend(SEARCH_REVIEW_MARKERS)
    return "\n".join(lines) + "\n"


def write_sample_repo(root: Path) -> Path:
    helper_path = root / STRING_HELPER_REL
    helper_path.parent.mkdir(parents=True, exist_ok=True)
    helper_path.write_text(sample_string_helper(), encoding="utf-8")
    return helper_path


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        helper_path = write_sample_repo(tmp_root)
        if collect_failures(tmp_root):
            raise SystemExit("phase1-string-search:self-test:clean_sample_failed")

        text = helper_path.read_text(encoding="utf-8").replace(EXPECTED_SEARCH_SYMBOLS[1] + "\n", "", 1)
        helper_path.write_text(text, encoding="utf-8")
        failures = collect_failures(tmp_root)
        if f"string_search_symbol:{EXPECTED_SEARCH_SYMBOLS[1]}:expected=1:actual=0" not in failures:
            raise SystemExit("phase1-string-search:self-test:missing_symbol")

        helper_path = write_sample_repo(tmp_root)
        text = helper_path.read_text(encoding="utf-8").replace(EXPECTED_SEARCH_TEST_ANCHORS[-1] + "\n", "", 1)
        helper_path.write_text(text, encoding="utf-8")
        failures = collect_failures(tmp_root)
        if f"string_search_test:{EXPECTED_SEARCH_TEST_ANCHORS[-1]}:expected=1:actual=0" not in failures:
            raise SystemExit("phase1-string-search:self-test:missing_test_anchor")

        helper_path = write_sample_repo(tmp_root)
        text = helper_path.read_text(encoding="utf-8").replace(SEARCH_REVIEW_MARKERS[0] + "\n", "", 1)
        helper_path.write_text(text, encoding="utf-8")
        failures = collect_failures(tmp_root)
        if f"string_search_review_marker:{SEARCH_REVIEW_MARKERS[0]}:expected=1:actual=0" not in failures:
            raise SystemExit("phase1-string-search:self-test:missing_review_marker")

    print("PHASE1_STRING_SEARCH_ANCHORS_SELF_TEST=pass")
    print("PHASE1_STRING_SEARCH_ANCHORS_SELF_TEST_CASE_COUNT=3")
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

    print("phase1-string-search-anchors:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
