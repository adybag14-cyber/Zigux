#!/usr/bin/env python3
"""Validate the current Phase 7 cmdline helper packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/phase7-cmdline-slice.md",
    "scripts/zigux/check-phase7-cmdline-packet.py",
    "lib/cmdline.zig",
    "zigux/tests/phase7_cmdline.zig",
    "zigux/tests/phase7_cmdline_manifest.json",
    "zigux/tests/phase7_cmdline_survey.zig",
    "samples/zigux/README.md",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-helper-lane-sequencing.md": [
        "- cmdline packet, lane `P7-L10`:",
        "  - `Documentation/zigux/phase7-cmdline-slice.md`",
        "  - `samples/zigux/README.md`",
        "Fresh helper-local reread for this slot confirmed the dedicated cmdline slice, companion replay, survey, manifest, checker, and no-sample boundary now directly materialize on current `master`",
        "`P7-L10` owns only cmdline helper-local parity, survey, manifest, checker, or reminder drift;",
    ],
    "Documentation/zigux/phase7-cmdline-slice.md": [
        "`PHASE7_STATUS=helper_local_test_survey_manifest_anchor`",
        "`PHASE7_SLICE=cmdline-runtime-leaf`",
        "Treat those surfaces as the current helper-local packet for this slice and keep same-lane follow-through inside that returned survey-backed packet.",
        "Keep same-lane follow-through limited to the returned helper-local survey-manifest-checker truthfulness packet or one bounded parsing replay proof.",
    ],
    "scripts/zigux/check-phase7-cmdline-packet.py": [
        "--self-test",
        "PHASE7_CMDLINE_PACKET_SELF_TEST=pass",
        "\"Documentation/zigux/phase7-cmdline-slice.md\",",
    ],
    "lib/cmdline.zig": [
        "pub fn parseOptionStr",
        "pub const parse_option_str = parseOptionStr;",
        "pub fn getOption",
        "pub const get_option = getOption;",
        "pub fn getOptions",
        "pub const get_options = getOptions;",
        "pub fn nextArg",
        "pub const next_arg = nextArg;",
        "pub fn memparse",
    ],
    "zigux/tests/phase7_cmdline.zig": [
        'const cmdline = @import("cmdline");',
        'test "phase 7 cmdline companion replays exact bare-option matching boundaries" {',
        'test "phase 7 cmdline companion replays option decoding, ranges, and malformed-input posture" {',
        'test "phase 7 cmdline companion replays quoted argument splitting and memparse boundaries" {',
        'test "phase 7 cmdline companion replays leading-whitespace sentinels and quoted full-token boundaries" {',
    ],
    "zigux/tests/phase7_cmdline_manifest.json": [
        '"anchor": "lib/cmdline.c"',
        '"current_master_state": "helper_slice_test_survey_manifest_anchor"',
        '"scripts/zigux/check-phase7-cmdline-packet.py"',
        "helper-local survey-manifest-checker truthfulness packet",
    ],
    "zigux/tests/phase7_cmdline_survey.zig": [
        'test "phase 7 cmdline survey keeps the returned helper-local packet truthful" {',
        'try std.testing.expectEqualStrings("helper_slice_test_survey_manifest_anchor", manifest.current_master_state);',
        'const checker = try readRepoFile(allocator, checker_path);',
    ],
    "samples/zigux/README.md": [
        "Current `master` still ships no standalone Phase 5 sample-root files here for:",
        "* `*cmdline*`",
    ],
}

SELF_TEST_CASE_COUNT = 11


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
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        companion_path = tmp_root / "zigux" / "tests" / "phase7_cmdline.zig"
        companion_path.unlink()
        expect_missing_file(
            "missing_cmdline_companion",
            tmp_root,
            "zigux/tests/phase7_cmdline.zig",
        )
        write_fixture_root(tmp_root)

        sequencing_path = tmp_root / "Documentation" / "zigux" / "phase7-helper-lane-sequencing.md"
        sequencing_text = read_text(sequencing_path)
        sequencing_marker = "`P7-L10` owns only cmdline helper-local parity, survey, manifest, checker, or reminder drift;"
        sequencing_path.write_text(
            sequencing_text.replace(sequencing_marker + "\n", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "missing_sequencing_owner_marker",
            tmp_root,
            f"Documentation/zigux/phase7-helper-lane-sequencing.md: {sequencing_marker}",
        )
        write_fixture_root(tmp_root)

        sequencing_text = read_text(sequencing_path)
        sequencing_samples_marker = "  - `samples/zigux/README.md`"
        sequencing_path.write_text(
            sequencing_text.replace(sequencing_samples_marker + "\n", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "missing_sequencing_samples_boundary_marker",
            tmp_root,
            f"Documentation/zigux/phase7-helper-lane-sequencing.md: {sequencing_samples_marker}",
        )
        write_fixture_root(tmp_root)

        slice_path = tmp_root / "Documentation" / "zigux" / "phase7-cmdline-slice.md"
        slice_text = read_text(slice_path)
        slice_marker = "Keep same-lane follow-through limited to the returned helper-local survey-manifest-checker truthfulness packet or one bounded parsing replay proof."
        slice_path.write_text(slice_text.replace(slice_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_slice_next_step_marker",
            tmp_root,
            f"Documentation/zigux/phase7-cmdline-slice.md: {slice_marker}",
        )
        write_fixture_root(tmp_root)

        checker_path = tmp_root / "scripts" / "zigux" / "check-phase7-cmdline-packet.py"
        checker_text = read_text(checker_path)
        checker_marker = "PHASE7_CMDLINE_PACKET_SELF_TEST=pass"
        checker_path.write_text(checker_text.replace(checker_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_checker_selftest_pass_marker",
            tmp_root,
            f"scripts/zigux/check-phase7-cmdline-packet.py: {checker_marker}",
        )
        write_fixture_root(tmp_root)

        helper_path = tmp_root / "lib" / "cmdline.zig"
        helper_text = read_text(helper_path)
        helper_marker = "pub fn nextArg"
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_helper_nextarg_marker",
            tmp_root,
            f"lib/cmdline.zig: {helper_marker}",
        )
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_alias_marker = "pub const next_arg = nextArg;"
        helper_path.write_text(
            helper_text.replace(helper_alias_marker + "\n", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "missing_helper_nextarg_alias_marker",
            tmp_root,
            f"lib/cmdline.zig: {helper_alias_marker}",
        )
        write_fixture_root(tmp_root)

        manifest_path = tmp_root / "zigux" / "tests" / "phase7_cmdline_manifest.json"
        manifest_text = read_text(manifest_path)
        manifest_marker = '"scripts/zigux/check-phase7-cmdline-packet.py"'
        manifest_path.write_text(manifest_text.replace(manifest_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_manifest_checker_marker",
            tmp_root,
            f"zigux/tests/phase7_cmdline_manifest.json: {manifest_marker}",
        )
        write_fixture_root(tmp_root)

        survey_path = tmp_root / "zigux" / "tests" / "phase7_cmdline_survey.zig"
        survey_text = read_text(survey_path)
        survey_marker = 'const checker = try readRepoFile(allocator, checker_path);'
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_survey_checker_reader",
            tmp_root,
            f"zigux/tests/phase7_cmdline_survey.zig: {survey_marker}",
        )
        write_fixture_root(tmp_root)

        companion_text = read_text(companion_path)
        companion_marker = 'test "phase 7 cmdline companion replays leading-whitespace sentinels and quoted full-token boundaries" {'
        companion_path.write_text(companion_text.replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_companion_leading_whitespace_boundary_marker",
            tmp_root,
            f"zigux/tests/phase7_cmdline.zig: {companion_marker}",
        )
        write_fixture_root(tmp_root)

        samples_path = tmp_root / "samples" / "zigux" / "README.md"
        samples_text = read_text(samples_path)
        samples_marker = "* `*cmdline*`"
        samples_path.write_text(samples_text.replace(samples_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_samples_cmdline_boundary",
            tmp_root,
            f"samples/zigux/README.md: {samples_marker}",
        )
        write_fixture_root(tmp_root)

    print("PHASE7_CMDLINE_PACKET_SELF_TEST=pass")
    print(f"PHASE7_CMDLINE_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")


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
        print("PHASE7_CMDLINE_PACKET=fail")
        print("MISSING_PHASE7_CMDLINE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_CMDLINE_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_CMDLINE_PACKET=fail")
        print("MISSING_PHASE7_CMDLINE_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_CMDLINE_MARKERS_END")
        return 1

    print("PHASE7_CMDLINE_PACKET=pass")
    print(f"PHASE7_CMDLINE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE7_CMDLINE_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())