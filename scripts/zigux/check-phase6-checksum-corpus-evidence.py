#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 checksum corpus-evidence packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    """Raised when an expected Phase 6 checksum marker is missing."""


SLICE_PATH = Path("Documentation/zigux/phase6-checksum-slice.md")
HELPER_TEST_PATH = Path("zigux/tests/phase6_checksum.zig")
PERF_TEST_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
FIXTURES_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")

REQUIRED_SNIPPETS = {
    SLICE_PATH: [
        "- `PHASE6_STATUS=parked`",
        "- `PHASE6_SLICE=checksum-leaf-helper`",
        "- `zigux/tests/phase6_checksum.zig` keeps the compute, partial, fold, replacement, folded and unfolded pseudo-header helpers, and aligned fast-path packet reviewable",
        "- `zigux/tests/phase6_checksum_perf.zig` keeps the helper-vs-reference slowdown gate explicit through the committed `64B` and `1501B` payload matrix in `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "- the same perf replay also keeps `ipFastCsum()` honest through committed `IPV4_20B`, `IPV4_24B`, and `IPV4_60B` aligned-header cases that compare the fast path directly against `compute()`",
        "- perf-matrix stability for the committed `64B` and `1501B` fixture payloads with explicit slowdown thresholds",
        "- aligned-header fast-path perf stability for the committed `IPV4_20B`, `IPV4_24B`, and `IPV4_60B` fixture headers with explicit slowdown thresholds against `compute()`",
    ],
    HELPER_TEST_PATH: [
        'test "phase 6 checksum compute parity matches local reference vectors" {',
        'test "phase 6 checksum split composition stays aligned with seeded partial accumulation" {',
        'test "phase 6 checksum fragment recomposition stays aligned across split boundaries" {',
        'test "phase 6 checksum carry helpers preserve one\'s-complement replacement behavior" {',
        'test "phase 6 checksum pseudo-header helpers match direct reference accumulation" {',
        'test "phase 6 checksum pseudo-header helpers keep high-length IPv6 carries visible" {',
        'test "phase 6 checksum negate stays involutive across representative carry edges" {',
        'test "phase 6 checksum incremental helpers preserve odd-offset carry discipline" {',
        "for (fixtures.carry16_cases) |case| {",
    ],
    PERF_TEST_PATH: [
        'test "phase 6 checksum perf matrix preflight stays aligned with the documented packet" {',
        "try validatePerfMatrix();",
        "try validateFastPathMatrix();",
        'std.debug.print("PHASE6_CHECKSUM_PERF_CASE_COUNT={d}\\n", .{fixtures.perf_cases.len});',
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT={d}\\n", .{fixtures.fast_path_cases.len});',
        'std.debug.print("PHASE6_CHECKSUM_PERF={s}\\n", .{if (failed) "fail" else "pass"});',
    ],
    FIXTURES_PATH: [
        '.{ .label = "64B", .bytes = &perf_payload_64b, .iterations = 200_000, .max_slowdown_pct = 150 },',
        '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 },',
        '.{ .label = "IPV4_20B", .header = &ip_fast_csum_ipv4_20b, .iterations = 600_000, .max_slowdown_pct = 100 },',
        '.{ .label = "IPV4_24B", .header = &ip_fast_csum_ipv4_24b, .iterations = 500_000, .max_slowdown_pct = 100 },',
        '.{ .label = "IPV4_60B", .header = &ip_fast_csum_ipv4_60b, .iterations = 250_000, .max_slowdown_pct = 100 },',
        '.{ .label = "near-wrap-plus-three", .sum = 0xfffe, .addend = 0x0003, .expected_add = 0x0002, .expected_sub = 0xfffb },',
        'test "phase 6 checksum perf fixture packet stays bounded to the documented matrices" {',
    ],
}

SELF_TEST_CASES = [
    (
        SLICE_PATH,
        "- `PHASE6_SLICE=checksum-leaf-helper`",
        "- `PHASE6_SLICE=checksum-runtime-helper`",
    ),
    (
        SLICE_PATH,
        "- perf-matrix stability for the committed `64B` and `1501B` fixture payloads with explicit slowdown thresholds",
        "- perf-matrix stability for the committed `64B` fixture payload only",
    ),
    (
        HELPER_TEST_PATH,
        'test "phase 6 checksum pseudo-header helpers keep high-length IPv6 carries visible" {',
        'test "phase 6 checksum pseudo-header helpers keep IPv6 carries visible" {',
    ),
    (
        HELPER_TEST_PATH,
        "for (fixtures.carry16_cases) |case| {",
        "for (fixtures.carry_cases) |case| {",
    ),
    (
        PERF_TEST_PATH,
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT={d}\\n", .{fixtures.fast_path_cases.len});',
        'std.debug.print("PHASE6_CHECKSUM_FAST_PATH_CASE_COUNT={d}\\n", .{fixtures.fast_path_cases.len});',
    ),
    (
        PERF_TEST_PATH,
        'std.debug.print("PHASE6_CHECKSUM_PERF={s}\\n", .{if (failed) "fail" else "pass"});',
        'std.debug.print("PHASE6_CHECKSUM_PERF_STATUS={s}\\n", .{if (failed) "fail" else "pass"});',
    ),
    (
        FIXTURES_PATH,
        '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 },',
        '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 10_000, .max_slowdown_pct = 150 },',
    ),
    (
        FIXTURES_PATH,
        '.{ .label = "IPV4_60B", .header = &ip_fast_csum_ipv4_60b, .iterations = 250_000, .max_slowdown_pct = 100 },',
        '.{ .label = "IPV4_60B", .header = &ip_fast_csum_ipv4_60b, .iterations = 250_000, .max_slowdown_pct = 125 },',
    ),
    (
        FIXTURES_PATH,
        '.{ .label = "near-wrap-plus-three", .sum = 0xfffe, .addend = 0x0003, .expected_add = 0x0002, .expected_sub = 0xfffb },',
        '.{ .label = "near-wrap-plus-three", .sum = 0xfffe, .addend = 0x0003, .expected_add = 0x0001, .expected_sub = 0xfffb },',
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
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_checksum_corpus_") as tmpdir:
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
