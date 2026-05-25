#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 checksum helper packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    """Raised when an expected Phase 6 checksum marker is missing."""


SLICE_PATH = Path("Documentation/zigux/phase6-checksum-slice.md")
LIB_PATH = Path("lib/checksum.zig")
HELPER_TEST_PATH = Path("zigux/tests/phase6_checksum.zig")
PERF_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
FIXTURES_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")
C_PARITY_PATH = Path("zigux/tests/phase6_checksum_c_parity.zig")
C_HARNESS_PATH = Path("zigux/tests/fixtures/phase6_checksum_c_harness.c")
C_PARITY_CHECKER_PATH = Path("scripts/zigux/check-phase6-checksum-c-parity.py")
CORPUS_CHECKER_PATH = Path("scripts/zigux/check-phase6-checksum-corpus-evidence.py")
BUILD_PATH = Path("zigux/tests/phase6_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_SNIPPETS = {
    SLICE_PATH: [
        "`PHASE6_STATUS=parked`",
        "`PHASE6_SLICE=checksum-leaf-helper`",
        "`lib/checksum.zig`",
        "`zigux/tests/phase6_checksum.zig`",
        "`zigux/tests/phase6_checksum_perf.zig`",
        "`zigux/tests/phase6_checksum_c_parity.zig`",
        "`zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "`zigux/tests/fixtures/phase6_checksum_c_harness.c`",
        "`scripts/zigux/check-phase6-checksum-c-parity.py`",
        "the current perf packet now keeps both the payload slowdown matrix and the `checksum.ipFastCsum` IPv4 fast-path matrix explicit",
    ],
    LIB_PATH: [
        "pub fn add(sum: u32, addend: u32) u32 {",
        "pub fn blockAdd(sum: u32, other: u32, offset: usize) u32 {",
        "pub fn replace4(sum: u16, from: u32, to: u32) u16 {",
        "pub fn tcpUdpV6Magic(sum: u32, saddr: *const [16]u8, daddr: *const [16]u8, len: u32, proto: u8) u16 {",
        "pub fn ipFastCsum(header: []const u8) u16 {",
        "test \"partial and compute match reference accumulation across seeded odd payloads\" {",
        "test \"pseudo-header helpers match direct checksum recomputation over pseudo-header bytes and payload\" {",
        "test \"ipFastCsum stays aligned with compute across aligned IPv4 headers\" {",
    ],
    HELPER_TEST_PATH: [
        "test \"phase 6 checksum helper packet replays the arithmetic and pseudo-header matrix\" {",
        "test \"phase 6 checksum helper packet keeps fragmented accumulation and replacement parity aligned\" {",
        "test \"phase 6 checksum helper packet keeps aligned IPv4 fast paths and carry helpers reviewable\" {",
    ],
    PERF_PATH: [
        "fn validatePerfMatrix() !void {",
        "fn validateFastPathMatrix() !void {",
        "std.debug.print(\"PHASE6_CHECKSUM_PERF_CASE_COUNT={d}\\n\", .{fixtures.perf_cases.len});",
        "std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT={d}\\n\", .{fixtures.fast_path_cases.len});",
        "std.debug.print(\"PHASE6_CHECKSUM_PERF={s}\\n\", .{if (failed) \"fail\" else \"pass\"});",
        "if (slowdown_pct > case.max_slowdown_pct) {",
        "return error.ChecksumPerfRegression;",
    ],
    FIXTURES_PATH: [
        "pub const perf_cases = [_]PerfCase{",
        ".{ .label = \"64B\", .bytes = &perf_payload_64b, .iterations = 200_000, .max_slowdown_pct = 150 },",
        ".{ .label = \"1501B\", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 },",
        "pub const fast_path_cases = [_]FastPathCase{",
        ".{ .label = \"IPV4_20B\", .header = &ip_fast_csum_ipv4_20b, .iterations = 600_000, .max_slowdown_pct = 100 },",
        ".{ .label = \"IPV4_20B_UPDATED\", .header = &ip_fast_csum_ipv4_20b_updated, .iterations = 600_000, .max_slowdown_pct = 100 },",
        ".{ .label = \"IPV4_24B\", .header = &ip_fast_csum_ipv4_24b, .iterations = 500_000, .max_slowdown_pct = 100 },",
        ".{ .label = \"IPV4_60B\", .header = &ip_fast_csum_ipv4_60b, .iterations = 250_000, .max_slowdown_pct = 100 },",
        "test \"phase 6 checksum perf fixture packet stays bounded to the documented matrices\" {",
    ],
    C_PARITY_PATH: [
        "const checksum = @import(\"checksum\");",
        "pub fn main() !void {",
        "try runCase(",
        "std.debug.print(\"PHASE6_CHECKSUM_C_PARITY=pass\\n\", .{});",
    ],
    C_HARNESS_PATH: [
        "uint16_t zigux_phase6_checksum_compute",
        "uint16_t zigux_phase6_checksum_ip_fast_csum",
        "uint16_t zigux_phase6_checksum_tcpudp_magic",
        "uint16_t zigux_phase6_checksum_tcpudp_v6_magic",
    ],
    C_PARITY_CHECKER_PATH: [
        "\"\"\"Fail-closed review hook for the current Phase 6 checksum C parity packet.\"\"\"",
        "print(\"PHASE6_CHECKSUM_C_PARITY_SELF_TEST=pass\")",
        "print(\"PHASE6_CHECKSUM_C_PARITY=pass\")",
    ],
    CORPUS_CHECKER_PATH: [
        "\"\"\"Guard the current Phase 6 checksum evidence packet.\"\"\"",
        "print(\"PHASE6_CHECKSUM_CORPUS_EVIDENCE_SELF_TEST=pass\")",
        "print(\"PHASE6_CHECKSUM_CORPUS_EVIDENCE=pass\")",
    ],
    BUILD_PATH: [
        "const checksum_test_step = b.step(\"phase6-checksum-test\", \"Run Phase 6 checksum helper tests\");",
        "const checksum_perf_matrix_test_step = b.step(",
        "\"phase6-checksum-perf-matrix-test\",",
        "const checksum_perf_step = b.step(\"phase6-checksum-perf\", \"Run Phase 6 checksum helper perf gate\");",
    ],
    MAKEFILE_PATH: [
        "phase6-checksum-test:",
        "phase6-checksum-perf-matrix-test:",
        "phase6-checksum-perf:",
        "$(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig --summary all",
    ],
}

SELF_TEST_CASES = [
    (SLICE_PATH, "`PHASE6_SLICE=checksum-leaf-helper`", "`PHASE6_SLICE=checksum`"),
    (SLICE_PATH, "`zigux/tests/phase6_checksum_perf.zig`", "`zigux/tests/phase6_checksum.zig`"),
    (LIB_PATH, "pub fn ipFastCsum(header: []const u8) u16 {", "pub fn ipFastCsumAligned(header: []const u8) u16 {"),
    (LIB_PATH, "test \"pseudo-header helpers match direct checksum recomputation over pseudo-header bytes and payload\" {", "test \"pseudo-header helpers match checksum recomputation\" {"),
    (HELPER_TEST_PATH, "test \"phase 6 checksum helper packet keeps aligned IPv4 fast paths and carry helpers reviewable\" {", "test \"phase 6 checksum helper packet keeps IPv4 fast paths reviewable\" {"),
    (PERF_PATH, "fn validateFastPathMatrix() !void {", "fn validateFastPathCases() !void {"),
    (PERF_PATH, "std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT={d}\\n\", .{fixtures.fast_path_cases.len});", "std.debug.print(\"PHASE6_CHECKSUM_FAST_PATH_CASE_COUNT={d}\\n\", .{fixtures.fast_path_cases.len});"),
    (FIXTURES_PATH, ".{ .label = \"1501B\", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 },", ".{ .label = \"1500B\", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 },"),
    (FIXTURES_PATH, ".{ .label = \"IPV4_60B\", .header = &ip_fast_csum_ipv4_60b, .iterations = 250_000, .max_slowdown_pct = 100 },", ".{ .label = \"IPV4_64B\", .header = &ip_fast_csum_ipv4_60b, .iterations = 250_000, .max_slowdown_pct = 100 },"),
    (C_PARITY_PATH, "std.debug.print(\"PHASE6_CHECKSUM_C_PARITY=pass\\n\", .{});", "std.debug.print(\"PHASE6_CHECKSUM_PARITY=pass\\n\", .{});"),
    (C_HARNESS_PATH, "uint16_t zigux_phase6_checksum_ip_fast_csum", "uint16_t zigux_phase6_checksum_fast_csum"),
    (C_PARITY_CHECKER_PATH, "print(\"PHASE6_CHECKSUM_C_PARITY=pass\")", "print(\"PHASE6_CHECKSUM_PARITY=pass\")"),
    (CORPUS_CHECKER_PATH, "print(\"PHASE6_CHECKSUM_CORPUS_EVIDENCE=pass\")", "print(\"PHASE6_CHECKSUM_CORPUS=pass\")"),
    (BUILD_PATH, "const checksum_perf_step = b.step(\"phase6-checksum-perf\", \"Run Phase 6 checksum helper perf gate\");", "const checksum_profile_step = b.step(\"phase6-checksum-perf\", \"Run Phase 6 checksum helper perf gate\");"),
    (MAKEFILE_PATH, "phase6-checksum-perf-matrix-test:", "phase6-checksum-perf-test:"),
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
                    f"missing expected Phase 6 checksum packet marker in {rel_path.as_posix()}: {snippet}"
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
    print("PHASE6_CHECKSUM_PACKET_SELF_TEST=pass")
    print(f"PHASE6_CHECKSUM_PACKET_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")


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
    print("PHASE6_CHECKSUM_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
