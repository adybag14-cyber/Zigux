#!/usr/bin/env python3
"""Guard the Phase 1 string copy-and-pad helper-local anchors against drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

STRING_HELPER_REL = Path("tools/lib/string.zig")

REQUIRED_SOURCE_SYMBOLS = [
    "pub fn memcpyAndPad(dest: []u8, src: []const u8, count: usize, pad: u8) void {",
    "pub fn memcpy_and_pad(dest: []u8, src: []const u8, count: usize, pad: u8) void {",
    "pub fn strtomem(dest: []u8, src: []const u8) void {",
    "pub fn strtomem_pad(dest: []u8, src: []const u8, pad: u8) void {",
    "pub fn memtostr(dest: []u8, src: []const u8) void {",
    "pub fn memtostrPad(dest: []u8, src: []const u8) void {",
    "pub fn memtostr_pad(dest: []u8, src: []const u8) void {",
]

REQUIRED_TEST_ANCHORS = [
    'test "memcpyAndPad copies the requested prefix and pads the destination tail"',
    'test "strtomem copies a C-string prefix without adding a terminator or padding"',
    'test "strtomem_pad copies through the first NUL and pads the remaining tail"',
    'test "memtostr copies a bounded non-NUL source and adds one terminator"',
    'test "memtostr stops at embedded NUL without padding the tail"',
    'test "memtostrPad zero-pads the remaining tail after copying"',
    'test "memtostr helpers keep one-byte destinations terminated"',
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    helper_path = root / STRING_HELPER_REL
    if not helper_path.exists():
        return [f"missing_file:{STRING_HELPER_REL.as_posix()}"]

    helper_text = load_text(root, STRING_HELPER_REL)
    failures: list[str] = []

    for symbol in REQUIRED_SOURCE_SYMBOLS:
        failures.extend(
            require_exact_occurrence(helper_text, f"string_copy_fill_source:{symbol}", symbol)
        )

    for anchor in REQUIRED_TEST_ANCHORS:
        failures.extend(
            require_exact_occurrence(helper_text, f"string_copy_fill_anchor:{anchor}", anchor)
        )

    return failures


def write_file(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    lines = REQUIRED_SOURCE_SYMBOLS + REQUIRED_TEST_ANCHORS
    write_file(root, STRING_HELPER_REL, "\n".join(lines) + "\n")


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker + "\n" in text:
        text = text.replace(marker + "\n", "", 1)
    else:
        text = text.replace(marker, "", 1)
    path.write_text(text, encoding="utf-8")


def duplicate_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace(marker, marker + "\n" + marker, 1)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, str, str] | None]] = [("success", None)]

    for symbol in REQUIRED_SOURCE_SYMBOLS:
        cases.append(("remove_source_symbol", (STRING_HELPER_REL.as_posix(), symbol, "remove")))
        cases.append(("duplicate_source_symbol", (STRING_HELPER_REL.as_posix(), symbol, "duplicate")))

    for anchor in REQUIRED_TEST_ANCHORS:
        cases.append(("remove_test_anchor", (STRING_HELPER_REL.as_posix(), anchor, "remove")))
        cases.append(("duplicate_test_anchor", (STRING_HELPER_REL.as_posix(), anchor, "duplicate")))

    cases.append(("missing_helper_file", (STRING_HELPER_REL.as_posix(), "", "missing_file")))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-string-copy-fill-helper-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if mutation is not None:
                relative_path, marker, kind = mutation
                target = root / relative_path
                if kind == "remove":
                    remove_marker(target, marker)
                elif kind == "duplicate":
                    duplicate_marker(target, marker)
                elif kind == "missing_file":
                    target.unlink()

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("PHASE1_STRING_COPY_FILL_HELPER_ANCHORS_SELF_TEST=fail")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_STRING_COPY_FILL_HELPER_ANCHORS_SELF_TEST=pass")
    print(f"PHASE1_STRING_COPY_FILL_HELPER_ANCHORS_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_STRING_COPY_FILL_HELPER_ANCHORS=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_STRING_COPY_FILL_HELPER_ANCHORS=pass")
    print(
        "PHASE1_STRING_COPY_FILL_HELPER_ANCHORS_REQUIRED_SYMBOL_COUNT="
        f"{len(REQUIRED_SOURCE_SYMBOLS)}"
    )
    print(
        "PHASE1_STRING_COPY_FILL_HELPER_ANCHORS_REQUIRED_TEST_COUNT="
        f"{len(REQUIRED_TEST_ANCHORS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
