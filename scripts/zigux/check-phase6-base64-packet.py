#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 6 base64 packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

REQUIRED_FILES = {
    "helper": "lib/base64.zig",
    "slice": "Documentation/zigux/phase6-base64-slice.md",
    "build": "zigux/tests/phase6_build.zig",
    "parity_runner": "zigux/tests/phase6_base64_c_parity.zig",
    "casegen": "zigux/tests/phase6_base64_c_casegen.zig",
    "parity_vectors": "zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig",
    "c_harness": "zigux/tests/fixtures/phase6_base64_c_harness.c",
    "parity_script": "scripts/zigux/check-phase6-base64-c-parity.py",
}

REQUIRED_ABSENT_FILES = [
    "zigux/tests/phase6_base64.zig",
    "zigux/tests/phase6_base64_perf.zig",
    "zigux/tests/fixtures/phase6_base64_vectors.zig",
]

HELPER_MARKERS = [
    "pub const Variant = enum {",
    "pub fn chars(nbytes: usize, padding: bool) usize {",
    "pub fn bytes(src: []const u8, padding: bool, variant: Variant) DecodeError!usize {",
    "pub fn encode(dst: []u8, src: []const u8, padding: bool, variant: Variant) EncodeError!usize {",
    "pub fn decode(dst: []u8, src: []const u8, padding: bool, variant: Variant) DecodeError!usize {",
    'test "base64 decode exhaustively accepts only canonical padded short tails across variants" {',
    'test "base64 decode exhaustively accepts only canonical unpadded short tails across variants" {',
]

SLICE_MARKERS = [
    "`PHASE6_STATUS=blocked`",
    "`PHASE6_SLICE=base64-leaf-helper`",
    "current `master` still keeps `lib/base64.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
    "current `master` lacks `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig`",
    "direct local C parity checker route: `python3 scripts/zigux/check-phase6-base64-c-parity.py`",
    "direct local packet checker route: `python3 scripts/zigux/check-phase6-base64-packet.py`",
    "built-in parity-script self-test route: `python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test`",
    "the shipped direct C parity surface is now self-contained again because `zigux/tests/phase6_base64_c_parity.zig` and `zigux/tests/phase6_base64_c_casegen.zig` both read the compact committed `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig` corpus instead of the absent focused replay fixture module",
]

BUILD_MARKERS = [
    '.root_source_file = b.path("phase6_base64.zig"),',
    '.name = "phase6-base64-tests"',
    '.root_source_file = b.path("phase6_base64_perf.zig"),',
    '.name = "phase6-base64-perf"',
    'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 perf gate");',
]

PARITY_RUNNER_MARKERS = [
    'const base64 = @import("base64");',
    'const fixtures = @import("fixtures/phase6_base64_c_parity_vectors.zig");',
    'for (fixtures.standard_cases) |case| {',
    'for (fixtures.variant_cases) |case| {',
    'for (fixtures.standard_decode_cases) |case| {',
    'for (fixtures.variant_decode_cases) |case| {',
    'for (fixtures.invalid_decode_cases) |case| {',
]

CASEGEN_MARKERS = [
    'const fixtures = @import("fixtures/phase6_base64_c_parity_vectors.zig");',
    'try writer.writeAll("/* Generated from zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig. */\\n\\n");',
    'if (std.mem.eql(u8, name, "std")) return "BASE64_STD";',
    'if (std.mem.eql(u8, name, "urlsafe")) return "BASE64_URLSAFE";',
    'if (std.mem.eql(u8, name, "imap")) return "BASE64_IMAP";',
]

PARITY_VECTOR_MARKERS = [
    'pub const standard_cases = [_]EncodeCase{',
    'pub const variant_cases = [_]VariantCase{',
    'pub const standard_decode_cases = [_]DecodeCase{',
    'pub const variant_decode_cases = [_]DecodeCase{',
    'pub const invalid_decode_cases = [_]InvalidDecodeCase{',
    'test "phase6 base64 direct parity corpus stays compact and portable" {',
    'try std.testing.expectEqual(@as(usize, 4), standard_cases.len);',
    'try std.testing.expectEqual(@as(usize, 4), variant_cases.len);',
    'try std.testing.expectEqual(@as(usize, 4), standard_decode_cases.len);',
    'try std.testing.expectEqual(@as(usize, 4), variant_decode_cases.len);',
    'try std.testing.expectEqual(@as(usize, 8), invalid_decode_cases.len);',
]

PARITY_SCRIPT_MARKERS = [
    'C_HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase6_base64_c_harness.c"',
    'HELPER_SOURCE = ROOT / "lib" / "base64.zig"',
    'CASE_GENERATOR = ROOT / "zigux" / "tests" / "phase6_base64_c_casegen.zig"',
    'FIXTURE_SOURCE = ROOT / "zigux" / "tests" / "fixtures" / "phase6_base64_c_parity_vectors.zig"',
    'GENERATED_INCLUDE = ROOT / "zigux" / "tests" / "fixtures" / "phase6_base64_c_generated_cases.inc"',
    'ZIG_RUNNER = ROOT / "zigux" / "tests" / "phase6_base64_c_parity.zig"',
    'print("PHASE6_BASE64_C_PARITY_SELF_TEST=pass")',
    'print("PHASE6_BASE64_C_PARITY=pass")',
]

C_HARNESS_MARKERS = [
    '#include "phase6_base64_c_generated_cases.inc"',
    'static int base64_encode(const unsigned char *src, int srclen, char *dst, bool padding, enum base64_variant variant)',
    'static int base64_decode(const char *src, int srclen, unsigned char *dst, bool padding, enum base64_variant variant)',
    'printf("enc\\t%s\\t%d\\t", variant_name(c->variant), c->padding ? 1 : 0);',
    'printf("dec\\t%s\\t%d\\t%d\\t", variant_name(c->variant), c->padding ? 1 : 0, bytes_result);',
    'printf("inv\\t%s\\t%d\\t",',
]

SELF_TEST_CASE_COUNT = 9


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(relative_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {relative_path}: {marker}")


def expect_absent(root: Path, relative_path: str) -> None:
    if (root / relative_path).exists():
        raise CheckError(f"expected Phase 6 base64 gap file to stay absent: {relative_path}")


def run_check(root: Path) -> None:
    expect_markers(REQUIRED_FILES["helper"], read_text(root, REQUIRED_FILES["helper"]), HELPER_MARKERS)
    expect_markers(REQUIRED_FILES["slice"], read_text(root, REQUIRED_FILES["slice"]), SLICE_MARKERS)
    expect_markers(REQUIRED_FILES["build"], read_text(root, REQUIRED_FILES["build"]), BUILD_MARKERS)
    expect_markers(REQUIRED_FILES["parity_runner"], read_text(root, REQUIRED_FILES["parity_runner"]), PARITY_RUNNER_MARKERS)
    expect_markers(REQUIRED_FILES["casegen"], read_text(root, REQUIRED_FILES["casegen"]), CASEGEN_MARKERS)
    expect_markers(REQUIRED_FILES["parity_vectors"], read_text(root, REQUIRED_FILES["parity_vectors"]), PARITY_VECTOR_MARKERS)
    expect_markers(REQUIRED_FILES["parity_script"], read_text(root, REQUIRED_FILES["parity_script"]), PARITY_SCRIPT_MARKERS)
    expect_markers(REQUIRED_FILES["c_harness"], read_text(root, REQUIRED_FILES["c_harness"]), C_HARNESS_MARKERS)
    for relative_path in REQUIRED_ABSENT_FILES:
        expect_absent(root, relative_path)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / REQUIRED_FILES["helper"], "\n".join(HELPER_MARKERS) + "\n")
    write(root / REQUIRED_FILES["slice"], "\n".join(SLICE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["build"], "\n".join(BUILD_MARKERS) + "\n")
    write(root / REQUIRED_FILES["parity_runner"], "\n".join(PARITY_RUNNER_MARKERS) + "\n")
    write(root / REQUIRED_FILES["casegen"], "\n".join(CASEGEN_MARKERS) + "\n")
    write(root / REQUIRED_FILES["parity_vectors"], "\n".join(PARITY_VECTOR_MARKERS) + "\n")
    write(root / REQUIRED_FILES["parity_script"], "\n".join(PARITY_SCRIPT_MARKERS) + "\n")
    write(root / REQUIRED_FILES["c_harness"], "\n".join(C_HARNESS_MARKERS) + "\n")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(
                f"expected self-test failure containing {expected_fragment!r}, got {exc!r}"
            ) from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase6_base64_packet_"))
    try:
        build_self_test_fixture(tmpdir)
        run_check(tmpdir)

        helper = tmpdir / REQUIRED_FILES["helper"]
        helper.write_text(helper.read_text(encoding="utf-8").replace(HELPER_MARKERS[-1], "", 1), encoding="utf-8")
        expect_failure(tmpdir, HELPER_MARKERS[-1])

        build_self_test_fixture(tmpdir)
        slice_note = tmpdir / REQUIRED_FILES["slice"]
        slice_note.write_text(slice_note.read_text(encoding="utf-8").replace(SLICE_MARKERS[5], "", 1), encoding="utf-8")
        expect_failure(tmpdir, "check-phase6-base64-packet.py")

        build_self_test_fixture(tmpdir)
        build_file = tmpdir / REQUIRED_FILES["build"]
        build_file.write_text(build_file.read_text(encoding="utf-8").replace(BUILD_MARKERS[2], "", 1), encoding="utf-8")
        expect_failure(tmpdir, BUILD_MARKERS[2])

        build_self_test_fixture(tmpdir)
        parity_vectors = tmpdir / REQUIRED_FILES["parity_vectors"]
        parity_vectors.write_text(parity_vectors.read_text(encoding="utf-8").replace(PARITY_VECTOR_MARKERS[-1], "", 1), encoding="utf-8")
        expect_failure(tmpdir, PARITY_VECTOR_MARKERS[-1])

        build_self_test_fixture(tmpdir)
        parity_script = tmpdir / REQUIRED_FILES["parity_script"]
        parity_script.write_text(parity_script.read_text(encoding="utf-8").replace(PARITY_SCRIPT_MARKERS[3], 'FIXTURE_SOURCE = ROOT / "zigux" / "tests" / "fixtures" / "phase6_base64_vectors.zig"', 1), encoding="utf-8")
        expect_failure(tmpdir, "phase6_base64_c_parity_vectors.zig")

        build_self_test_fixture(tmpdir)
        c_harness = tmpdir / REQUIRED_FILES["c_harness"]
        c_harness.write_text(c_harness.read_text(encoding="utf-8").replace(C_HARNESS_MARKERS[0], "", 1), encoding="utf-8")
        expect_failure(tmpdir, "phase6_base64_c_generated_cases.inc")

        build_self_test_fixture(tmpdir)
        (tmpdir / REQUIRED_FILES["parity_runner"]).unlink()
        expect_failure(tmpdir, REQUIRED_FILES["parity_runner"])

        build_self_test_fixture(tmpdir)
        write(tmpdir / REQUIRED_ABSENT_FILES[0], 'test "unexpected replay" {}\n')
        expect_failure(tmpdir, REQUIRED_ABSENT_FILES[0])

        build_self_test_fixture(tmpdir)
        (tmpdir / REQUIRED_FILES["slice"]).unlink()
        expect_failure(tmpdir, REQUIRED_FILES["slice"])

        print("PHASE6_BASE64_PACKET_SELF_TEST=pass")
        print(f"PHASE6_BASE64_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(Path(args.root))
    except CheckError as exc:
        print(f"PHASE6_BASE64_PACKET=fail: {exc}")
        return 1

    print("PHASE6_BASE64_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
