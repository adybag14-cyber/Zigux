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
    "pub const HexError = error{",
    "pub fn hexDumpLineLength(",
    "pub fn hexDumpToBuffer(",
    "if (len == 0) {",
    "linebuf[0] = 0;",
    "fn normalizedRowsize(rowsize_input: usize) usize {",
    "fn normalizedGroupsize(len: usize, groupsize_input: usize) usize {",
    'test "hexdump grouped plain output stays exact at full and truncated buffer capacity" {',
]

SLICE_NOTE_MARKERS = [
    "`PHASE6_SLICE=hexdump-leaf-helper`",
    "`zigux/tests/phase6_hexdump_perf_matrix.zig`",
    "`scripts/zigux/check-phase6-hexdump-packet.py`",
    "direct local checker route: `python3 scripts/zigux/check-phase6-hexdump-packet.py`",
    "`make -C zigux phase6-hexdump-test`",
    "`make -C zigux phase6-hexdump-perf`",
    "`make -C zigux phase6-hexdump-review`",
    "the helper-local checker, focused replay, perf-matrix preflight, and perf gate under the same `PYTHON` and `ZIG` environment plumbing",
]

LANE_SEQUENCING_MARKERS = [
    "### `P6-L19`, `P6-Y07`, and `P6-Y08` hexdump packet",
    "- `Documentation/zigux/phase6-hexdump-perf-refresh.md`",
    "Treat `P6-L19` as the hexdump parked-survey or slice-note truthfulness lane, `P6-Y07` as the hexdump fixture-governance lane, and `P6-Y08` as the hexdump perf-evidence or serialized empty-ASCII length-packet closure lane when the same helper-local review packet could otherwise overlap itself.",
]

PERF_REFRESH_NOTE_MARKERS = [
    "# Phase 6 Hexdump Perf Refresh Evidence",
    "This note preserves one bounded Phase 6 hexdump perf-gate finding so the `lib/hexdump` packet stays reviewable alongside the now-aligned shared catalog, slice note, manifest, and harness thresholds on `master`.",
    "This note now serves as the bounded rationale for why the grouped ASCII formatter case keeps a higher ceiling than the plain formatter case, not as a placeholder for a still-unlanded threshold refresh.",
]

CATALOG_MARKERS = [
    "### hexdump",
    "- direct local packet checker: `python3 scripts/zigux/check-phase6-hexdump-packet.py`",
    "- Linux-style packet review route: `make -C zigux phase6-hexdump-review`",
    "- direct local rerun route: `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig`",
    "- Linux-style rerun route: `make -C zigux phase6-hexdump-test`",
    "- dedicated environment-plumbed review route: the shipped `make -C zigux phase6-hexdump-review` wrapper keeps the helper-local checker plus the focused helper and perf replays on the same `PYTHON` and `ZIG` selection path",
]

PERF_SURVEY_MARKERS = [
    "hexdump shared posture: the dedicated slowdown gate remains wired through the exact preflight in `zigux/tests/phase6_hexdump_perf_matrix.zig`, the timed replay in `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`",
    "hexdump helper-local command posture: `python3 scripts/zigux/check-phase6-hexdump-packet.py` and `make -C zigux phase6-hexdump-review`",
    "hexdump environment posture: the helper-local review route still inherits `PYTHON ?= python3` and `ZIG ?= zig` from `zigux/Makefile`",
]

MANIFEST_MARKERS = [
    '"id": "hexdump"',
    '"zigux/tests/phase6_hexdump_perf_matrix.zig"',
    '"perf_refresh_note": "Documentation/zigux/phase6-hexdump-perf-refresh.md"',
    '"packet_checker": "scripts/zigux/check-phase6-hexdump-packet.py"',
    '"linux_review_route": "make -C zigux phase6-hexdump-review"',
    '"python3 scripts/zigux/check-phase6-hexdump-packet.py --self-test"',
    '"python3 scripts/zigux/check-phase6-hexdump-packet.py"',
    '"make -C zigux phase6-hexdump-review"',
]

BUILD_FILE_MARKERS = [
    'const hexdump_vectors_module = b.createModule(.{',
    '.root_source_file = b.path("fixtures/phase6_hexdump_vectors.zig"),',
    '.root_source_file = b.path("phase6_hexdump.zig"),',
    'hexdump_root_module.addImport("phase6_hexdump_vectors", hexdump_vectors_module);',
    '.root_source_file = b.path("phase6_hexdump_perf_matrix.zig"),',
    '.name = "phase6-hexdump-perf-matrix-tests"',
    "const run_hexdump_perf_matrix_tests = b.addRunArtifact(hexdump_perf_matrix_tests);",
    '.root_source_file = b.path("phase6_hexdump_perf.zig"),',
    'hexdump_perf_root_module.addImport("phase6_hexdump_vectors", hexdump_vectors_module);',
    'const hexdump_test_step = b.step("phase6-hexdump-test", "Run Phase 6 hexdump helper tests");',
    'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump perf gate");',
    "hexdump_perf_step.dependOn(&run_hexdump_perf_matrix_tests.step);",
]

MAKEFILE_MARKERS = [
    "PHONY += phase6-validate phase6-test phase6-bsearch-test phase6-base64-c-parity phase6-checksum-c-parity phase6-hexdump-test phase6-hexdump-review phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf phase6-perf phase6",
    "phase6-hexdump-review:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-hexdump-packet.py",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
]

FOCUSED_TEST_MARKERS = [
    'try std.testing.expectEqual(@as(usize, 10), fixtures.parity_cases.len);',
    'try std.testing.expectEqual(@as(usize, 4), fixtures.overflow_cases.len);',
    'try std.testing.expectEqual(@as(usize, 9), fixtures.length_cases.len);',
    'try std.testing.expectEqual(@as(usize, 4), fixtures.perf_cases.len);',
    'const normalized_length_case = fixtures.length_cases[7];',
    'const uneven_group_length_case = fixtures.length_cases[8];',
    'test "phase 6 hexdump covers normalization and empty-buffer edge cases" {',
    'try std.testing.expectEqual(@as(usize, 65), hexdump.hexDumpToBuffer(test_data_b[0..16], 7, 3, empty[0..0], true));',
]

PERF_TEST_MARKERS = [
    'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_CASE_COUNT={d}\\n", .{fixtures.perf_cases.len});',
    "const expected = fixtures.prepareExpectedLine(",
    'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_THRESHOLD_PCT={d}\\n", .{ case.label, case.max_slowdown_pct });',
    "if (helper_result.accumulator != reference_result.accumulator) {",
    "return error.HexdumpPerfAccumulatorMismatch;",
    "if (failed) return error.HexdumpPerfRegression;",
]

FIXTURE_MARKERS = [
    'test "phase 6 hexdump curated length packet stays bounded to the documented matrix" {',
    '.{ .name = "empty plain line reports zero length", .len = 0, .rowsize = 16, .groupsize = 1, .ascii = false, .expected_length = 0 },',
    '.{ .name = "uneven group fallback line length", .len = 9, .rowsize = 32, .groupsize = 4, .ascii = false, .expected_length = 26 },',
    'test "phase 6 hexdump perf fixture packet stays bounded to the documented matrix" {',
    '.label = "16B-plain-g1",',
    '.label = "32B-ascii-g2",',
    '.label = "16B-ascii-g4",',
    '.label = "16B-ascii-g8",',
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

SELF_TEST_CASE_COUNT = 21


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
    expect_markers(REQUIRED_FILES["focused_test"], read_text(root, REQUIRED_FILES["focused_test"]), FOCUSED_TEST_MARKERS)
    expect_markers(REQUIRED_FILES["perf_test"], read_text(root, REQUIRED_FILES["perf_test"]), PERF_TEST_MARKERS)
    expect_markers(REQUIRED_FILES["perf_matrix_test"], read_text(root, REQUIRED_FILES["perf_matrix_test"]), PERF_MATRIX_MARKERS)
    expect_markers(REQUIRED_FILES["fixtures"], read_text(root, REQUIRED_FILES["fixtures"]), FIXTURE_MARKERS)


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
    write(root / REQUIRED_FILES["focused_test"], "\n".join(FOCUSED_TEST_MARKERS) + "\n")
    write(root / REQUIRED_FILES["perf_test"], "\n".join(PERF_TEST_MARKERS) + "\n")
    write(root / REQUIRED_FILES["perf_matrix_test"], "\n".join(PERF_MATRIX_MARKERS) + "\n")
    write(root / REQUIRED_FILES["fixtures"], "\n".join(FIXTURE_MARKERS) + "\n")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected self-test failure containing {expected_fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase6_hexdump_packet_"))
    try:
        build_self_test_fixture(tmpdir)
        run_check(tmpdir)

        helper_source = tmpdir / REQUIRED_FILES["helper_source"]
        helper_source.write_text(helper_source.read_text(encoding="utf-8").replace("pub fn hexDumpToBuffer(\n", ""), encoding="utf-8")
        expect_failure(tmpdir, "pub fn hexDumpToBuffer(")

        build_self_test_fixture(tmpdir)
        helper_source = tmpdir / REQUIRED_FILES["helper_source"]
        helper_source.unlink()
        expect_failure(tmpdir, REQUIRED_FILES["helper_source"])

        build_self_test_fixture(tmpdir)
        slice_note = tmpdir / REQUIRED_FILES["slice_note"]
        slice_note.write_text(slice_note.read_text(encoding="utf-8").replace("`make -C zigux phase6-hexdump-review`\n", ""), encoding="utf-8")
        expect_failure(tmpdir, "`make -C zigux phase6-hexdump-review`")

        build_self_test_fixture(tmpdir)
        lane_sequencing = tmpdir / REQUIRED_FILES["lane_sequencing"]
        lane_sequencing.write_text(lane_sequencing.read_text(encoding="utf-8").replace("- `Documentation/zigux/phase6-hexdump-perf-refresh.md`\n", ""), encoding="utf-8")
        expect_failure(tmpdir, "Documentation/zigux/phase6-hexdump-perf-refresh.md")

        build_self_test_fixture(tmpdir)
        perf_refresh_note = tmpdir / REQUIRED_FILES["perf_refresh_note"]
        perf_refresh_note.write_text(perf_refresh_note.read_text(encoding="utf-8").replace("grouped ASCII formatter case keeps a higher ceiling than the plain formatter case", "grouped ASCII formatter case shares one ceiling with the plain formatter case"), encoding="utf-8")
        expect_failure(tmpdir, "grouped ASCII formatter case keeps a higher ceiling than the plain formatter case")

        build_self_test_fixture(tmpdir)
        catalog = tmpdir / REQUIRED_FILES["catalog"]
        catalog.write_text(catalog.read_text(encoding="utf-8").replace("`python3 scripts/zigux/check-phase6-hexdump-packet.py`\n", ""), encoding="utf-8")
        expect_failure(tmpdir, "`python3 scripts/zigux/check-phase6-hexdump-packet.py`")

        build_self_test_fixture(tmpdir)
        perf_survey = tmpdir / REQUIRED_FILES["perf_survey"]
        perf_survey.write_text(perf_survey.read_text(encoding="utf-8").replace("`PYTHON ?= python3` and `ZIG ?= zig`", "`PYTHON` only"), encoding="utf-8")
        expect_failure(tmpdir, "`PYTHON ?= python3` and `ZIG ?= zig`")

        build_self_test_fixture(tmpdir)
        manifest = tmpdir / REQUIRED_FILES["manifest"]
        manifest.write_text(manifest.read_text(encoding="utf-8").replace('"make -C zigux phase6-hexdump-review"\n', ""), encoding="utf-8")
        expect_failure(tmpdir, '"make -C zigux phase6-hexdump-review"')

        build_self_test_fixture(tmpdir)
        manifest = tmpdir / REQUIRED_FILES["manifest"]
        manifest.write_text(manifest.read_text(encoding="utf-8").replace('"perf_refresh_note": "Documentation/zigux/phase6-hexdump-perf-refresh.md"\n', ""), encoding="utf-8")
        expect_failure(tmpdir, '"perf_refresh_note": "Documentation/zigux/phase6-hexdump-perf-refresh.md"')

        build_self_test_fixture(tmpdir)
        manifest = tmpdir / REQUIRED_FILES["manifest"]
        manifest.write_text(manifest.read_text(encoding="utf-8").replace('"zigux/tests/phase6_hexdump_perf_matrix.zig"\n', ""), encoding="utf-8")
        expect_failure(tmpdir, '"zigux/tests/phase6_hexdump_perf_matrix.zig"')

        build_self_test_fixture(tmpdir)
        build_file = tmpdir / REQUIRED_FILES["build_file"]
        build_file.write_text(build_file.read_text(encoding="utf-8").replace("phase6-hexdump-perf", "phase6-hexdump-perf-missing", 1), encoding="utf-8")
        expect_failure(tmpdir, "phase6-hexdump-perf")

        build_self_test_fixture(tmpdir)
        makefile = tmpdir / REQUIRED_FILES["makefile"]
        makefile.write_text(makefile.read_text(encoding="utf-8").replace("$(PYTHON) scripts/zigux/check-phase6-hexdump-packet.py", "$(PYTHON) scripts/zigux/check-phase6-hexdump-review.py"), encoding="utf-8")
        expect_failure(tmpdir, "scripts/zigux/check-phase6-hexdump-packet.py")

        build_self_test_fixture(tmpdir)
        focused_test = tmpdir / REQUIRED_FILES["focused_test"]
        focused_test.write_text(focused_test.read_text(encoding="utf-8").replace('try std.testing.expectEqual(@as(usize, 9), fixtures.length_cases.len);\n', ""), encoding="utf-8")
        expect_failure(tmpdir, "fixtures.length_cases.len")

        build_self_test_fixture(tmpdir)
        focused_test = tmpdir / REQUIRED_FILES["focused_test"]
        focused_test.write_text("", encoding="utf-8")
        expect_failure(tmpdir, REQUIRED_FILES["focused_test"])

        build_self_test_fixture(tmpdir)
        perf_test = tmpdir / REQUIRED_FILES["perf_test"]
        perf_test.write_text(perf_test.read_text(encoding="utf-8").replace("PHASE6_HEXDUMP_PERF_CASE_COUNT", "PHASE6_HEXDUMP_PERF_CASE_TOTAL", 1), encoding="utf-8")
        expect_failure(tmpdir, "PHASE6_HEXDUMP_PERF_CASE_COUNT")

        build_self_test_fixture(tmpdir)
        perf_test = tmpdir / REQUIRED_FILES["perf_test"]
        perf_test.unlink()
        expect_failure(tmpdir, REQUIRED_FILES["perf_test"])

        build_self_test_fixture(tmpdir)
        perf_matrix_test = tmpdir / REQUIRED_FILES["perf_matrix_test"]
        perf_matrix_test.write_text(perf_matrix_test.read_text(encoding="utf-8").replace('.label = "16B-ascii-g8"', '.label = "16B-ascii-g9"', 1), encoding="utf-8")
        expect_failure(tmpdir, '.label = "16B-ascii-g8"')

        build_self_test_fixture(tmpdir)
        perf_matrix_test = tmpdir / REQUIRED_FILES["perf_matrix_test"]
        perf_matrix_test.unlink()
        expect_failure(tmpdir, REQUIRED_FILES["perf_matrix_test"])

        build_self_test_fixture(tmpdir)
        fixtures = tmpdir / REQUIRED_FILES["fixtures"]
        fixtures.write_text(fixtures.read_text(encoding="utf-8").replace('.{ .name = "empty plain line reports zero length", .len = 0, .rowsize = 16, .groupsize = 1, .ascii = false, .expected_length = 0 },\n', ""), encoding="utf-8")
        expect_failure(tmpdir, "empty plain line reports zero length")

        build_self_test_fixture(tmpdir)
        fixtures = tmpdir / REQUIRED_FILES["fixtures"]
        fixtures.write_text("   \n", encoding="utf-8")
        expect_failure(tmpdir, REQUIRED_FILES["fixtures"])

        build_self_test_fixture(tmpdir)
        shutil.rmtree(tmpdir / "Documentation")
        expect_failure(tmpdir, REQUIRED_FILES["slice_note"])

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
