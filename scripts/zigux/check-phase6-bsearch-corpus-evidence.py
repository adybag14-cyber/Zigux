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
PARITY_CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
HELPER_EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
HELPER_PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
LIB_PATH = Path("lib/bsearch.zig")
HELPER_TEST_PATH = Path("zigux/tests/phase6_bsearch.zig")
PERF_TEST_PATH = Path("zigux/tests/phase6_bsearch_perf.zig")
LOWER_BOUND_TEST_PATH = Path("zigux/tests/phase6_bsearch_lower_bound_c_abi.zig")
BUDGET_TEST_PATH = Path("zigux/tests/phase6_bsearch_c_abi_budget.zig")
FIXTURES_PATH = Path("zigux/tests/fixtures/phase6_bsearch_vectors.zig")
C_PARITY_CHECKER_PATH = Path("scripts/zigux/check-phase6-bsearch-c-parity.py")
C_PARITY_RUNNER_PATH = Path("zigux/tests/phase6_bsearch_c_parity.zig")
C_HARNESS_PATH = Path("zigux/tests/fixtures/phase6_bsearch_c_harness.c")
BUILD_PATH = Path("zigux/tests/phase6_build.zig")

BUDGET_FORMULA = '"budget_formula": "std.math.log2_int_ceil(len) + 1"'
BOUND_BUDGET_FORMULA = '"bound_budget_formula": "std.math.log2_int_ceil(len) + 1"'
PARITY_ROW = (
    "- helper-evidence row: `zigux/tests/phase6_bsearch_perf.zig`, "
    "`zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, "
    "`zigux/tests/phase6_bsearch_c_abi_budget.zig`, "
    "`zigux/tests/phase6_bsearch_c_parity.zig`, "
    "`zigux/tests/fixtures/phase6_bsearch_c_harness.c`, "
    "`zigux/tests/fixtures/phase6_bsearch_vectors.zig`, "
    "`scripts/zigux/check-phase6-bsearch-corpus-evidence.py`, "
    "`scripts/zigux/check-phase6-bsearch-c-parity.py`, "
    "`Documentation/zigux/phase6-bsearch-slice.md`, "
    "`Documentation/zigux/phase6-helper-evidence-catalog.md`, "
    "`zigux/tests/phase6_helper_evidence_manifest.json`, and "
    "`zigux/tests/phase6_helper_parity_manifest.json`"
)
PARITY_POSTURE = (
    "- current posture: direct helper readback is restored across the helper, "
    "focused replay, perf replay, C ABI review routes, direct C parity runner, "
    "direct C parity harness, fixture surface, dedicated corpus checker, direct "
    "C parity checker, and slice note"
)

REQUIRED_SNIPPETS = {
    SLICE_PATH: [
        "- `PHASE6_STATUS=parked`",
        "- `IndexRange.firstConst`",
        "- `IndexRange.lastConst`",
        "- `IndexRange.bytes`",
        "- `IndexRange.bytesMutable`",
        "- `zigux/tests/phase6_bsearch_perf.zig`",
        "- `zigux/tests/phase6_bsearch_c_parity.zig`",
        "- `zigux/tests/fixtures/phase6_bsearch_c_harness.c`",
        "- helper-local checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
        "- direct C parity checker: `scripts/zigux/check-phase6-bsearch-c-parity.py`",
        "python3 scripts/zigux/check-phase6-bsearch-c-parity.py",
    ],
    CATALOG_PATH: [
        "- dedicated slowdown replay: `zigux/tests/phase6_bsearch_perf.zig`",
        "- direct C parity companions: `zigux/tests/phase6_bsearch_c_parity.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`, and `scripts/zigux/check-phase6-bsearch-c-parity.py`",
        "- dedicated corpus checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
        "- `bsearch` now keeps a dedicated helper-local perf replay in `zigux/tests/phase6_bsearch_perf.zig`",
        "- `python3 scripts/zigux/check-phase6-bsearch-c-parity.py`",
    ],
    PARITY_CATALOG_PATH: [
        "### bsearch",
        PARITY_ROW,
        PARITY_POSTURE,
    ],
    HELPER_EVIDENCE_MANIFEST_PATH: [
        '"key": "bsearch"',
        '"direct_c_parity_replay": "zigux/tests/phase6_bsearch_c_parity.zig"',
        '"direct_c_parity_harness": "zigux/tests/fixtures/phase6_bsearch_c_harness.c"',
        '"scripts/zigux/check-phase6-bsearch-corpus-evidence.py"',
        '"scripts/zigux/check-phase6-bsearch-c-parity.py"',
        '"query_count": 16',
        BUDGET_FORMULA,
        '"zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig"',
        '"make -C zigux phase6-bsearch-perf"',
    ],
    HELPER_PARITY_MANIFEST_PATH: [
        '"key": "bsearch"',
        '"direct_c_parity_replay": "zigux/tests/phase6_bsearch_c_parity.zig"',
        '"direct_c_parity_harness": "zigux/tests/fixtures/phase6_bsearch_c_harness.c"',
        '"scripts/zigux/check-phase6-bsearch-corpus-evidence.py"',
        '"scripts/zigux/check-phase6-bsearch-c-parity.py"',
        '"budget_model": "comparison_budget"',
        BOUND_BUDGET_FORMULA,
        '"zigux/tests/phase6_bsearch_lower_bound_c_abi.zig"',
        '"zigux/tests/phase6_bsearch_c_abi_budget.zig"',
        '"make -C zigux phase6-bsearch-perf"',
        '"make -C zigux phase6-perf"',
    ],
    LIB_PATH: [
        "pub fn lowerBoundIndex(comptime Key: type, comptime T: type, key: *const Key, items: []const T, compare: anytype) usize {",
        "pub fn equalRangeIndex(comptime Key: type, comptime T: type, key: *const Key, items: []const T, compare: anytype) IndexRange {",
        "pub fn equalRange(comptime Key: type, comptime T: type, key: *const Key, items: []const T, compare: anytype) []const T {",
        "pub fn equalRangeMutable(comptime Key: type, comptime T: type, key: *const Key, items: []T, compare: anytype) []T {",
        'test "index range views keep typed and byte aliases aligned for hits and insertion sites" {',
        "pub fn firstConst(self: @This(), comptime T: type, items: []const T) ?*const T {",
        "pub fn lastConst(self: @This(), comptime T: type, items: []const T) ?*const T {",
        "pub fn bytesMutable(self: @This(), base: [*]u8, size: usize) []u8 {",
    ],
    HELPER_TEST_PATH: [
        'test "phase 6 bsearch direct equalRange wrappers keep duplicate-span and write-through coverage aligned" {',
        'test "phase 6 bsearch direct descending equalRange wrappers keep duplicate-span and write-through coverage aligned" {',
        'test "phase 6 bsearch accepts runtime-selected descending raw c abi comparator pointers" {',
        'test "phase 6 bsearch accepts runtime-selected typed c abi comparator pointers" {',
        'test "phase 6 bsearch keeps symbol fixtures searchable through typed bounds" {',
        'test "phase 6 bsearch keeps packed-record fixtures searchable through raw wrappers" {',
    ],
    PERF_TEST_PATH: [
        "phase6-bsearch-perf",
        "avg_compare_calls",
        "max_compare_calls",
        "max_compare_budget",
        "populateDescending(descending_values, ascending_values);",
        "const descending_witness = try runWitnessCases(",
        "for (descending_queries, descending_expected_hits) |query, expected_hit| {",
        "try std.testing.expect(descending_witness.max_compare_calls <= max_compare_budget);",
    ],
    LOWER_BOUND_TEST_PATH: [
        'test "phase 6 bsearch raw c abi bounds keep duplicate spans and insertion points aligned" {',
        'test "phase 6 bsearch descending raw c abi mutable wrappers keep duplicate-span write-through aligned" {',
        "const mutable_lower = bsearch.bsearchLowerBoundMutable(",
        "try std.testing.expectEqual(@intFromPtr(&insertion_duplicates[6]), @intFromPtr(typed_missing_lower));",
        "try expectRange(descending_duplicates[0..], 20, .{ .lower = 6, .upper = 6 }, compare);",
    ],
    BUDGET_TEST_PATH: [
        'test "phase 6 bsearch raw c abi budgets stay logarithmic for deterministic ascending and descending slices" {',
        'test "phase 6 bsearch typed c abi budgets stay logarithmic for deterministic ascending and descending slices" {',
        'test "phase 6 bsearch raw c abi equal-range budgets stay logarithmic for duplicate spans in both sort orders" {',
        'test "phase 6 bsearch typed c abi equal-range budgets stay logarithmic for duplicate spans in both sort orders" {',
        'test "phase 6 bsearch typed c abi runtime-selected comparator pointers keep the budget contract" {',
        'test "phase 6 bsearch runtime-selected raw c abi comparator pointers keep the budget contract" {',
        'test "phase 6 bsearch runtime-selected raw c abi bound and equal-range comparator pointers keep the budget contract" {',
    ],
    FIXTURES_PATH: [
        '.{ .label = "len15", .len = representative_ascending_values.len, .reps = 4_000 },',
        '.{ .label = "len64", .len = 64, .reps = 2_000 },',
        '.{ .label = "len1024", .len = 1_024, .reps = 250 },',
        "pub const query_count: usize = 16;",
        'test "phase 6 bsearch perf seeds stay deterministic" {',
    ],
    C_PARITY_CHECKER_PATH: [
        'C_HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase6_bsearch_c_harness.c"',
        'ZIG_RUNNER = ROOT / "zigux" / "tests" / "phase6_bsearch_c_parity.zig"',
        'print("PHASE6_BSEARCH_C_PARITY=pass")',
    ],
    C_PARITY_RUNNER_PATH: [
        'try writeIndexCase(writer, "descending-hit", 34, bsearch.searchIndex(u32, u32, &@as(u32, 34), descending_values[0..], compareDescendingU32));',
        'try writeIndexCase(writer, "descending-miss", 20, bsearch.searchIndex(u32, u32, &@as(u32, 20), descending_values[0..], compareDescendingU32));',
    ],
    C_HARNESS_PATH: [
        "static int compare_descending_u32(const void *key, const void *elt)",
        'print_index_case("descending-hit", key, descending_values, inline_bsearch(&key, descending_values, sizeof(descending_values) / sizeof(descending_values[0]), sizeof(descending_values[0]), compare_descending_u32));',
    ],
    BUILD_PATH: [
        'const bsearch_test_step = b.step("phase6-bsearch-test", "Run Phase 6 bsearch helper tests");',
        'const bsearch_perf_step = b.step("phase6-bsearch-perf", "Run Phase 6 bsearch helper perf gate");',
        "bsearch_test_step.dependOn(&run_bsearch_c_abi_budget_tests.step);",
        "bsearch_perf_step.dependOn(&run_bsearch_perf.step);",
    ],
}

SELF_TEST_CASES = [
    (PARITY_CATALOG_PATH, PARITY_ROW, "- helper-evidence row: `zigux/tests/phase6_bsearch_perf.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, and `zigux/tests/phase6_helper_evidence_manifest.json`"),
    (PARITY_CATALOG_PATH, PARITY_POSTURE, "- current posture: direct helper readback is restored across the helper, focused replay, perf replay, C ABI review routes, fixture surface, checker, and slice note"),
    (HELPER_EVIDENCE_MANIFEST_PATH, BUDGET_FORMULA, '"budget_formula": "std.math.log2_int_floor(len) + 1"'),
    (HELPER_PARITY_MANIFEST_PATH, BOUND_BUDGET_FORMULA, '"bound_budget_formula": "std.math.log2_int_floor(len) + 1"'),
    (CATALOG_PATH, "- direct C parity companions: `zigux/tests/phase6_bsearch_c_parity.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`, and `scripts/zigux/check-phase6-bsearch-c-parity.py`", "- direct C parity companions: `zigux/tests/phase6_bsearch_c_parity.zig` and `scripts/zigux/check-phase6-bsearch-c-parity.py`"),
    (SLICE_PATH, "- direct C parity checker: `scripts/zigux/check-phase6-bsearch-c-parity.py`", "- direct C parity checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`"),
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
            raise AssertionError(f"expected failure mentioning {rel_path.as_posix()}, got {exc}") from exc
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
