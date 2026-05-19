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
    "zigux/tests/phase7_argv_split.zig",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/phase7_argv_split_survey.zig",
    "samples/zigux/README.md",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-helper-lane-sequencing.md": [
        "- argv-split packet, lane `P7-L09`:",
        "  - `zigux/tests/phase7_argv_split.zig`",
        "`P7-L09` owns only argv-split helper-local parity, survey, manifest, fixture, checker, or reminder drift;",
    ],
    "Documentation/zigux/phase7-argv-split-slice.md": [
        "`PHASE7_STATUS=helper_local_test_packet_landed`",
        "`PHASE7_SLICE=argv-split-runtime-leaf`",
        "`Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `scripts/zigux/check-phase7-argv-split-packet.py`, and `samples/zigux/README.md`.",
        "Keep the dedicated argv_split replay, survey, manifest, checker, and no-standalone-argv-sample boundary fail-closed",
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
    ],
    "zigux/tests/phase7_argv_split.zig": [
        'const argv_split = @import("argv_split");',
        'test "phase 7 argv split companion replays copied-storage token ownership" {',
        'test "phase 7 argv split companion replays blank-input sentinel reuse and first-NUL truncation" {',
        'test "phase 7 argv split companion replays caller-owned teardown and failure boundaries" {',
    ],
    "zigux/tests/phase7_argv_split_manifest.json": [
        '"anchor": "lib/argv_split.c"',
        '"current_master_state": "helper_slice_test_survey_manifest_anchor"',
        '"zigux/tests/phase7_argv_split.zig"',
        "helper-local survey-manifest-checker truthfulness",
    ],
    "zigux/tests/phase7_argv_split_survey.zig": [
        'test "phase 7 argv split survey keeps the returned helper-local packet truthful" {',
        'try std.testing.expectEqualStrings("helper_slice_test_survey_manifest_anchor", manifest.current_master_state);',
        'const helper_companion = try readRepoFile(allocator, "zigux/tests/phase7_argv_split.zig");',
    ],
    "samples/zigux/README.md": [
        "Current `master` still ships no standalone Phase 5 sample-root files here for:",
        "* `*argv*`",
    ],
}

SELF_TEST_CASE_COUNT = 12


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

        companion_path = tmp_root / "zigux" / "tests" / "phase7_argv_split.zig"
        companion_path.unlink()
        expect_missing_file(
            "missing_argv_split_companion",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig",
        )
        write_fixture_root(tmp_root)

        slice_path = tmp_root / "Documentation" / "zigux" / "phase7-argv-split-slice.md"
        slice_text = read_text(slice_path)
        slice_marker = "Keep the dedicated argv_split replay, survey, manifest, checker, and no-standalone-argv-sample boundary fail-closed"
        slice_path.write_text(slice_text.replace(slice_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_slice_companion_marker",
            tmp_root,
            f"Documentation/zigux/phase7-argv-split-slice.md: {slice_marker}",
        )
        write_fixture_root(tmp_root)

        manifest_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_manifest.json"
        manifest_text = read_text(manifest_path)
        manifest_marker = '"zigux/tests/phase7_argv_split.zig"'
        manifest_path.write_text(manifest_text.replace(manifest_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_manifest_companion_marker",
            tmp_root,
            f"zigux/tests/phase7_argv_split_manifest.json: {manifest_marker}",
        )
        write_fixture_root(tmp_root)

        survey_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_survey.zig"
        survey_text = read_text(survey_path)
        survey_marker = 'const helper_companion = try readRepoFile(allocator, "zigux/tests/phase7_argv_split.zig");'
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_survey_companion_reader",
            tmp_root,
            f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}",
        )
        write_fixture_root(tmp_root)

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