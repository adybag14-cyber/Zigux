#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 bsearch corpus-evidence packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    """Raised when an expected Phase 6 bsearch marker is missing."""


SLICE_PATH = Path("Documentation/zigux/phase6-bsearch-slice.md")
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
LIB_PATH = Path("lib/bsearch.zig")
HELPER_TEST_PATH = Path("zigux/tests/phase6_bsearch.zig")
LOWER_BOUND_TEST_PATH = Path("zigux/tests/phase6_bsearch_lower_bound_c_abi.zig")
BUDGET_TEST_PATH = Path("zigux/tests/phase6_bsearch_c_abi_budget.zig")
FIXTURES_PATH = Path("zigux/tests/fixtures/phase6_bsearch_vectors.zig")
BUILD_PATH = Path("zigux/tests/phase6_build.zig")

REQUIRED_SNIPPETS = {
    SLICE_PATH: [
        "- `PHASE6_STATUS=parked`",
        "- lane state: helper slice restored; parked unless helper-local parity, portability, duplicate-span, raw C ABI bounds, or compact fixture-companion drift reappears",
        "- `zigux/tests/phase6_bsearch_c_abi_budget.zig`",
        "- the compact shared seed fixture companion keeps representative ascending, descending, duplicate, symbol, packed-record, and deterministic query corpus reviewable without widening this lane into a standalone timing route",
        "- helper-local checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
    ],
    CATALOG_PATH: [
        "- dedicated corpus checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
        "- current review posture: direct helper-local evidence is readable again through `lib/bsearch.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `Documentation/zigux/phase6-bsearch-slice.md`, `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`, this shared catalog, `zigux/tests/phase6_helper_evidence_manifest.json`, the returned `zigux/tests/phase6_helper_parity_manifest.json`, the restored shared build foothold, the current Makefile wrapper surface, and the directly readable scripts-root plus tests-root reminders",
        "- `bsearch` still measures bounded search cost through `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`, and the deterministic `perf_cases` plus seeded query corpus in `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, which hold raw C ABI search and equal-range comparisons to logarithmic budgets across representative lengths instead of using a dedicated wall-clock slowdown harness.",
    ],
    LIB_PATH: [
        "pub fn lowerBoundIndex(comptime Key: type, comptime T: type, key: *const Key, items: []const T, compare: anytype) usize {",
        "pub fn equalRangeMutable(comptime Key: type, comptime T: type, key: *const Key, items: []T, compare: anytype) []T {",
        "pub fn bsearchLowerBoundIndex(key: *const anyopaque, base: [*]const u8, num: usize, size: usize, compare: anytype) usize {",
        "pub fn bsearchEqualRangeMutable(key: *const anyopaque, base: [*]u8, num: usize, size: usize, compare: anytype) []u8 {",
    ],
    HELPER_TEST_PATH: [
        'test "phase 6 bsearch direct equalRange wrappers keep duplicate-span and write-through coverage aligned" {',
        'test "phase 6 bsearch accepts runtime-selected descending raw c abi comparator pointers" {',
        'test "phase 6 bsearch accepts runtime-selected typed c abi comparator pointers" {',
        'test "phase 6 bsearch keeps symbol fixtures searchable through typed bounds" {',
        'test "phase 6 bsearch keeps packed-record fixtures searchable through raw wrappers" {',
    ],
    LOWER_BOUND_TEST_PATH: [
        'test "phase 6 bsearch raw c abi bounds keep duplicate spans and insertion points aligned" {',
        'test "phase 6 bsearch descending raw c abi mutable wrappers keep duplicate-span write-through aligned" {',
        "try expectRange(descending_duplicates[0..], 20, .{ .lower = 6, .upper = 6 }, compare);",
    ],
    BUDGET_TEST_PATH: [
        'test "phase 6 bsearch raw c abi budgets stay logarithmic for deterministic ascending and descending slices" {',
        'test "phase 6 bsearch typed c abi budgets stay logarithmic for deterministic ascending and descending slices" {',
        'test "phase 6 bsearch raw c abi equal-range budgets stay logarithmic for duplicate spans in both sort orders" {',
        'test "phase 6 bsearch typed c abi equal-range budgets stay logarithmic for duplicate spans in both sort orders" {',
        'test "phase 6 bsearch typed c abi runtime-selected comparator pointers keep the budget contract" {',
        'test "phase 6 bsearch typed c abi runtime-selected bound and equal-range comparator pointers keep the budget contract" {',
        'test "phase 6 bsearch runtime-selected raw c abi comparator pointers keep the budget contract" {',
        'test "phase 6 bsearch runtime-selected raw c abi bound and equal-range comparator pointers keep the budget contract" {',
    ],
    FIXTURES_PATH: [
        "pub const representative_duplicate_values = [_]u32{ 3, 6, 9, 12, 21, 21, 21, 24, 27, 30, 33, 36, 39, 42, 45 };",
        "pub const representative_descending_duplicate_values = [_]u32{ 45, 42, 39, 21, 21, 21, 12, 9, 6, 3 };",
        "pub const dynamic_case_lengths = [_]usize{",
        '.{ .label = "len15", .len = representative_ascending_values.len, .reps = 4_000 },',
        '.{ .label = "len64", .len = 64, .reps = 2_000 },',
        '.{ .label = "len1024", .len = 1_024, .reps = 250 },',
        "pub const query_count: usize = 16;",
        'test "phase 6 bsearch perf seeds stay deterministic" {',
    ],
    BUILD_PATH: [
        'const bsearch_test_step = b.step("phase6-bsearch-test", "Run Phase 6 bsearch helper tests");',
        "bsearch_test_step.dependOn(&run_bsearch_tests.step);",
        "bsearch_test_step.dependOn(&run_bsearch_lower_bound_c_abi_tests.step);",
        "bsearch_test_step.dependOn(&run_bsearch_c_abi_budget_tests.step);",
    ],
}

SELF_TEST_CASES = [
    (
        SLICE_PATH,
        "- helper-local checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
        "- helper-local checker: `scripts/zigux/check-phase6-bsearch-helper-check.py`",
    ),
    (
        CATALOG_PATH,
        "- dedicated corpus checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
        "- dedicated corpus checker: `scripts/zigux/check-phase6-bsearch-corpus-proof.py`",
    ),
    (
        LIB_PATH,
        "pub fn bsearchEqualRangeMutable(key: *const anyopaque, base: [*]u8, num: usize, size: usize, compare: anytype) []u8 {",
        "pub fn bsearchEqualRangeMutable(key: *const anyopaque, base: [*]u8, num: usize, size: usize, compare: anytype) []const u8 {",
    ),
    (
        HELPER_TEST_PATH,
        'test "phase 6 bsearch keeps packed-record fixtures searchable through raw wrappers" {',
        'test "phase 6 bsearch keeps packed-record fixtures searchable through typed wrappers" {',
    ),
    (
        LOWER_BOUND_TEST_PATH,
        "try expectRange(descending_duplicates[0..], 20, .{ .lower = 6, .upper = 6 }, compare);",
        "try expectRange(descending_duplicates[0..], 20, .{ .lower = 5, .upper = 5 }, compare);",
    ),
    (
        BUDGET_TEST_PATH,
        'test "phase 6 bsearch typed c abi runtime-selected comparator pointers keep the budget contract" {',
        'test "phase 6 bsearch typed c abi runtime-selected pointer budgets keep the contract" {',
    ),
    (
        BUDGET_TEST_PATH,
        'test "phase 6 bsearch typed c abi runtime-selected bound and equal-range comparator pointers keep the budget contract" {',
        'test "phase 6 bsearch typed c abi runtime-selected bound comparator pointers keep the budget contract" {',
    ),
    (
        BUDGET_TEST_PATH,
        'test "phase 6 bsearch runtime-selected raw c abi comparator pointers keep the budget contract" {',
        'test "phase 6 bsearch runtime-selected raw comparator pointers keep the budget contract" {',
    ),
    (
        BUDGET_TEST_PATH,
        'test "phase 6 bsearch runtime-selected raw c abi bound and equal-range comparator pointers keep the budget contract" {',
        'test "phase 6 bsearch runtime-selected raw bound comparator pointers keep the budget contract" {',
    ),
    (
        FIXTURES_PATH,
        '.{ .label = "len1024", .len = 1_024, .reps = 250 },',
        '.{ .label = "len1024", .len = 1_024, .reps = 300 },',
    ),
    (
        BUILD_PATH,
        "bsearch_test_step.dependOn(&run_bsearch_c_abi_budget_tests.step);",
        "bsearch_test_step.dependOn(&run_bsearch_tests.step);",
    ),
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def validate(repo_root: Path) -> None:
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        content = read_text(repo_root / rel_path)
        for snippet in snippets:
            if snippet not in content:
                raise ValidationError(
                    f"missing expected Phase 6 bsearch corpus marker in {rel_path.as_posix()}: {snippet}"
                )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        write(root / rel_path, "\n".join(snippets) + "\n")


def expect_failure(root: Path, rel_path: Path, old: str, new: str) -> None:
    path = root / rel_path
    original = read_text(path)
    if old not in original:
        raise AssertionError(f"self-test marker not found in {rel_path.as_posix()}: {old}")
    write(path, original.replace(old, new, 1))
    try:
        validate(root)
    except ValidationError as exc:
        if rel_path.as_posix() not in str(exc):
            raise AssertionError(
                f"expected failure mentioning {rel_path.as_posix()}, got {exc}"
            ) from exc
    else:
        raise AssertionError(f"expected validation failure for {rel_path.as_posix()}")
    finally:
        write(path, original)


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)
        for rel_path, old, new in SELF_TEST_CASES:
            expect_failure(root, rel_path, old, new)
    print("PHASE6_BSEARCH_CORPUS_EVIDENCE_SELF_TEST=pass")
    print(f"PHASE6_BSEARCH_CORPUS_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root to validate (default: current directory)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in self-test instead of validating a repository",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    validate(args.repo_root)
    print("PHASE6_BSEARCH_CORPUS_EVIDENCE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
