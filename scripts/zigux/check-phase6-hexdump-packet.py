#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 hexdump helper packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    """Raised when an expected Phase 6 hexdump marker is missing."""


CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
LIB_PATH = Path("lib/hexdump.zig")
SLICE_PATH = Path("Documentation/zigux/phase6-hexdump-slice.md")
HELPER_TEST_PATH = Path("zigux/tests/phase6_hexdump.zig")
PERF_PATH = Path("zigux/tests/phase6_hexdump_perf.zig")
PERF_MATRIX_PATH = Path("zigux/tests/phase6_hexdump_perf_matrix.zig")
FIXTURES_PATH = Path("zigux/tests/fixtures/phase6_hexdump_vectors.zig")
BUILD_PATH = Path("zigux/tests/phase6_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
ROUTE_PATH = Path("scripts/zigux/check-phase6-hexdump-route.py")

REQUIRED_SNIPPETS = {
    CATALOG_PATH: [
        "- helper: `lib/hexdump.zig`",
        "- direct local packet checker: `python3 scripts/zigux/check-phase6-hexdump-packet.py`",
        "- Linux-style packet review route: `make -C zigux phase6-hexdump-review`",
        "- exact perf-matrix preflight: `zigux/tests/phase6_hexdump_perf_matrix.zig`",
        "- direct local rerun route: `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig`",
    ],
    LIB_PATH: [
        'pub const hex_asc = "0123456789abcdef";',
        "pub fn hexAscHi(byte: u8) u8 {",
        "pub fn hexAscUpperHi(byte: u8) u8 {",
        "pub fn hexBytePack(buf: []u8, byte: u8) HexError![]u8 {",
        "pub fn hexBytePackUpper(buf: []u8, byte: u8) HexError![]u8 {",
        "pub fn hex2bin(dst: []u8, src: []const u8) HexError!void {",
        "pub fn bin2hex(dst: []u8, src: []const u8) HexError![]u8 {",
        "pub fn hexDumpLineLength(",
        "pub fn hexDumpToBuffer(",
        'test "hex2bin and bin2hex snake-case aliases stay aligned" {',
        'test "hexBytePack helpers chain bytes and preserve destination on bounds errors" {',
        'test "hexDumpLineLength mirrors formatter normalization" {',
    ],
    SLICE_PATH: [
        "`PHASE6_STATUS=parked_reviewable`",
        "`PHASE6_SLICE=hexdump-leaf-helper`",
        "`scripts/zigux/check-phase6-hexdump-packet.py`",
        "`make -C zigux phase6-hexdump-review`",
        "the landed `hexAsc*`, `hexBytePack`, `hexBytePackUpper`, and `hexDumpLineLength` helper parity surface",
        "focused helper formatting parity plus a four-case fixture-backed slowdown matrix keep the shipped hexdump packet reviewable",
    ],
    HELPER_TEST_PATH: [
        'test "phase 6 hexdump helper packet replays the serialized parity matrix" {',
        'test "phase 6 hexdump helper packet preserves the overflow contract" {',
        'test "phase 6 hexdump helper packet preserves the curated length matrix" {',
        'test "phase 6 hexdump direct helper entrypoints stay aligned with the packet" {',
        'test "phase 6 hexdump direct pack helpers keep uppercase and lowercase nibble parity" {',
    ],
    PERF_PATH: [
        "fn validatePerfMatrix() !void {",
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_CASE_COUNT={d}\\n", .{fixtures.perf_cases.len});',
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF={s}\\n", .{if (failed) "fail" else "pass"});',
        "return error.HexdumpPerfRegression;",
    ],
    PERF_MATRIX_PATH: [
        "pub fn validatePerfMatrix() !void {",
        '.label = "16B-plain-g1",',
        '.label = "32B-ascii-g2",',
        '.label = "16B-ascii-g4",',
        '.label = "16B-ascii-g8",',
        ".max_slowdown_pct = 175,",
        ".max_slowdown_pct = 550,",
        ".max_slowdown_pct = 600,",
        'test "phase 6 hexdump perf matrix preflight stays aligned with the documented packet" {',
    ],
    FIXTURES_PATH: [
        "pub const test_hexdump_buf_size = 32 * 3 + 2 + 32 + 1;",
        "pub const parity_cases = [_]ParityCase{",
        "pub const overflow_cases = [_]OverflowCase{",
        "pub const length_cases = [_]LengthCase{",
        "pub const perf_cases = [_]PerfCase{",
        '.name = "empty ascii line reports zero length",',
        '.name = "plain rowsize-16 group-8 line length",',
        '.name = "ascii rowsize-16 group-8 line length",',
        '.label = "16B-ascii-g8",',
    ],
    BUILD_PATH: [
        'const hexdump_test_step = b.step("phase6-hexdump-test", "Run Phase 6 hexdump helper tests");',
        "hexdump_test_step.dependOn(&run_hexdump_tests.step);",
        "hexdump_test_step.dependOn(&run_hexdump_perf_matrix_tests.step);",
        'const hexdump_review_step = b.step("phase6-hexdump-review", "Run Phase 6 hexdump perf-matrix review preflight");',
        'const hexdump_perf_matrix_test_step = b.step(',
        '"phase6-hexdump-perf-matrix-test",',
        'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump helper perf gate");',
    ],
    MAKEFILE_PATH: [
        "phase6-hexdump-review:",
        "$(PYTHON) scripts/zigux/check-phase6-hexdump-route.py",
        "phase6-hexdump-perf-matrix-test:",
        "$(ZIG) build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
        "phase6-hexdump-test:",
        "$(ZIG) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig --summary all",
        "phase6-hexdump-perf:",
        "$(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig --summary all",
    ],
    ROUTE_PATH: [
        '"""Guard the current Phase 6 hexdump review route."""',
        'MAKEFILE = Path("zigux/Makefile")',
        'BUILD_FILE = Path("zigux/tests/phase6_build.zig")',
        'PERF_MATRIX_FILE = Path("zigux/tests/phase6_hexdump_perf_matrix.zig")',
        '"$(PYTHON) scripts/zigux/check-phase6-hexdump-route.py",',
        '"PHASE6_HEXDUMP_ROUTE=pass"',
    ],
}

SELF_TEST_CASES = [
    (
        CATALOG_PATH,
        "- direct local packet checker: `python3 scripts/zigux/check-phase6-hexdump-packet.py`",
        "- direct local packet checker: `python3 scripts/zigux/check-phase6-hexdump-proof.py`",
    ),
    (
        LIB_PATH,
        "pub fn hexBytePackUpper(buf: []u8, byte: u8) HexError![]u8 {",
        "pub fn hexBytePackUpper(dst: []u8, byte: u8) HexError![]u8 {",
    ),
    (
        LIB_PATH,
        'test "hexDumpLineLength mirrors formatter normalization" {',
        'test "hexDumpLength mirrors formatter normalization" {',
    ),
    (
        SLICE_PATH,
        "the landed `hexAsc*`, `hexBytePack`, `hexBytePackUpper`, and `hexDumpLineLength` helper parity surface",
        "the landed nibble-helper parity surface",
    ),
    (
        HELPER_TEST_PATH,
        'test "phase 6 hexdump direct pack helpers keep uppercase and lowercase nibble parity" {',
        'test "phase 6 hexdump direct pack helpers keep nibble parity" {',
    ),
    (
        PERF_PATH,
        "return error.HexdumpPerfRegression;",
        "return error.HexdumpPerfDrift;",
    ),
    (
        PERF_MATRIX_PATH,
        '.label = "16B-ascii-g8",',
        '.label = "16B-ascii-g16",',
    ),
    (
        FIXTURES_PATH,
        '.name = "ascii rowsize-16 group-8 line length",',
        '.name = "ascii rowsize-16 group-16 line length",',
    ),
    (
        BUILD_PATH,
        'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump helper perf gate");',
        'const hexdump_perf_step = b.step("phase6-hexdump-profile", "Run Phase 6 hexdump helper perf gate");',
    ),
    (
        MAKEFILE_PATH,
        "$(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig --summary all",
        "$(ZIG) build phase6-hexdump-profile --build-file zigux/tests/phase6_build.zig --summary all",
    ),
    (
        ROUTE_PATH,
        '"PHASE6_HEXDUMP_ROUTE=pass"',
        '"PHASE6_HEXDUMP_REVIEW_ROUTE=pass"',
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
                    f"missing expected Phase 6 hexdump packet marker in {rel_path.as_posix()}: {snippet}"
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
    print("PHASE6_HEXDUMP_PACKET_SELF_TEST=pass")
    print(f"PHASE6_HEXDUMP_PACKET_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")


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
    print("PHASE6_HEXDUMP_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())