#!/usr/bin/env python3
"""Guard the current Phase 1 bitmap helper packet against direct-anchor drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent

BITMAP_HELPER_REL = Path("tools/lib/bitmap.zig")

EXPECTED_BITMAP_SOURCE_SYMBOLS = [
    "pub fn orBits(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {",
    "pub fn xorBits(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {",
    "pub fn scnprintf(bitmap: []const Word, nbits: usize, buffer: []u8) usize {",
]

EXPECTED_BITMAP_DIRECT_TEST_ANCHORS = [
    'test "bitmap xor keeps caller-selected bit window"',
    'test "bitmap xor across a multiword tail still lets callers clamp the last word"',
    'test "bitmap or keeps caller-selected bit window"',
    'test "bitmap or across a multiword tail still lets callers clamp the last word"',
    'test "bitmap scnprintf collapses contiguous ranges"',
    'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
    'test "bitmap scnprintf truncates and keeps a terminator slot"',
    'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
    'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
]

EXPECTED_SUMMARY = (
    "Phase 1 bitmap stays on the direct-anchor family for the current helper-local "
    "bit-window orBits and xorBits coverage plus the contiguous-range scnprintf packet, "
    "so future rereads should refresh this one helper-local checker before widening into "
    "closure-note or reminder-surface sync work."
)


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

    bitmap_path = root / BITMAP_HELPER_REL
    if not bitmap_path.exists():
        return [f"missing_file:{BITMAP_HELPER_REL.as_posix()}"]

    bitmap_text = load_text(root, BITMAP_HELPER_REL)

    for marker in EXPECTED_BITMAP_SOURCE_SYMBOLS:
        failures.extend(
            require_exact_occurrence(
                bitmap_text,
                f"{BITMAP_HELPER_REL.as_posix()}:source_symbol",
                marker,
            )
        )

    for marker in EXPECTED_BITMAP_DIRECT_TEST_ANCHORS:
        failures.extend(
            require_exact_occurrence(
                bitmap_text,
                f"{BITMAP_HELPER_REL.as_posix()}:helper_test_anchor",
                marker,
            )
        )

    if EXPECTED_SUMMARY.count("Phase 1 bitmap stays on the direct-anchor family") != 1:
        failures.append("checker:summary_marker:expected=1")

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_file(
        root,
        BITMAP_HELPER_REL,
        "\n".join(EXPECTED_BITMAP_SOURCE_SYMBOLS + EXPECTED_BITMAP_DIRECT_TEST_ANCHORS) + "\n",
    )


def run_self_test() -> int:
    cases = [
        ("baseline", None, True),
        ("missing_source_symbol", EXPECTED_BITMAP_SOURCE_SYMBOLS[0], False),
        ("missing_or_anchor", EXPECTED_BITMAP_DIRECT_TEST_ANCHORS[2], False),
        ("missing_crossword_scnprintf_anchor", EXPECTED_BITMAP_DIRECT_TEST_ANCHORS[5], False),
        ("duplicate_anchor", ("duplicate", EXPECTED_BITMAP_DIRECT_TEST_ANCHORS[3]), False),
    ]

    for name, mutation, expect_ok in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-bitmap-packet-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if isinstance(mutation, str):
                path = root / BITMAP_HELPER_REL
                text = path.read_text(encoding="utf-8")
                path.write_text(text.replace(mutation + "\n", "", 1), encoding="utf-8")
            elif isinstance(mutation, tuple):
                _, marker = mutation
                path = root / BITMAP_HELPER_REL
                text = path.read_text(encoding="utf-8")
                path.write_text(
                    text.replace(marker + "\n", marker + "\n" + marker + "\n", 1),
                    encoding="utf-8",
                )

            failures = collect_failures(root)
            ok = not failures
            if ok != expect_ok:
                print(f"phase1-bitmap-helper-packet-self-test:{name}:unexpected={failures}")
                return 1

    print("PHASE1_BITMAP_HELPER_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_HELPER_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
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
        for failure in failures:
            print(failure)
        return 1

    print("phase1-bitmap-helper-packet:ok")
    print(f"PHASE1_BITMAP_HELPER_PACKET_SUMMARY={EXPECTED_SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
