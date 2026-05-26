#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 checksum corpus-evidence packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    """Raised when an expected Phase 6 checksum marker is missing."""


SLICE_PATH = Path("Documentation/zigux/phase6-checksum-slice.md")
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
HELPER_EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
HELPER_PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
LIB_PATH = Path("lib/checksum.zig")
HELPER_TEST_PATH = Path("zigux/tests/phase6_checksum.zig")
PERF_TEST_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
FIXTURES_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")
BUILD_PATH = Path("zigux/tests/phase6_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_SNIPPETS = {
    SLICE_PATH: [
        "- `PHASE6_STATUS=parked`",
        "- `PHASE6_SLICE=checksum-leaf-helper`",
        "- `zigux/tests/phase6_checksum.zig` keeps the compute, partial, carry, replacement, folded and unfolded pseudo-header helpers, and aligned fast-path packet reviewable",
        "- `zigux/tests/phase6_checksum_perf.zig` keeps the helper-vs-reference slowdown gate explicit through the committed `64B` and `1501B` payload matrix in `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "- the same perf replay also keeps `ipFastCsum()` honest through committed `IPV4_20B`, `IPV4_20B_UPDATED`, `IPV4_24B`, and `IPV4_60B` aligned-header cases that compare the fast path directly against `compute()`",
    ],
    CATALOG_PATH: [
        "- roadmap anchor: `lib/checksum.c`",
        "- Zig helper: `lib/checksum.zig`",
        "- focused helper replay: `zigux/tests/phase6_checksum.zig`",
        "- dedicated slowdown replay: `zigux/tests/phase6_checksum_perf.zig`",
        "- committed fixture surface: `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "- direct C parity companions: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`",
        "- `zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig`",
        "- `make -C zigux phase6-checksum-perf`",
    ],
    HELPER_EVIDENCE_MANIFEST_PATH: [
        '"key": "checksum"',
        '"roadmap_anchor": "lib/checksum.c"',
        '"zig_helper": "lib/checksum.zig"',
        '"focused_helper_replay": "zigux/tests/phase6_checksum.zig"',
        '"dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig"',
        '"scripts/zigux/check-phase6-checksum-corpus-evidence.py"',
        '"scripts/zigux/check-phase6-checksum-c-parity.py"',
        '"still_missing_direct_companions": [],',
        '"payload_case_labels": [',
        '"64B"',
        '"1501B"',
        '"ipv4_fast_path_case_labels": [',
        '"IPV4_20B"',
        '"IPV4_20B_UPDATED"',
        '"IPV4_24B"',
        '"IPV4_60B"',
        '"zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig"',
        '"make -C zigux phase6-checksum-perf"',
        '"make -C zigux phase6-perf"',
    ],
    HELPER_PARITY_MANIFEST_PATH: [
        '"key": "checksum"',
        '"still_missing_direct_companions": [],',
        '"ipv4_fast_path_case_labels": [',
        '"IPV4_20B"',
        '"IPV4_20B_UPDATED"',
        '"IPV4_24B"',
        '"IPV4_60B"',
        '"make -C zigux phase6-checksum-perf"',
        '"make -C zigux phase6-perf"',
    ],
    LIB_PATH: [
        "pub fn replaceByDiff(sum: u16, diff: u32) u16 {",
        "pub fn replace4(sum: u16, from: u32, to: u32) u16 {",
        "pub fn tcpUdpV6Magic(sum: u32, saddr: *const [16]u8, daddr: *const [16]u8, len: u32, proto: u8) u16 {",
        "pub fn ipFastCsum(header: []const u8) u16 {",
        'test "incremental helper exports keep large odd offsets and 16-bit carries aligned" {',
        'test "partial and compute match reference accumulation across seeded odd payloads" {',
    ],
    HELPER_TEST_PATH: [
        'test "phase 6 checksum fragment recomposition stays aligned across split boundaries" {',
        'test "phase 6 checksum carry helpers preserve one\'s-complement replacement behavior" {',
        'test "phase 6 checksum pseudo-header helpers match direct reference accumulation" {',
        'test "phase 6 checksum pseudo-header helpers keep high-length IPv6 carries visible" {',
        'test "phase 6 checksum negate stays involutive across representative carry edges" {',
    ],
    PERF_TEST_PATH: [
        "fn validatePerfMatrix() !void {",
        "fn validateFastPathMatrix() !void {",
        'std.debug.print("PHASE6_CHECKSUM_PERF_CASE_COUNT={d}\\n", .{fixtures.perf_cases.len});',
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT={d}\\n", .{fixtures.fast_path_cases.len});',
        "const fast_path_expected = checksum.ipFastCsum(case.header);",
        "const compute_expected = checksum.compute(case.header);",
        "const slowdown_pct = slowdownPct(fast_path_median_ns, compute_median_ns);",
        "return error.ChecksumPerfRegression;",
    ],
    FIXTURES_PATH: [
        'pub const perf_payload_64b = makePerfPayload(64, 0x36);',
        'pub const perf_payload_1501b = makePerfPayload(1501, 0x6c);',
        '.{ .label = "64B", .bytes = &perf_payload_64b, .iterations = 200_000, .max_slowdown_pct = 150 },',
        '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 },',
        'pub const ip_fast_csum_ipv4_20b_updated = [_]u8{',
        '.{ .label = "IPV4_20B_UPDATED", .header = &ip_fast_csum_ipv4_20b_updated, .iterations = 600_000, .max_slowdown_pct = 100 },',
        '.{ .label = "IPV4_24B", .header = &ip_fast_csum_ipv4_24b, .iterations = 500_000, .max_slowdown_pct = 100 },',
        '.{ .label = "IPV4_60B", .header = &ip_fast_csum_ipv4_60b, .iterations = 250_000, .max_slowdown_pct = 100 },',
        'test "phase 6 checksum perf fixture packet stays bounded to the documented matrices" {',
    ],
    BUILD_PATH: [
        'const checksum_test_step = b.step("phase6-checksum-test", "Run Phase 6 checksum helper tests");',
        "checksum_test_step.dependOn(&run_checksum_perf_matrix_tests.step);",
        '"phase6-checksum-perf-matrix-test",',
        'const checksum_perf = b.addExecutable(.{',
        '.name = "phase6-checksum-perf",',
    ],
    MAKEFILE_PATH: [
        "phase6-checksum-test:",
        "$(ZIG) build phase6-checksum-test --build-file zigux/tests/phase6_build.zig --summary all",
        "phase6-checksum-perf-matrix-test:",
        "$(ZIG) build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
        "phase6-checksum-perf:",
        "$(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig --summary all",
        "phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf",
    ],
}

SELF_TEST_CASES = [
    (
        SLICE_PATH,
        "- the same perf replay also keeps `ipFastCsum()` honest through committed `IPV4_20B`, `IPV4_20B_UPDATED`, `IPV4_24B`, and `IPV4_60B` aligned-header cases that compare the fast path directly against `compute()`",
        "- the same perf replay also keeps `ipFastCsum()` honest through committed `IPV4_20B`, `IPV4_24B`, and `IPV4_60B` aligned-header cases that compare the fast path directly against `compute()`",
    ),
    (
        CATALOG_PATH,
        "- direct C parity companions: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`",
        "- direct C parity companions: `zigux/tests/phase6_checksum_c_parity.zig` and `scripts/zigux/check-phase6-checksum-c-parity.py`",
    ),
    (
        HELPER_EVIDENCE_MANIFEST_PATH,
        '"IPV4_20B_UPDATED"',
        '"IPV4_20B_REFRESHED"',
    ),
    (
        HELPER_PARITY_MANIFEST_PATH,
        '"IPV4_20B_UPDATED"',
        '"IPV4_20B_REFRESHED"',
    ),
    (
        LIB_PATH,
        "pub fn ipFastCsum(header: []const u8) u16 {",
        "pub fn ipChecksumFast(header: []const u8) u16 {",
    ),
    (
        HELPER_TEST_PATH,
        'test "phase 6 checksum pseudo-header helpers keep high-length IPv6 carries visible" {',
        'test "phase 6 checksum IPv6 pseudo-header helpers keep high-length carries visible" {',
    ),
    (
        PERF_TEST_PATH,
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT={d}\\n", .{fixtures.fast_path_cases.len});',
        'std.debug.print("PHASE6_CHECKSUM_FAST_PATH_CASE_COUNT={d}\\n", .{fixtures.fast_path_cases.len});',
    ),
    (
        FIXTURES_PATH,
        '.{ .label = "IPV4_20B_UPDATED", .header = &ip_fast_csum_ipv4_20b_updated, .iterations = 600_000, .max_slowdown_pct = 100 },',
        '.{ .label = "IPV4_20B_REFRESHED", .header = &ip_fast_csum_ipv4_20b_updated, .iterations = 600_000, .max_slowdown_pct = 100 },',
    ),
    (
        BUILD_PATH,
        '"phase6-checksum-perf-matrix-test",',
        '"phase6-checksum-matrix-test",',
    ),
    (
        MAKEFILE_PATH,
        "$(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig --summary all",
        "$(ZIG) build phase6-checksum-profile --build-file zigux/tests/phase6_build.zig --summary all",
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
                    f"missing expected Phase 6 checksum corpus marker in {rel_path.as_posix()}: {snippet}"
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
    print("PHASE6_CHECKSUM_CORPUS_EVIDENCE_SELF_TEST=pass")
    print(f"PHASE6_CHECKSUM_CORPUS_EVIDENCE_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")


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
    print("PHASE6_CHECKSUM_CORPUS_EVIDENCE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
