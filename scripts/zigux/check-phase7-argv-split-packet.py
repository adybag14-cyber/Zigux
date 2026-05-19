#!/usr/bin/env python3
"""Validate the current Phase 7 argv_split helper packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/phase7-argv-split-slice.md",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "lib/argv_split.zig",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/phase7_argv_split_survey.zig",
    "samples/zigux/README.md",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-helper-lane-sequencing.md": [
        "- argv-split packet, lane `P7-L09`:",
        "  - `scripts/zigux/check-phase7-argv-split-packet.py`",
        "`argv_split` currently survives through `lib/argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, and `scripts/zigux/check-phase7-argv-split-packet.py`.",
        "`P7-L09` owns only argv-split helper-local parity, survey, manifest, fixture, checker, or reminder drift;",
    ],
    "Documentation/zigux/phase7-argv-split-slice.md": [
        "`PHASE7_STATUS=helper_local_slice_anchor_landed`",
        "`PHASE7_SLICE=argv-split-runtime-leaf`",
        "`Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `scripts/zigux/check-phase7-argv-split-packet.py`, and `samples/zigux/README.md`.",
        "Keep the helper-local survey, manifest, checker, and no-standalone-argv-sample boundary fail-closed on this returned slice anchor",
    ],
    "scripts/zigux/check-phase7-argv-split-packet.py": [
        "--self-test",
        "PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass",
    ],
    "lib/argv_split.zig": [
        "pub const ArgvSplitResult = struct {",
        "pub fn argvSplitWithArgc(",
        "pub fn argvFree(allocator: std.mem.Allocator, result: *ArgvSplitResult) void {",
        "pub fn cArgv(self: *const ArgvSplitResult) [*:null]const ?[*:0]const u8 {",
        'test "argvSplit duplicates the input before tokenizing" {',
        'test "argvSplit reuses the exported empty storage view for blank input without allocating" {',
        'test "argvFree mirrors argv_free release ownership and stays safe after teardown" {',
    ],
    "zigux/tests/phase7_argv_split_manifest.json": [
        '"anchor": "lib/argv_split.c"',
        '"current_master_state": "helper_slice_survey_manifest_anchor"',
        '"covered_helpers": [',
        '"ArgvSplitResult.cArgv"',
        '"Documentation/zigux/phase7-argv-split-slice.md"',
        '"samples/zigux/README.md"',
        "helper-local survey-manifest-checker-slice truthfulness",
        "the no-standalone-argv sample boundary stays explicit only while `samples/zigux/README.md` keeps `*argv*` listed among the no-extra-sample reminders",
    ],
    "zigux/tests/phase7_argv_split_survey.zig": [
        'test "phase 7 argv split survey keeps the helper-local slice anchor truthful" {',
        'try std.testing.expectEqualStrings("helper_slice_survey_manifest_anchor", manifest.current_master_state);',
        'try expectStringSliceContains(manifest.review_surfaces, "Documentation/zigux/phase7-argv-split-slice.md");',
        'const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-argv-split-slice.md");',
        'try expectContains(samples_readme, "* `*argv*`");',
    ],
    "samples/zigux/README.md": [
        "Current `master` still ships no standalone Phase 5 sample-root files here for:",
        "* `*argv*`",
    ],
}

SELF_TEST_CASE_COUNT = 15


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = read_text(root / rel)
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return missing_files, collect_missing_markers(root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_root(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES:
        write(tmp_root / rel, "\n".join(REQUIRED_MARKERS[rel]) + "\n")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [marker], case


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_argv_split_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        sequencing_path = tmp_root / "Documentation" / "zigux" / "phase7-helper-lane-sequencing.md"
        sequencing_path.unlink()
        expect_missing_file(
            "missing_phase7_helper_lane_sequencing",
            tmp_root,
            "Documentation/zigux/phase7-helper-lane-sequencing.md",
        )
        write_fixture_root(tmp_root)

        slice_path = tmp_root / "Documentation" / "zigux" / "phase7-argv-split-slice.md"
        slice_path.unlink()
        expect_missing_file(
            "missing_argv_split_slice",
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md",
        )
        write_fixture_root(tmp_root)

        checker_path = tmp_root / "scripts" / "zigux" / "check-phase7-argv-split-packet.py"
        checker_path.unlink()
        expect_missing_file(
            "missing_argv_split_checker",
            tmp_root,
            "scripts/zigux/check-phase7-argv-split-packet.py",
        )
        write_fixture_root(tmp_root)

        helper_path = tmp_root / "lib" / "argv_split.zig"
        helper_path.unlink()
        expect_missing_file("missing_argv_split_helper", tmp_root, "lib/argv_split.zig")
        write_fixture_root(tmp_root)

        manifest_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_manifest.json"
        manifest_path.unlink()
        expect_missing_file(
            "missing_argv_split_manifest",
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json",
        )
        write_fixture_root(tmp_root)

        survey_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_survey.zig"
        survey_path.unlink()
        expect_missing_file(
            "missing_argv_split_survey",
            tmp_root,
            "zigux/tests/phase7_argv_split_survey.zig",
        )
        write_fixture_root(tmp_root)

        samples_path = tmp_root / "samples" / "zigux" / "README.md"
        samples_path.unlink()
        expect_missing_file("missing_samples_readme", tmp_root, "samples/zigux/README.md")
        write_fixture_root(tmp_root)

        slice_text = read_text(slice_path)
        slice_marker = "Keep the helper-local survey, manifest, checker, and no-standalone-argv-sample boundary fail-closed on this returned slice anchor"
        slice_path.write_text(slice_text.replace(slice_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_slice_next_step_marker",
            tmp_root,
            f"Documentation/zigux/phase7-argv-split-slice.md: {slice_marker}",
        )
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = 'test "argvFree mirrors argv_free release ownership and stays safe after teardown" {'
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_release_ownership_marker",
            tmp_root,
            f"lib/argv_split.zig: {helper_marker}",
        )
        write_fixture_root(tmp_root)

        manifest_text = read_text(manifest_path)
        manifest_marker = '"Documentation/zigux/phase7-argv-split-slice.md"'
        manifest_path.write_text(manifest_text.replace(manifest_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_manifest_slice_review_surface",
            tmp_root,
            f"zigux/tests/phase7_argv_split_manifest.json: {manifest_marker}",
        )
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = 'const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-argv-split-slice.md");'
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_survey_slice_reader",
            tmp_root,
            f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}",
        )
        write_fixture_root(tmp_root)

        samples_text = read_text(samples_path)
        samples_marker = "* `*argv*`"
        samples_path.write_text(samples_text.replace(samples_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_samples_boundary_marker",
            tmp_root,
            f"samples/zigux/README.md: {samples_marker}",
        )
        write_fixture_root(tmp_root)

        manifest_text = read_text(manifest_path)
        manifest_marker = "helper-local survey-manifest-checker-slice truthfulness"
        manifest_path.write_text(manifest_text.replace(manifest_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_manifest_truthfulness_marker",
            tmp_root,
            f"zigux/tests/phase7_argv_split_manifest.json: {manifest_marker}",
        )
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = 'try expectStringSliceContains(manifest.review_surfaces, "Documentation/zigux/phase7-argv-split-slice.md");'
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_survey_manifest_slice_anchor_marker",
            tmp_root,
            f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}",
        )
        write_fixture_root(tmp_root)

        sequencing_text = read_text(sequencing_path)
        sequencing_marker = "`P7-L09` owns only argv-split helper-local parity, survey, manifest, fixture, checker, or reminder drift;"
        sequencing_path.write_text(sequencing_text.replace(sequencing_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_sequencing_lane_ownership_marker",
            tmp_root,
            f"Documentation/zigux/phase7-helper-lane-sequencing.md: {sequencing_marker}",
        )

    print("PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass")
    print(f"PHASE7_ARGV_SPLIT_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="repository root to validate (default: current repository root)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in self-tests instead of validating the repository",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(args.repo_root)
    if missing_files:
        print("PHASE7_ARGV_SPLIT_PACKET=fail")
        print("MISSING_PHASE7_ARGV_SPLIT_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_ARGV_SPLIT_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_ARGV_SPLIT_PACKET=fail")
        print("MISSING_PHASE7_ARGV_SPLIT_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_ARGV_SPLIT_MARKERS_END")
        return 1

    print("PHASE7_ARGV_SPLIT_PACKET=pass")
    print(f"PHASE7_ARGV_SPLIT_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE7_ARGV_SPLIT_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
