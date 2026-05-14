#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 6 hexdump review packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

REQUIRED_FILES = {
    "helper_source": "lib/hexdump.zig",
    "slice_note": "Documentation/zigux/phase6-hexdump-slice.md",
    "lane_sequencing": "Documentation/zigux/phase6-leaf-helper-lane-sequencing.md",
    "perf_refresh_note": "Documentation/zigux/phase6-hexdump-perf-refresh.md",
    "catalog": "Documentation/zigux/phase6-helper-parity-catalog.md",
    "perf_survey": "Documentation/zigux/phase6-perf-gate-survey.md",
    "manifest": "zigux/tests/phase6_helper_parity_manifest.json",
    "build_file": "zigux/tests/phase6_build.zig",
    "makefile": "zigux/Makefile",
    "focused_test": "zigux/tests/phase6_hexdump.zig",
    "perf_test": "zigux/tests/phase6_hexdump_perf.zig",
    "perf_matrix_test": "zigux/tests/phase6_hexdump_perf_matrix.zig",
    "fixtures": "zigux/tests/fixtures/phase6_hexdump_vectors.zig",
}

HELPER_SOURCE_MARKERS = [
    'pub const hex_asc = "0123456789abcdef";',
    "pub fn hex_to_bin(ch: u8) isize {",
    "pub const Hex2BinError = error{",
    "pub fn hex2Bin(dst: []u8, src: []const u8) Hex2BinError!void {",
    "pub fn bin2Hex(dst: []u8, src: []const u8) []u8 {",
    "pub fn requiredLineLength(len: usize, rowsize: usize, groupsize: usize, ascii: bool) usize {",
    "pub fn hexDumpToBuffer(buf: []const u8, rowsize: usize, groupsize: usize, linebuf: []u8, ascii: bool) usize {",
    'test "hex_to_bin accepts numeric, lower, and upper digits" {',
    'test "hex2bin decodes mixed-case input" {',
    'test "bin2hex emits lowercase output and returns the written slice" {',
    'test "hex dump truncation still reports the full logical length" {',
]

SLICE_NOTE_MARKERS = [
    "`PHASE6_SLICE=hexdump-leaf-helper`",
    "`zigux/tests/phase6_hexdump_perf_matrix.zig`",
    "`Documentation/zigux/phase6-hexdump-perf-refresh.md`",
    "`scripts/zigux/check-phase6-hexdump-packet.py`",
    "`make -C zigux phase6-hexdump-test`",
    "`make -C zigux phase6-hexdump-perf`",
    "`make -C zigux phase6-hexdump-review`",
    "lib/hexdump.zig` now also carries direct same-file coverage for the landed `hexToBin`/`hex_to_bin`, `hex2Bin`/`hex2bin`, and `bin2Hex`/`bin2hex` helper parity surface",
    "the directly coupled serialized `length_cases` packet in `zigux/tests/fixtures/phase6_hexdump_vectors.zig` still keeps the empty plain zero-length row aligned with the focused replay and the helper's landed empty-input contract, but the empty ASCII zero-length row has not been serialized into that helper-local fixture packet yet",
    "The current bounded next safe step is one helper-local empty-ASCII length-packet follow-through: add the missing zero-length ASCII row to `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, rerun `python3 scripts/zigux/check-phase6-hexdump-packet.py` and `make -C zigux phase6-hexdump-test`, and keep the repair to that directly coupled fixture-plus-replay packet only.",
    "focused helper formatting parity plus a four-case fixture-backed slowdown matrix keep the shipped hexdump packet reviewable",
]

LANE_SEQUENCING_MARKERS = [
    "### `P6-L19`, `P6-Y07`, `P6-Y08`, and `P6-Y09` hexdump packet",
    "Treat `P6-L19` as the hexdump parked-survey or slice-note truthfulness lane",
    "Treat `P6-Y07` as the hexdump fixture-governance lane",
    "Treat `P6-Y08` as the hexdump serialized empty-ASCII length-packet closure lane",
    "- `lib/hexdump.zig`",
    "- `zigux/tests/phase6_hexdump.zig`",
    "- `zigux/tests/phase6_hexdump_perf.zig`",
    "- `zigux/tests/phase6_hexdump_perf_matrix.zig`",
    "- `zigux/tests/fixtures/phase6_hexdump_vectors.zig`",
    "- `Documentation/zigux/phase6-hexdump-perf-refresh.md`",
]

PERF_REFRESH_NOTE_MARKERS = [
    "# Phase 6 Hexdump Perf Refresh Evidence",
    "- owner lane: `P6-Y09`",
    "- `16B-plain`: `max_slowdown_pct = 175` remained sufficient, with the successful replay recording `slowdown_pct = 139`",
    "- `32B-ascii-g2`: the grouped ASCII formatter replay needed a wider ceiling, with the successful replay recording `slowdown_pct = 518`",
    "This note now serves as the bounded rationale for why the grouped ASCII formatter case keeps a higher ceiling than the plain formatter case",
]

CATALOG_MARKERS = [
    "### hexdump",
    "- helper: `lib/hexdump.zig`",
    "- perf refresh note: `Documentation/zigux/phase6-hexdump-perf-refresh.md`",
    "- focused helper replay: `zigux/tests/phase6_hexdump.zig`",
    "- dedicated perf replay: `zigux/tests/phase6_hexdump_perf.zig`",
    "- exact perf-matrix preflight: `zigux/tests/phase6_hexdump_perf_matrix.zig`",
    "- fixtures: `zigux/tests/fixtures/phase6_hexdump_vectors.zig`",
    "- direct local packet checker: `python3 scripts/zigux/check-phase6-hexdump-packet.py`",
    "- Linux-style packet review route: `make -C zigux phase6-hexdump-review`",
]

PERF_SURVEY_MARKERS = [
    "* hexdump shared posture: a dedicated slowdown gate remains wired through `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`",
    "* hexdump exact thresholds: `zigux/tests/fixtures/phase6_hexdump_vectors.zig` still pins `16B-plain-g1` at `reps = 40_000` with `max_slowdown_pct = 175`, `32B-ascii-g2` at `reps = 10_000` with `max_slowdown_pct = 550`, `16B-ascii-g4` at `reps = 20_000` with `max_slowdown_pct = 550`, and `16B-ascii-g8` at `reps = 20_000` with `max_slowdown_pct = 600`",
]

MANIFEST_MARKERS = [
    '"id": "hexdump"',
    '"helper": "lib/hexdump.zig"',
    '"zigux/tests/phase6_hexdump_perf.zig"',
    '"zigux/tests/phase6_hexdump_perf_matrix.zig"',
    '"zigux/tests/fixtures/phase6_hexdump_vectors.zig"',
    '"perf_refresh_note": "Documentation/zigux/phase6-hexdump-perf-refresh.md"',
    '"packet_checker": "scripts/zigux/check-phase6-hexdump-packet.py"',
    '"linux_review_route": "make -C zigux phase6-hexdump-review"',
    '"label": "16B-plain-g1"',
    '"label": "32B-ascii-g2"',
    '"label": "16B-ascii-g4"',
    '"label": "16B-ascii-g8"',
]

BUILD_FILE_MARKERS = [
    'const hexdump_module = b.createModule(.{',
    '.root_source_file = b.path("../../lib/hexdump.zig"),',
    'const hexdump_vectors_module = b.createModule(.{',
    '.root_source_file = b.path("fixtures/phase6_hexdump_vectors.zig"),',
    '.root_source_file = b.path("phase6_hexdump.zig"),',
    'hexdump_root_module.addImport("phase6_hexdump_vectors", hexdump_vectors_module);',
    '.root_source_file = b.path("phase6_hexdump_perf_matrix.zig"),',
    '.name = "phase6-hexdump-perf-matrix-tests"',
    '.root_source_file = b.path("phase6_hexdump_perf.zig"),',
    'const hexdump_test_step = b.step("phase6-hexdump-test", "Run Phase 6 hexdump helper tests");',
    'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump perf gate");',
]

MAKEFILE_MARKERS = [
    "PHONY += phase6-validate phase6-test phase6-bsearch-test phase6-base64-c-parity phase6-checksum-c-parity phase6-hexdump-test phase6-hexdump-review phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf phase6-perf phase6",
]

PERF_MATRIX_MARKERS = [
    'const fixtures = @import("phase6_hexdump_vectors");',
    '.label = "16B-plain-g1"',
    '.label = "32B-ascii-g2"',
    '.label = "16B-ascii-g4"',
    '.label = "16B-ascii-g8"',
    "return error.HexdumpPerfMatrixMismatch;",
    'test "phase 6 hexdump perf matrix preflight stays aligned with the documented packet" {',
]

FIXTURE_MARKERS = [
    "pub const length_cases = [_]LengthCase{",
    '.name = "empty plain line reports zero length"',
    '.{ .name = "empty plain line reports zero length", .len = 0, .rowsize = 16, .groupsize = 1, .ascii = false, .expected_length = 0 },',
    'test "phase 6 hexdump curated length packet stays bounded to the documented matrix" {',
    "try std.testing.expectEqual(expected.len, length_cases.len);",
]

SELF_TEST_CASE_COUNT = 17


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


def run_check(root: Path) -> None:
    expect_markers(REQUIRED_FILES["helper_source"], read_text(root, REQUIRED_FILES["helper_source"]), HELPER_SOURCE_MARKERS)
    expect_markers(REQUIRED_FILES["slice_note"], read_text(root, REQUIRED_FILES["slice_note"]), SLICE_NOTE_MARKERS)
    expect_markers(REQUIRED_FILES["lane_sequencing"], read_text(root, REQUIRED_FILES["lane_sequencing"]), LANE_SEQUENCING_MARKERS)
    expect_markers(REQUIRED_FILES["perf_refresh_note"], read_text(root, REQUIRED_FILES["perf_refresh_note"]), PERF_REFRESH_NOTE_MARKERS)
    expect_markers(REQUIRED_FILES["catalog"], read_text(root, REQUIRED_FILES["catalog"]), CATALOG_MARKERS)
    expect_markers(REQUIRED_FILES["perf_survey"], read_text(root, REQUIRED_FILES["perf_survey"]), PERF_SURVEY_MARKERS)
    expect_markers(REQUIRED_FILES["manifest"], read_text(root, REQUIRED_FILES["manifest"]), MANIFEST_MARKERS)
    expect_markers(REQUIRED_FILES["build_file"], read_text(root, REQUIRED_FILES["build_file"]), BUILD_FILE_MARKERS)
    expect_markers(REQUIRED_FILES["makefile"], read_text(root, REQUIRED_FILES["makefile"]), MAKEFILE_MARKERS)
    expect_markers(REQUIRED_FILES["perf_matrix_test"], read_text(root, REQUIRED_FILES["perf_matrix_test"]), PERF_MATRIX_MARKERS)
    expect_markers(REQUIRED_FILES["fixtures"], read_text(root, REQUIRED_FILES["fixtures"]), FIXTURE_MARKERS)

    # These files are still part of the live hexdump packet even when this checker
    # only needs their continued presence rather than a large literal inventory.
    for key in ("focused_test", "perf_test"):
        read_text(root, REQUIRED_FILES[key])


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / REQUIRED_FILES["helper_source"], "\n".join(HELPER_SOURCE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["slice_note"], "\n".join(SLICE_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["lane_sequencing"], "\n".join(LANE_SEQUENCING_MARKERS) + "\n")
    write(root / REQUIRED_FILES["perf_refresh_note"], "\n".join(PERF_REFRESH_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["catalog"], "\n".join(CATALOG_MARKERS) + "\n")
    write(root / REQUIRED_FILES["perf_survey"], "\n".join(PERF_SURVEY_MARKERS) + "\n")
    write(root / REQUIRED_FILES["manifest"], "\n".join(MANIFEST_MARKERS) + "\n")
    write(root / REQUIRED_FILES["build_file"], "\n".join(BUILD_FILE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["makefile"], "\n".join(MAKEFILE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["focused_test"], 'test "phase6 placeholder" {}\n')
    write(root / REQUIRED_FILES["perf_test"], "pub fn main() void {}\n")
    write(root / REQUIRED_FILES["perf_matrix_test"], "\n".join(PERF_MATRIX_MARKERS) + "\n")
    write(root / REQUIRED_FILES["fixtures"], "\n".join(FIXTURE_MARKERS) + "\n")


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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase6_hexdump_packet_"))
    try:
        build_self_test_fixture(tmpdir)
        run_check(tmpdir)

        helper_source = tmpdir / REQUIRED_FILES["helper_source"]
        helper_source.write_text(
            helper_source.read_text(encoding="utf-8").replace(
                "pub fn hexDumpToBuffer(buf: []const u8, rowsize: usize, groupsize: usize, linebuf: []u8, ascii: bool) usize {\n",
                "",
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "pub fn hexDumpToBuffer")

        build_self_test_fixture(tmpdir)
        helper_source = tmpdir / REQUIRED_FILES["helper_source"]
        helper_source.write_text(
            helper_source.read_text(encoding="utf-8").replace(
                'test "hex2bin decodes mixed-case input" {\n',
                "",
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, 'test "hex2bin decodes mixed-case input" {')

        build_self_test_fixture(tmpdir)
        perf_survey = tmpdir / REQUIRED_FILES["perf_survey"]
        perf_survey.write_text(
            perf_survey.read_text(encoding="utf-8").replace("max_slowdown_pct = 550", "max_slowdown_pct = 175", 1),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "max_slowdown_pct = 550")

        build_self_test_fixture(tmpdir)
        manifest = tmpdir / REQUIRED_FILES["manifest"]
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace('"label": "16B-ascii-g8"', '"label": "16B-ascii-g9"', 1),
            encoding="utf-8",
        )
        expect_failure(tmpdir, '"label": "16B-ascii-g8"')

        build_self_test_fixture(tmpdir)
        build_file = tmpdir / REQUIRED_FILES["build_file"]
        build_file.write_text(
            build_file.read_text(encoding="utf-8").replace("phase6-hexdump-perf", "phase6-hexdump-perf-missing", 1),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "phase6-hexdump-perf")

        build_self_test_fixture(tmpdir)
        perf_matrix_test = tmpdir / REQUIRED_FILES["perf_matrix_test"]
        perf_matrix_test.write_text(
            perf_matrix_test.read_text(encoding="utf-8").replace('.label = "16B-ascii-g4"', '.label = "16B-ascii-g5"', 1),
            encoding="utf-8",
        )
        expect_failure(tmpdir, '.label = "16B-ascii-g4"')

        build_self_test_fixture(tmpdir)
        (tmpdir / REQUIRED_FILES["perf_test"]).unlink()
        expect_failure(tmpdir, REQUIRED_FILES["perf_test"])

        build_self_test_fixture(tmpdir)
        fixtures = tmpdir / REQUIRED_FILES["fixtures"]
        fixtures.write_text(
            fixtures.read_text(encoding="utf-8").replace(
                "pub const length_cases = [_]LengthCase{",
                "pub const size_cases = [_]LengthCase{",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "pub const length_cases = [_]LengthCase{")

        build_self_test_fixture(tmpdir)
        fixtures = tmpdir / REQUIRED_FILES["fixtures"]
        fixtures.write_text(
            fixtures.read_text(encoding="utf-8").replace(
                '.{ .name = "empty plain line reports zero length", .len = 0, .rowsize = 16, .groupsize = 1, .ascii = false, .expected_length = 0 },\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, '.{ .name = "empty plain line reports zero length", .len = 0, .rowsize = 16, .groupsize = 1, .ascii = false, .expected_length = 0 },')

        build_self_test_fixture(tmpdir)
        slice_note = tmpdir / REQUIRED_FILES["slice_note"]
        slice_note.write_text(
            slice_note.read_text(encoding="utf-8").replace("four-case fixture-backed slowdown matrix", "two-case slowdown matrix", 1),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "four-case fixture-backed slowdown matrix")

        build_self_test_fixture(tmpdir)
        slice_note = tmpdir / REQUIRED_FILES["slice_note"]
        slice_note.write_text(
            slice_note.read_text(encoding="utf-8").replace(
                "length_cases` packet in `zigux/tests/fixtures/phase6_hexdump_vectors.zig` still keeps the empty plain zero-length row aligned with the focused replay and the helper's landed empty-input contract, but the empty ASCII zero-length row has not been serialized into that helper-local fixture packet yet",
                "length_cases packet drifted",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "length_cases")

        build_self_test_fixture(tmpdir)
        lane_sequencing = tmpdir / REQUIRED_FILES["lane_sequencing"]
        lane_sequencing.write_text(
            lane_sequencing.read_text(encoding="utf-8").replace(
                "### `P6-L19`, `P6-Y07`, `P6-Y08`, and `P6-Y09` hexdump packet\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "P6-L19")

        build_self_test_fixture(tmpdir)
        perf_refresh_note = tmpdir / REQUIRED_FILES["perf_refresh_note"]
        perf_refresh_note.write_text(
            perf_refresh_note.read_text(encoding="utf-8").replace("slowdown_pct = 518", "slowdown_pct = 402", 1),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "slowdown_pct = 518")

        build_self_test_fixture(tmpdir)
        catalog = tmpdir / REQUIRED_FILES["catalog"]
        catalog.write_text(
            catalog.read_text(encoding="utf-8").replace("scripts/zigux/check-phase6-hexdump-packet.py", "scripts/zigux/check-phase6-hexdump-review.py", 1),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "scripts/zigux/check-phase6-hexdump-packet.py")

        build_self_test_fixture(tmpdir)
        (tmpdir / REQUIRED_FILES["helper_source"]).unlink()
        expect_failure(tmpdir, REQUIRED_FILES["helper_source"])

        build_self_test_fixture(tmpdir)
        shutil.rmtree(tmpdir / "Documentation")
        expect_failure(tmpdir, REQUIRED_FILES["slice_note"])

        build_self_test_fixture(tmpdir)
        makefile = tmpdir / REQUIRED_FILES["makefile"]
        makefile.write_text("", encoding="utf-8")
        expect_failure(tmpdir, "phase6-hexdump-review")

        print("PHASE6_HEXDUMP_PACKET_SELF_TEST=pass")
        print(f"PHASE6_HEXDUMP_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(Path(args.root))
    except CheckError as exc:
        print(f"PHASE6_HEXDUMP_PACKET=fail: {exc}")
        return 1

    print("PHASE6_HEXDUMP_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
