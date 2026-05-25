#!/usr/bin/env python3
"""Guard the current Phase 1 string strlcat helper-local anchor packet against drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
STRING_HELPER_REL = Path("tools/lib/string.zig")

REQUIRED_SYMBOLS = (
    "pub fn strlcat(dest: []u8, src: []const u8) usize {",
    "const src_len = cStringLen(src);",
    "const dest_len = strnlen(dest, dest.len);",
    "return dest.len + src_len;",
    "const copy_len = @min(src_len, dest.len - dest_len - 1);",
    "dest[dest_len + copy_len] = 0;",
    "return dest_len + src_len;",
)

REQUIRED_TEST_ANCHORS = (
    'test "strlcat appends within the destination size and reports the attempted length"',
    'test "strlcat truncates with a terminator and keeps the full attempted length"',
    'test "strlcat treats an unterminated destination as full"',
    'test "strlcat handles a zero-length destination buffer"',
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def helper_path(root: Path) -> Path:
    return root / STRING_HELPER_REL


def collect_failures(root: Path) -> list[str]:
    path = helper_path(root)
    if not path.exists():
        return [f"missing_file:{STRING_HELPER_REL.as_posix()}"]

    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    for symbol in REQUIRED_SYMBOLS:
        count = text.count(symbol)
        if count != 1:
            failures.append(f"string_strlcat_symbol:{symbol}:expected=1:actual={count}")
    for anchor in REQUIRED_TEST_ANCHORS:
        count = text.count(anchor)
        if count != 1:
            failures.append(f"string_strlcat_anchor:{anchor}:expected=1:actual={count}")
    return failures


def sample_helper_text() -> str:
    symbol_lines = "\n".join(REQUIRED_SYMBOLS)
    test_lines = "\n".join(REQUIRED_TEST_ANCHORS)
    return f"{symbol_lines}\n\n{test_lines}\n"


def write_sample_root(root: Path) -> None:
    path = helper_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sample_helper_text(), encoding="utf-8")


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="phase1-string-strlcat-") as tmp:
        root = Path(tmp)

        failures = collect_failures(root)
        if failures != [f"missing_file:{STRING_HELPER_REL.as_posix()}"]:
            print("self-test:missing-file:unexpected-result")
            for item in failures:
                print(item)
            return 1
        case_count += 1

        write_sample_root(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:baseline:unexpected-failures")
            for item in failures:
                print(item)
            return 1
        case_count += 1

        helper = helper_path(root)
        text = helper.read_text(encoding="utf-8")
        text = text.replace(REQUIRED_SYMBOLS[3] + "\n", "", 1)
        helper.write_text(text, encoding="utf-8")
        failures = collect_failures(root)
        expected = f"string_strlcat_symbol:{REQUIRED_SYMBOLS[3]}:expected=1:actual=0"
        if expected not in failures:
            print("self-test:missing-symbol:unexpected-result")
            for item in failures:
                print(item)
            return 1
        case_count += 1

        write_sample_root(root)
        text = helper.read_text(encoding="utf-8")
        duplicated = REQUIRED_TEST_ANCHORS[0]
        text = text.replace(duplicated + "\n", duplicated + "\n" + duplicated + "\n", 1)
        helper.write_text(text, encoding="utf-8")
        failures = collect_failures(root)
        expected = f"string_strlcat_anchor:{duplicated}:expected=1:actual=2"
        if expected not in failures:
            print("self-test:duplicate-anchor:unexpected-result")
            for item in failures:
                print(item)
            return 1
        case_count += 1

    print("PHASE1_STRING_STRLCAT_ANCHORS_SELF_TEST=pass")
    print(f"PHASE1_STRING_STRLCAT_ANCHORS_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root used for validation")
    parser.add_argument(
        "--write-sample-root",
        help="write a minimal sample tree to this directory and exit",
    )
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.write_sample_root:
        root = Path(args.write_sample_root).resolve()
        write_sample_root(root)
        print(f"PHASE1_STRING_STRLCAT_ANCHORS_SAMPLE_ROOT={root}")
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("PHASE1_STRING_STRLCAT_ANCHORS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
