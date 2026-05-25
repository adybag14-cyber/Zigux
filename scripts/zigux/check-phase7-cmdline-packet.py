#!/usr/bin/env python3
"""Validate the current Phase 7 cmdline helper-local packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/phase7-cmdline-slice.md",
    "lib/cmdline.zig",
    "zigux/tests/phase7_cmdline.zig",
    "zigux/tests/phase7_cmdline_survey.zig",
    "zigux/tests/phase7_cmdline_manifest.json",
    "scripts/zigux/check-phase7-cmdline-packet.py",
    "samples/zigux/README.md",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-helper-lane-sequencing.md": [
        "Documentation/zigux/phase7-cmdline-slice.md",
        "samples/zigux/README.md",
        "Fresh helper-local reread for this slot confirmed the dedicated cmdline slice, companion replay, survey, manifest, checker, and no-sample boundary now directly materialize on current `master`",
    ],
    "Documentation/zigux/phase7-cmdline-slice.md": [
        "`PHASE7_STATUS=helper_local_test_survey_manifest_checker_anchor`",
        "`PHASE7_SLICE=cmdline-runtime-leaf`",
        "`PHASE7_LANE_KEY=P7-L08`",
        "`scripts/zigux/check-phase7-cmdline-packet.py`",
        "Treat those surfaces as the current helper-local packet for this slice and keep same-lane follow-through inside that returned survey-backed packet.",
        "Keep same-lane follow-through limited to the returned helper-local survey-manifest-checker truthfulness packet or one bounded parsing replay proof.",
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
        'test "nextArg keeps whitespace-only input as an empty sentinel before the first NUL" {',
        'test "nextArg keeps leading equals tokens as bare parameters" {',
        'test "nextArg keeps quoted leading equals tokens as bare parameters" {',
        'test "nextArg parses bare parameters and keeps the remaining text" {',
        'test "nextArg keeps quoted empty values explicit without swallowing the next token" {',
        'test "nextArg keeps unterminated quoted values inside the current token" {',
        'test "nextArg keeps rest and remaining as the same borrowed suffix view" {',
        'test "getOption preserves incomplete hex-prefix, leading-plus parity, and descending-range behavior" {',
        'test "getOptions expands negative ranges and negative upper bounds" {',
        'test "memparse saturates signed overflow instead of trapping" {',
    ],
    "zigux/tests/phase7_cmdline.zig": [
        'const cmdline = @import("cmdline");',
        'test "phase 7 cmdline companion replays exact bare-option matching boundaries" {',
        'try std.testing.expect(!cmdline.parseOptionStr("quiet,debug\\x00,nohlt", "nohlt"));',
        'try std.testing.expect(cmdline.parseOptionStr("debug,,quiet", ""));',
        'try std.testing.expect(!cmdline.parseOptionStr("debug,", ""));',
        'test "phase 7 cmdline companion replays option decoding, ranges, and malformed-input posture" {',
        'test "phase 7 cmdline companion replays incomplete-hex, leading-plus parity, and descending-range boundaries" {',
        'try std.testing.expectEqualStrings("2,9", descending_rest);',
        'test "phase 7 cmdline companion replays negative range expansion and negative upper-bound posture" {',
        'test "phase 7 cmdline companion replays validator-only getOption cursor movement" {',
        'test "phase 7 cmdline companion replays quoted argument splitting and memparse boundaries" {',
        'test "phase 7 cmdline companion replays leading-plus fallback boundaries" {',
        'test "phase 7 cmdline companion replays memparse signed clamp saturation" {',
    ],
    "zigux/tests/phase7_cmdline_survey.zig": [
        'try std.testing.expectEqualStrings("helper_slice_test_survey_manifest_checker_anchor", manifest.current_master_state);',
        'try expectContains(checker, "PHASE7_CMDLINE_PACKET=pass");',
        'try expectContains(checker, "PHASE7_CMDLINE_PACKET_SELF_TEST=pass");',
        'try expectContains(slice_note, "`PHASE7_STATUS=helper_local_test_survey_manifest_checker_anchor`");',
        'try expectContains(helper, "test \\\"getOption preserves incomplete hex-prefix, leading-plus parity, and descending-range behavior\\\" {");',
        'try expectContains(helper_companion, "phase 7 cmdline companion replays incomplete-hex, leading-plus parity, and descending-range boundaries");',
    ],
    "zigux/tests/phase7_cmdline_manifest.json": [
        '"current_master_state": "helper_slice_test_survey_manifest_checker_anchor"',
        '"scripts/zigux/check-phase7-cmdline-packet.py"',
        '"parseOptionStr"',
        '"memparse"',
        "helper-local survey-manifest-checker truthfulness packet",
    ],
    "scripts/zigux/check-phase7-cmdline-packet.py": [
        "--self-test",
        "PHASE7_CMDLINE_PACKET_SELF_TEST=pass",
        "PHASE7_CMDLINE_PACKET=pass",
        "PHASE7_CMDLINE_PACKET=fail",
        "MISSING_PHASE7_CMDLINE_FILES_START",
        "MISSING_PHASE7_CMDLINE_FILES_END",
        "MISSING_PHASE7_CMDLINE_MARKERS_START",
        "MISSING_PHASE7_CMDLINE_MARKERS_END",
        '"Documentation/zigux/phase7-cmdline-slice.md",',
        '"lib/cmdline.zig",',
    ],
    "samples/zigux/README.md": [
        "Current `master` still ships no standalone Phase 5 sample-root files here for:",
        "* `*cmdline*`",
    ],
}

SELF_TEST_CASE_COUNT = 29


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

    manifest = json.loads(read_text(root / "zigux/tests/phase7_cmdline_manifest.json"))
    if manifest.get("current_master_state") != "helper_slice_test_survey_manifest_checker_anchor":
        return [], ["zigux/tests/phase7_cmdline_manifest.json: current_master_state"]

    return [], collect_missing_markers(root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_root(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES:
        write(tmp_root / rel, "\n".join(REQUIRED_MARKERS[rel]) + "\n")

    write(
        tmp_root / "zigux/tests/phase7_cmdline_manifest.json",
        json.dumps(
            {
                "lane_key": "P7-L08",
                "phase": "Phase 7",
                "verified_on_utc": "2026-05-24T17:30:01Z",
                "anchor": "lib/cmdline.c",
                "current_master_state": "helper_slice_test_survey_manifest_checker_anchor",
                "review_surfaces": [
                    "Documentation/zigux/phase7-helper-lane-sequencing.md",
                    "Documentation/zigux/phase7-cmdline-slice.md",
                    "lib/cmdline.zig",
                    "zigux/tests/phase7_cmdline.zig",
                    "zigux/tests/phase7_cmdline_survey.zig",
                    "zigux/tests/phase7_cmdline_manifest.json",
                    "scripts/zigux/check-phase7-cmdline-packet.py",
                    "samples/zigux/README.md",
                ],
                "covered_helpers": [
                    "parseOptionStr",
                    "parse_option_str",
                    "getOption",
                    "get_option",
                    "getOptions",
                    "get_options",
                    "nextArg",
                    "next_arg",
                    "memparse",
                ],
                "missing_paths": [],
                "ownership_focus": [
                    "parseOptionStr() stays bounded to exact comma-delimited bare options inside the exported C-string prefix",
                    "getOption() and getOptions() keep caller-provided state explicit while preserving Linux-style malformed-input, range, and wraparound behavior",
                    "nextArg() and next_arg() keep parameter, optional value, and remaining text borrowed from the caller slice without widening beyond the exported C-string boundary",
                    "memparse() keeps no-conversion, suffix handling, and signed-clamp posture reviewable without widening into separate allocator-backed helper ownership",
                    "the no-standalone-cmdline sample boundary stays explicit only while `samples/zigux/README.md` keeps `*cmdline*` listed among the no-extra-sample reminders",
                ],
                "next_bounded_step": "Keep same-lane follow-through limited to the returned helper-local survey-manifest-checker truthfulness packet or one bounded parsing replay proof while shared-control routes stay parked outside this helper-local lane.",
            },
            indent=2,
        )
        + "\n",
    )


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
        cases_run = 0

        checker_path = tmp_root / "scripts" / "zigux" / "check-phase7-cmdline-packet.py"
        checker_path.unlink()
        expect_missing_file("missing_checker_file", tmp_root, "scripts/zigux/check-phase7-cmdline-packet.py")
        cases_run += 1
        write_fixture_root(tmp_root)

        mutations = [
            ("Documentation/zigux/phase7-cmdline-slice.md", "`PHASE7_STATUS=helper_local_test_survey_manifest_checker_anchor`", ""),
            ("Documentation/zigux/phase7-cmdline-slice.md", "`scripts/zigux/check-phase7-cmdline-packet.py`", ""),
            ("lib/cmdline.zig", "pub const parse_option_str = parseOptionStr;", ""),
            ("lib/cmdline.zig", 'test "getOption preserves incomplete hex-prefix, leading-plus parity, and descending-range behavior" {', ""),
            ("zigux/tests/phase7_cmdline.zig", 'test "phase 7 cmdline companion replays incomplete-hex, leading-plus parity, and descending-range boundaries" {', ""),
            ("zigux/tests/phase7_cmdline_survey.zig", 'try std.testing.expectEqualStrings("helper_slice_test_survey_manifest_checker_anchor", manifest.current_master_state);', ""),
            ("zigux/tests/phase7_cmdline_survey.zig", 'try expectContains(checker, "PHASE7_CMDLINE_PACKET=pass");', ""),
            ("samples/zigux/README.md", "Current `master` still ships no standalone Phase 5 sample-root files here for:", ""),
            ("samples/zigux/README.md", "* `*cmdline*`", ""),
            ("Documentation/zigux/phase7-helper-lane-sequencing.md", "Documentation/zigux/phase7-cmdline-slice.md", ""),
            ("Documentation/zigux/phase7-helper-lane-sequencing.md", "samples/zigux/README.md", ""),
            ("Documentation/zigux/phase7-helper-lane-sequencing.md", "Fresh helper-local reread for this slot confirmed the dedicated cmdline slice, companion replay, survey, manifest, checker, and no-sample boundary now directly materialize on current `master`", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "--self-test", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "PHASE7_CMDLINE_PACKET_SELF_TEST=pass", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "PHASE7_CMDLINE_PACKET=pass", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "PHASE7_CMDLINE_PACKET=fail", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "MISSING_PHASE7_CMDLINE_FILES_START", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "MISSING_PHASE7_CMDLINE_FILES_END", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "MISSING_PHASE7_CMDLINE_MARKERS_START", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "MISSING_PHASE7_CMDLINE_MARKERS_END", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", '"Documentation/zigux/phase7-cmdline-slice.md",', ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", '"lib/cmdline.zig",', ""),
            ("zigux/tests/phase7_cmdline.zig", 'test "phase 7 cmdline companion replays leading-plus fallback boundaries" {', ""),
            ("lib/cmdline.zig", 'test "memparse saturates signed overflow instead of trapping" {', ""),
        ]

        for rel, old, new in mutations:
            path = tmp_root / rel
            text = read_text(path)
            replaced = text.replace(old, new, 1)
            assert replaced != text, rel
            write(path, replaced)
            expect_missing_marker(f"missing_marker::{rel}::{old}", tmp_root, f"{rel}: {old}")
            cases_run += 1
            write_fixture_root(tmp_root)

        manifest_path = tmp_root / "zigux/tests/phase7_cmdline_manifest.json"
        manifest_marker = "\"scripts/zigux/check-phase7-cmdline-packet.py\""
        manifest = json.loads(read_text(manifest_path))
        manifest["review_surfaces"].remove("scripts/zigux/check-phase7-cmdline-packet.py")
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_checker_path_guard",
            tmp_root,
            f"zigux/tests/phase7_cmdline_manifest.json: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest_marker = "helper-local survey-manifest-checker truthfulness packet"
        manifest["next_bounded_step"] = (
            "Keep same-lane follow-through limited to one bounded parsing replay proof "
            "while shared-control routes stay parked outside this helper-local lane."
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_next_bounded_step_truthfulness_guard",
            tmp_root,
            f"zigux/tests/phase7_cmdline_manifest.json: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest_marker = "\"parseOptionStr\""
        manifest["covered_helpers"].remove("parseOptionStr")
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_covered_helper_guard",
            tmp_root,
            f"zigux/tests/phase7_cmdline_manifest.json: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["current_master_state"] = "helper_slice_test_survey_manifest_anchor"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker("manifest_state_guard", tmp_root, "zigux/tests/phase7_cmdline_manifest.json: current_master_state")
        cases_run += 1

        assert cases_run == SELF_TEST_CASE_COUNT, cases_run
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
