#!/usr/bin/env python3
"""Fail-closed checks for the live Phase 6 shared helper packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


SHARED_REQUIRED_PATHS = [
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("Documentation/zigux/phase6-helper-parity-catalog.md"),
    Path("Documentation/zigux/phase6-perf-gate-survey.md"),
    Path("Documentation/zigux/phase6-leaf-helper-lane-sequencing.md"),
    Path("scripts/zigux/README.md"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/phase6_build.zig"),
]

CHECKSUM_REQUIRED_PATHS = [
    Path("Documentation/zigux/phase6-checksum-slice.md"),
    Path("lib/checksum.zig"),
    Path("zigux/tests/phase6_checksum.zig"),
    Path("zigux/tests/phase6_checksum_perf.zig"),
    Path("zigux/tests/phase6_checksum_c_parity.zig"),
    Path("zigux/tests/fixtures/phase6_checksum_vectors.zig"),
    Path("zigux/tests/fixtures/phase6_checksum_c_harness.c"),
]

BUILD_REQUIRED_SNIPPETS = [
    'const checksum_module = b.createModule(.{',
    'const checksum_test_step = b.step("phase6-checksum-test", "Run Phase 6 checksum helper tests");',
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum perf gate");',
]

CHECKSUM_SLICE_REQUIRED_SNIPPETS = [
    "- `PHASE6_STATUS=reviewable`",
    "- helper: `lib/checksum.zig`",
    "- focused helper replay: `zigux/tests/phase6_checksum.zig`",
    "- dedicated perf replay: `zigux/tests/phase6_checksum_perf.zig`",
    "- shared fixture companion: `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
    "- direct local helper replay route: `zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig`",
    "- direct local perf route: `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`",
    "- direct C parity scaffolding: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`",
]

HELPER_REQUIRED_SNIPPETS = [
    "pub fn partial(bytes: []const u8, seed: u32) u32 {",
    "pub fn compute(bytes: []const u8) u16 {",
    "pub fn tcpUdpNofold(sum: u32, saddr: u32, daddr: u32, len: u32, proto: u8) u32 {",
    "pub fn tcpUdpV6Nofold(sum: u32, saddr: [16]u8, daddr: [16]u8, len: u32, proto: u8) u32 {",
    "pub fn replaceByDiff(sum: u16, diff: u32) u16 {",
]

FIXTURE_REQUIRED_SNIPPETS = [
    "pub const compute_cases = [_]ComputeCase{",
    "pub const seeded_cases = [_]SeededCase{",
    "pub const composition_cases = [_]CompositionCase{",
    "pub const pseudo_header_cases = [_]PseudoHeaderCase{",
    "pub const ipv6_pseudo_header_cases = [_]Ipv6PseudoHeaderCase{",
    "pub const carry_discipline_cases = [_]CarryDisciplineCase{",
    '.{ .label = "64B", .payload = perf_payload_64[0..], .iterations = 200000, .max_slowdown_pct = 150 },',
    '.{ .label = "1501B", .payload = perf_payload_1501[0..], .iterations = 12000, .max_slowdown_pct = 150 },',
]

TEST_REQUIRED_SNIPPETS = [
    'test "phase6 checksum compute cases match the shared fixture corpus" {',
    'test "phase6 checksum pseudo header helpers match the shared fixture corpus" {',
    'test "phase6 checksum replacement helpers match the documented IPv4 and payload updates" {',
]

PERF_REQUIRED_SNIPPETS = [
    'test "phase6 checksum perf cases keep the documented labels and thresholds" {',
    'test "phase6 checksum perf cases keep helper and reference outputs aligned before timing" {',
    'phase6-checksum-perf {s} len={} iterations={} helper_ns_per_call={} reference_ns_per_call={} slowdown_pct={}',
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc


def require_paths(repo_root: Path) -> None:
    for rel_path in SHARED_REQUIRED_PATHS + CHECKSUM_REQUIRED_PATHS:
        if not (repo_root / rel_path).exists():
            raise ValidationError(f"missing required Phase 6 path: {rel_path}")


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"missing expected Phase 6 marker in {path.relative_to(path.anchor)}: {snippet}")


def run_checks(repo_root: Path) -> None:
    require_paths(repo_root)
    require_snippets(repo_root / Path("zigux/tests/phase6_build.zig"), BUILD_REQUIRED_SNIPPETS)
    require_snippets(repo_root / Path("Documentation/zigux/phase6-checksum-slice.md"), CHECKSUM_SLICE_REQUIRED_SNIPPETS)
    require_snippets(repo_root / Path("lib/checksum.zig"), HELPER_REQUIRED_SNIPPETS)
    require_snippets(repo_root / Path("zigux/tests/fixtures/phase6_checksum_vectors.zig"), FIXTURE_REQUIRED_SNIPPETS)
    require_snippets(repo_root / Path("zigux/tests/phase6_checksum.zig"), TEST_REQUIRED_SNIPPETS)
    require_snippets(repo_root / Path("zigux/tests/phase6_checksum_perf.zig"), PERF_REQUIRED_SNIPPETS)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    for rel_path in SHARED_REQUIRED_PATHS:
        write(root / rel_path, "placeholder\n")

    write(root / Path("Documentation/zigux/phase6-checksum-slice.md"), "\n".join(CHECKSUM_SLICE_REQUIRED_SNIPPETS) + "\n")
    write(root / Path("lib/checksum.zig"), "\n".join(HELPER_REQUIRED_SNIPPETS) + "\n")
    write(root / Path("zigux/tests/fixtures/phase6_checksum_vectors.zig"), "\n".join(FIXTURE_REQUIRED_SNIPPETS) + "\n")
    write(root / Path("zigux/tests/phase6_checksum.zig"), "\n".join(TEST_REQUIRED_SNIPPETS) + "\n")
    write(root / Path("zigux/tests/phase6_checksum_perf.zig"), "\n".join(PERF_REQUIRED_SNIPPETS) + "\n")
    write(root / Path("zigux/tests/phase6_checksum_c_parity.zig"), "placeholder\n")
    write(root / Path("zigux/tests/fixtures/phase6_checksum_c_harness.c"), "placeholder\n")
    write(root / Path("zigux/tests/phase6_build.zig"), "\n".join(BUILD_REQUIRED_SNIPPETS) + "\n")


def expect_failure(root: Path, rel_path: Path, old: str, new: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    if old not in original:
        raise AssertionError(f"self-test marker not found in {rel_path}: {old}")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    try:
        run_checks(root)
    except ValidationError:
        pass
    else:
        raise AssertionError(f"expected failure for {rel_path}")
    path.write_text(original, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        run_checks(root)
        expect_failure(
            root,
            Path("Documentation/zigux/phase6-checksum-slice.md"),
            "- `PHASE6_STATUS=reviewable`",
            "- `PHASE6_STATUS=blocked`",
        )
        expect_failure(
            root,
            Path("zigux/tests/phase6_build.zig"),
            'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum perf gate");',
            'const checksum_perf_step = b.step("phase6-checksum-perf", "Document Phase 6 checksum perf gate");',
        )
        expect_failure(
            root,
            Path("zigux/tests/fixtures/phase6_checksum_vectors.zig"),
            '.{ .label = "1501B", .payload = perf_payload_1501[0..], .iterations = 12000, .max_slowdown_pct = 150 },',
            '.{ .label = "1501B", .payload = perf_payload_1501[0..], .iterations = 12000, .max_slowdown_pct = 151 },',
        )
    print("self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Path to the Zigux repository root")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checks")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    run_checks(Path(args.repo_root).resolve())
    print("Phase 6 shared surface matches the live checksum helper packet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
