#!/usr/bin/env python3
"""Guard Phase 1 string helper top-level definition uniqueness."""

from __future__ import annotations

import argparse
import re
import tempfile
from collections import defaultdict
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[3]
STRING_HELPER_REL = Path("tools/lib/string.zig")

DECL_RE = re.compile(r"^(?P<kind>pub fn|fn|pub const|const)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\b")
TEST_RE = re.compile(r'^test\s+"(?P<name>[^"]+)"')


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def helper_path(root: Path) -> Path:
    return root / STRING_HELPER_REL


def collect_failures(root: Path) -> list[str]:
    path = helper_path(root)
    if not path.exists():
        return [f"missing_file:{STRING_HELPER_REL.as_posix()}"]

    failures: list[str] = []
    decl_lines: dict[tuple[str, str], list[int]] = defaultdict(list)
    test_lines: dict[str, list[int]] = defaultdict(list)
    first_test_line: int | None = None

    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        decl_match = DECL_RE.match(raw_line)
        if decl_match:
            kind = decl_match.group("kind")
            name = decl_match.group("name")
            decl_lines[(kind, name)].append(lineno)
            if first_test_line is not None:
                failures.append(
                    f"late_top_level_decl:{kind}:{name}:line={lineno}:first_test_line={first_test_line}"
                )
            continue

        test_match = TEST_RE.match(raw_line)
        if test_match:
            name = test_match.group("name")
            test_lines[name].append(lineno)
            if first_test_line is None:
                first_test_line = lineno

    for (kind, name), lines in sorted(decl_lines.items()):
        if len(lines) > 1:
            joined = ",".join(str(line) for line in lines)
            failures.append(f"duplicate_top_level_decl:{kind}:{name}:count={len(lines)}:lines={joined}")

    for name, lines in sorted(test_lines.items()):
        if len(lines) > 1:
            joined = ",".join(str(line) for line in lines)
            failures.append(f"duplicate_test_name:{name}:count={len(lines)}:lines={joined}")

    return failures


def write_helper(root: Path, text: str) -> None:
    path = helper_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def clean_helper_text() -> str:
    return """const std = @import("std");

pub const ParseBoolError = error{Invalid};

pub fn strscpy(dest: []u8, src: []const u8) isize {
    _ = dest;
    _ = src;
    return 0;
}

fn cStringLen(buf: []const u8) usize {
    return buf.len;
}

test "strscpy keeps NUL termination and reports truncation with -E2BIG" {
    try std.testing.expect(true);
}

test "strcmp mirrors C-string lexical ordering" {
    try std.testing.expectEqual(@as(usize, 3), cStringLen("abc"));
}
"""


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_string_uniqueness_") as tmpdir:
        root = Path(tmpdir)

        if collect_failures(root) != [f"missing_file:{STRING_HELPER_REL.as_posix()}"]:
            print("self-test:missing-file-check")
            return 1

        write_helper(root, clean_helper_text())
        if collect_failures(root):
            print("self-test:clean-helper-should-pass")
            return 1

        write_helper(
            root,
            clean_helper_text()
            + """
pub fn strscpy(dest: []u8, src: []const u8) isize {
    _ = dest;
    _ = src;
    return -7;
}
""",
        )
        duplicate_failures = collect_failures(root)
        if not any(item.startswith("late_top_level_decl:pub fn:strscpy") for item in duplicate_failures):
            print("self-test:expected-late-decl-failure")
            return 1
        if not any(item.startswith("duplicate_top_level_decl:pub fn:strscpy") for item in duplicate_failures):
            print("self-test:expected-duplicate-decl-failure")
            return 1

        write_helper(
            root,
            clean_helper_text()
            + """
test "strcmp mirrors C-string lexical ordering" {
    try std.testing.expect(true);
}
""",
        )
        test_failures = collect_failures(root)
        if not any(item.startswith("duplicate_test_name:strcmp mirrors C-string lexical ordering") for item in test_failures):
            print("self-test:expected-duplicate-test-failure")
            return 1

    print("phase1-string-definition-uniqueness:self-test:ok")
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

    print("phase1-string-definition-uniqueness:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
