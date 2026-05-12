#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 6 hexdump review packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

REQUIRED_FILES = {
    "slice_note": "Documentation/zigux/phase6-hexdump-slice.md",
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

CATALOG_MARKERS = [
    "### hexdump",
    "- direct local packet checker: `python3 scripts/zigux/check-phase6-hexdump-packet.py`",
    "- Linux-style packet review route: `make -C zigux phase6-hexdump-review`",
    "- direct local rerun route: `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig`",
    "- Linux-style rerun route: `make -C zigux phase6-hexdump-test`",
    "- dedicated environment-plumbed review route: the shipped `make -C zigux phase6-hexdump-review` wrapper keeps the helper-local checker plus the focused helper and perf replays on the same `PYTHON` and `ZIG` selection path",
]

PERF_SURVEY_MARKERS = [
    "hexdump shared posture: a dedicated slowdown gate remains wired through `zigux/tests/phase6_hexdump_perf.zig`",
    "hexdump helper-local command posture: `python3 scripts/zigux/check-phase6-hexdump-packet.py` and `make -C zigux phase6-hexdump-review`",
    "hexdump environment posture: the helper-local review route still inherits `PYTHON ?= python3` and `ZIG ?= zig` from `zigux/Makefile`",
]

MANIFEST_MARKERS = [
    '"id": "hexdump"',
    '"zigux/tests/phase6_hexdump_perf_matrix.zig"',
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

SELF_TEST_CASE_COUNT = 12


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


def expect_nonempty(relative_path: str, text: str) -> None:
    if not text.strip():
        raise CheckError(f"empty required file: {relative_path}")


def run_check(root: Path) -> None:
    expect_markers(REQUIRED_FILES["slice_note"], read_text(root, REQUIRED_FILES["slice_note"]), SLICE_NOTE_MARKERS)
    expect_markers(REQUIRED_FILES["catalog"], read_text(root, REQUIRED_FILES["catalog"]), CATALOG_MARKERS)
    expect_markers(REQUIRED_FILES["perf_survey"], read_text(root, REQUIRED_FILES["perf_survey"]), PERF_SURVEY_MARKERS)
    expect_markers(REQUIRED_FILES["manifest"], read_text(root, REQUIRED_FILES["manifest"]), MANIFEST_MARKERS)
    expect_markers(REQUIRED_FILES["build_file"], read_text(root, REQUIRED_FILES["build_file"]), BUILD_FILE_MARKERS)
    expect_markers(REQUIRED_FILES["makefile"], read_text(root, REQUIRED_FILES["makefile"]), MAKEFILE_MARKERS)
    expect_nonempty(REQUIRED_FILES["focused_test"], read_text(root, REQUIRED_FILES["focused_test"]))
    expect_nonempty(REQUIRED_FILES["perf_test"], read_text(root, REQUIRED_FILES["perf_test"]))
    expect_nonempty(REQUIRED_FILES["perf_matrix_test"], read_text(root, REQUIRED_FILES["perf_matrix_test"]))
    expect_nonempty(REQUIRED_FILES["fixtures"], read_text(root, REQUIRED_FILES["fixtures"]))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / REQUIRED_FILES["slice_note"], "\n".join(SLICE_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["catalog"], "\n".join(CATALOG_MARKERS) + "\n")
    write(root / REQUIRED_FILES["perf_survey"], "\n".join(PERF_SURVEY_MARKERS) + "\n")
    write(root / REQUIRED_FILES["manifest"], "\n".join(MANIFEST_MARKERS) + "\n")
    write(root / REQUIRED_FILES["build_file"], "\n".join(BUILD_FILE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["makefile"], "\n".join(MAKEFILE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["focused_test"], 'test "phase6 hexdump focused replay placeholder" {}\n')
    write(root / REQUIRED_FILES["perf_test"], 'const perf_case = "phase6 hexdump perf placeholder";\n')
    write(root / REQUIRED_FILES["perf_matrix_test"], 'test "phase6 hexdump perf matrix placeholder" {}\n')
    write(root / REQUIRED_FILES["fixtures"], "pub const length_cases = [_]u8{0};\n")


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

        slice_note = tmpdir / REQUIRED_FILES["slice_note"]
        slice_note.write_text(slice_note.read_text(encoding="utf-8").replace("`make -C zigux phase6-hexdump-review`\n", ""), encoding="utf-8")
        expect_failure(tmpdir, "`make -C zigux phase6-hexdump-review`")

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
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace('"zigux/tests/phase6_hexdump_perf_matrix.zig"\n', ""),
            encoding="utf-8",
        )
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
        focused_test.write_text("", encoding="utf-8")
        expect_failure(tmpdir, REQUIRED_FILES["focused_test"])

        build_self_test_fixture(tmpdir)
        perf_test = tmpdir / REQUIRED_FILES["perf_test"]
        perf_test.unlink()
        expect_failure(tmpdir, REQUIRED_FILES["perf_test"])

        build_self_test_fixture(tmpdir)
        perf_matrix_test = tmpdir / REQUIRED_FILES["perf_matrix_test"]
        perf_matrix_test.unlink()
        expect_failure(tmpdir, REQUIRED_FILES["perf_matrix_test"])

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
