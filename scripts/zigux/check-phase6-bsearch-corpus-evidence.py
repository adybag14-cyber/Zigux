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
BUILD_PATH = Path("zigux/tests/phase6_build.zig")

REQUIRED_SNIPPETS = {
    SLICE_PATH: [
        "- `PHASE6_STATUS=parked`",
        "- lane state: helper slice restored; parked unless helper-local parity, portability, duplicate-span, raw C ABI bounds, fixture-backed perf replay, or compact fixture-companion drift reappears",
        "- `zigux/tests/phase6_bsearch_perf.zig`",
        "- `zigux/tests/phase6_bsearch_c_abi_budget.zig`",
        "- the compact shared seed fixture companion keeps representative ascending, descending, duplicate, symbol, packed-record, deterministic query corpus, and dedicated perf-case lengths reviewable without widening this lane into speculative threshold recalibration or broader shared survey work",
        "- helper-local checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
    ],
    CATALOG_PATH: [
        "- dedicated slowdown replay: `zigux/tests/phase6_bsearch_perf.zig`",
        "- dedicated corpus checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
        "- `bsearch` now keeps a dedicated helper-local perf replay in `zigux/tests/phase6_bsearch_perf.zig`",
    ],
    PARITY_CATALOG_PATH: [
        "- helper-evidence row: `zigux/tests/phase6_bsearch_perf.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, and `zigux/tests/phase6_helper_parity_manifest.json`",
        "- current posture: direct helper readback is restored across the helper, focused replay, perf replay, C ABI review routes, fixture surface, checker, and slice note",
    ],
    HELPER_EVIDENCE_MANIFEST_PATH: [
        '"key": "bsearch"',
        '"dedicated_slowdown_replay": "zigux/tests/phase6_bsearch_perf.zig"',
        '"checker_surfaces": [',
        '"scripts/zigux/check-phase6-bsearch-corpus-evidence.py"',
        '"case_labels": [',
        '"len15"',
        '"len64"',
        '"len1024"',
        '"query_count": 16',
        '"zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig"',
        '"make -C zigux phase6-bsearch-perf"',
    ],
    HELPER_PARITY_MANIFEST_PATH: [
        '"key": "bsearch"',
        '"dedicated_slowdown_replay": "zigux/tests/phase6_bsearch_perf.zig"',
        '"budget_model": "comparison_budget"',
        '"bound_budget_formula": "std.math.log2_int_ceil(len) + 1"',
        '"runtime_selected_c_abi_replays": [',
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
        "pub fn bsearchLowerBoundIndex(key: *const anyopaque, base: [*]const u8, num: usize, size: usize, compare: anytype) usize {",
        "pub fn bsearchEqualRangeIndex(key: *const anyopaque, base: [*]const u8, num: usize, size: usize, compare: anytype) IndexRange {",
        "pub fn bsearchEqualRange(key: *const anyopaque, base: [*]const u8, num: usize, size: usize, compare: anytype) []const u8 {",
        "pub fn bsearchEqualRangeMutable(key: *const anyopaque, base: [*]u8, num: usize, size: usize, compare: anytype) []u8 {",
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
        "fixtures.perf_cases",
        "fixtures.seedDeterministicQueries",
        "avg_compare_calls",
        "max_compare_calls",
        "max_compare_budget",
        "compareCountedDescending",
        "compareCountedOpaqueDescending",
        "populateDescending(descending_values, ascending_values);",
        "const descending_witness = try runWitnessCases(",
        "for (descending_queries, descending_expected_hits) |query, expected_hit| {",
        "try std.testing.expect(descending_witness.max_compare_calls <= max_compare_budget);",
    ],
    LOWER_BOUND_TEST_PATH: [
        'test "phase 6 bsearch raw c abi bounds keep duplicate spans and insertion points aligned" {',
        'test "phase 6 bsearch descending raw c abi mutable wrappers keep duplicate-span write-through aligned" {',
        "const mutable_lower = bsearch.bsearchLowerBoundMutable(",
        "try std.testing.expectEqual(@intFromPtr(&mutable_duplicates[3]), @intFromPtr(typed_mutable_lower));",
        "const missing_lower = bsearch.bsearchLowerBoundMutable(",
        "try std.testing.expectEqual(@intFromPtr(&insertion_duplicates[6]), @intFromPtr(typed_missing_lower));",
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
        '.{ .label = "len15", .len = representative_ascending_values.len, .reps = 4_000 },',
        '.{ .label = "len64", .len = 64, .reps = 2_000 },',
        '.{ .label = "len1024", .len = 1_024, .reps = 250 },',
        "pub const query_count: usize = 16;",
        'test "phase 6 bsearch perf seeds stay deterministic" {',
    ],
    BUILD_PATH: [
        'const bsearch_test_step = b.step("phase6-bsearch-test", "Run Phase 6 bsearch helper tests");',
        'const bsearch_perf_step = b.step("phase6-bsearch-perf", "Run Phase 6 bsearch helper perf gate");',
        "bsearch_test_step.dependOn(&run_bsearch_c_abi_budget_tests.step);",
        "bsearch_perf_step.dependOn(&run_bsearch_perf.step);",
    ],
}

SELF_TEST_CASES = [
    (SLICE_PATH, "- `zigux/tests/phase6_bsearch_perf.zig`", "- `zigux/tests/phase6_bsearch_perf_matrix.zig`"),
    (
        HELPER_TEST_PATH,
        'test "phase 6 bsearch direct descending equalRange wrappers keep duplicate-span and write-through coverage aligned" {',
        'test "phase 6 bsearch direct descending bounds wrappers keep duplicate-span and write-through coverage aligned" {',
    ),
    (CATALOG_PATH, "- dedicated slowdown replay: `zigux/tests/phase6_bsearch_perf.zig`", "- dedicated slowdown replay: `zigux/tests/phase6_bsearch_perf_matrix.zig`"),
    (
        PARITY_CATALOG_PATH,
        "- current posture: direct helper readback is restored across the helper, focused replay, perf replay, C ABI review routes, fixture surface, checker, and slice note",
        "- current posture: direct helper readback is restored across the helper, focused replay, perf replay, C ABI review routes, fixture surface, and slice note",
    ),
    (
        HELPER_EVIDENCE_MANIFEST_PATH,
        '"query_count": 16',
        '"query_count": 8',
    ),
    (
        HELPER_PARITY_MANIFEST_PATH,
        '"bound_budget_formula": "std.math.log2_int_ceil(len) + 1"',
        '"bound_budget_formula": "std.math.log2_int_floor(len) + 1"',
    ),
    (
        LIB_PATH,
        "pub fn bsearchEqualRange(key: *const anyopaque, base: [*]const u8, num: usize, size: usize, compare: anytype) []const u8 {",
        "pub fn bsearchEqualRangeBytes(key: *const anyopaque, base: [*]const u8, num: usize, size: usize, compare: anytype) []const u8 {",
    ),
    (
        LOWER_BOUND_TEST_PATH,
        "const mutable_lower = bsearch.bsearchLowerBoundMutable(",
        "const mutable_alias = bsearch.bsearchLowerBoundMutable(",
    ),
    (
        LOWER_BOUND_TEST_PATH,
        "try std.testing.expectEqual(@intFromPtr(&insertion_duplicates[6]), @intFromPtr(typed_missing_lower));",
        "try std.testing.expectEqual(@intFromPtr(&insertion_duplicates[5]), @intFromPtr(typed_missing_lower));",
    ),
    (
        BUDGET_TEST_PATH,
        'test "phase 6 bsearch runtime-selected raw c abi bound and equal-range comparator pointers keep the budget contract" {',
        'test "phase 6 bsearch runtime-selected raw c abi comparator pointers keep the budget contract" {',
    ),
    (FIXTURES_PATH, "pub const query_count: usize = 16;", "pub const query_count: usize = 15;"),
    (PERF_TEST_PATH, "avg_compare_calls", "avg_probe_calls"),
    (PERF_TEST_PATH, "compareCountedDescending", "compareCountedReverse"),
    (PERF_TEST_PATH, "compareCountedOpaqueDescending", "compareCountedOpaqueReverse"),
    (PERF_TEST_PATH, "populateDescending(descending_values, ascending_values);", "populateDescendingPerf(descending_values, ascending_values);"),
    (PERF_TEST_PATH, "const descending_witness = try runWitnessCases(", "const alternate_witness = try runWitnessCases("),
    (
        PERF_TEST_PATH,
        "for (descending_queries, descending_expected_hits) |query, expected_hit| {",
        "for (ascending_queries, descending_expected_hits) |query, expected_hit| {",
    ),
    (
        PERF_TEST_PATH,
        "try std.testing.expect(descending_witness.max_compare_calls <= max_compare_budget);",
        "try std.testing.expect(descending_witness.max_compare_calls < max_compare_budget);",
    ),
    (BUILD_PATH, 'const bsearch_perf_step = b.step("phase6-bsearch-perf", "Run Phase 6 bsearch helper perf gate");', 'const bsearch_perf_step = b.step("phase6-bsearch-scan", "Run Phase 6 bsearch helper perf gate");'),
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
