#!/usr/bin/env python3
"""Guard the Phase 1 string helper review anchors against direct helper drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
STRING_HELPER_REL = Path("tools/lib/string.zig")

EXPECTED_STRING_SOURCE_SYMBOLS = [
    "pub fn sysfsStreq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn sysfs_streq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn sysfsMatchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn sysfs_match_string(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn matchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn match_string(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn strnchr(buf: []const u8, count: usize, needle: u8) ?usize {",
    "pub fn strnlen(buf: []const u8, count: usize) usize {",
    "pub fn strchr(buf: []const u8, needle: u8) ?usize {",
    "pub fn strrchr(buf: []const u8, needle: u8) ?usize {",
    "pub fn strnchrNul(buf: []const u8, count: usize, needle: u8) usize {",
    "pub fn strnchrnul(buf: []const u8, count: usize, needle: u8) usize {",
    "pub fn strchrNul(buf: []const u8, needle: u8) usize {",
    "pub fn strchrnul(buf: []const u8, needle: u8) usize {",
]

EXPECTED_HELPER_TEST_ANCHORS = [
    'test "strtobool accepts common Linux forms"',
    'test "strlcpy copies and returns the source length"',
    'test "strscpy keeps NUL termination and reports truncation with -E2BIG"',
    'test "strscpyPad zero-pads the tail after a short source"',
    'test "strscpyPad stops at embedded NUL and pads the remaining tail"',
    'test "strscpyPad preserves strscpy truncation semantics"',
    'test "strscpy_pad mirrors strscpyPad padding semantics"',
    'test "strscpy and strscpyPad keep one-byte destinations terminated"',
    'test "streq matches C-string equality semantics"',
    'test "skip trim remove and replace spaces work in place"',
    'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
    'test "strreplace mirrors replaceChar C-string semantics"',
    'test "strHasPrefix returns the matched prefix length with C-string semantics"',
    'test "strHasSuffix returns the matched suffix length with C-string semantics"',
    'test "strstarts mirrors the header-level prefix helper"',
    'test "strEndsWith honors C-string boundaries"',
    'test "kbasename returns the final path component with C-string semantics"',
    'test "sysfsStreq treats trailing newline and NUL as equivalent"',
    'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
    'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
    'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
    'test "matchString finds C-string matches and preserves first-match order"',
    'test "match_string mirrors matchString for empty and matched lists"',
    'test "memdup and memchrInv preserve byte content"',
    'test "memchr_inv mirrors memchrInv byte-search semantics"',
    'test "memchrInv keeps long-buffer first-dirty-byte results stable"',
    'test "memchrInv follows the earliest dirty byte as long buffers change"',
    'test "memchrInv dirty-word shortcut handles zero-value scans at word boundaries"',
    'test "memchrInv zero-value scans keep the earliest dirty byte across every prefix alignment"',
    'test "memchrInv keeps the earliest dirty byte for long non-zero scans across alignments"',
    'test "memchrInv keeps the earliest dirty byte for long zero-value scans across alignments"',
    'test "memchrInv short zero-value scans stay byte-accurate"',
    'test "memchrInv keeps the earliest dirty byte across the fast-path cutoff"',
    'test "memparse handles decimal hexadecimal octal and suffixes"',
    'test "memparse keeps original rest when sign is not followed by digits"',
    'test "memparse saturates signed overflow instead of trapping"',
    'test "memparse clamps explicit positive signed overflow"',
    'test "memparse keeps signed values and their trailing rest aligned"',
    'test "memparse consumes suffix after saturation"',
    'test "memparse applies suffixes before signed clamping"',
    'test "strchr mirrors full-length C-string searches"',
    'test "strrchr finds the last in-range match with C-string semantics"',
    'test "strnchr honors count and C-string boundaries"',
    'test "strnlen honors count and C-string boundaries"',
    'test "strnchrNul returns the first match, NUL, or count boundary"',
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in (STRING_HELPER_REL,):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, STRING_HELPER_REL)

    for symbol in EXPECTED_STRING_SOURCE_SYMBOLS:
        failures.extend(
            require_exact_occurrence(helper_text, f"string_source:{symbol}", symbol)
        )

    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        failures.extend(
            require_exact_occurrence(helper_text, f"string_helper:{anchor}", anchor)
        )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_file(
        root,
        STRING_HELPER_REL,
        "\n".join(EXPECTED_STRING_SOURCE_SYMBOLS + EXPECTED_HELPER_TEST_ANCHORS) + "\n",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-string-review-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for item in failures:
                print(item)
            return 1
        case_count += 1

    mutation_specs = [
    ]
    mutation_specs.extend(
        (f"source_symbol_{idx}_{kind}", ("source_symbol", symbol), kind)
        for idx, symbol in enumerate(EXPECTED_STRING_SOURCE_SYMBOLS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (f"helper_anchor_{idx}_{kind}", ("helper_anchor", anchor), kind)
        for idx, anchor in enumerate(EXPECTED_HELPER_TEST_ANCHORS)
        for kind in ("remove", "duplicate")
    )
    for name, target, kind in mutation_specs:
        with tempfile.TemporaryDirectory(prefix=f"phase1-string-review-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if isinstance(target, tuple) and target[0] == "source_symbol":
                path = root / STRING_HELPER_REL
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(marker + "\n", "", 1)
                else:
                    text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                path.write_text(text, encoding="utf-8")
            else:
                path = root / STRING_HELPER_REL
                assert isinstance(target, tuple) and target[0] == "helper_anchor"
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(marker + "\n", "", 1)
                else:
                    text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                path.write_text(text, encoding="utf-8")

            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1
            case_count += 1

    print("PHASE1_STRING_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_STRING_REVIEW_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-string-review-packet:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())