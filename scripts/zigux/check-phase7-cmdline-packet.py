#!/usr/bin/env python3
"""Validate the current Phase 7 cmdline helper-local packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

EXPECTED_MANIFEST_LANE_KEY = "P7-L08"
EXPECTED_MANIFEST_PHASE = "Phase 7"
EXPECTED_MANIFEST_ANCHOR = "lib/cmdline.c"
EXPECTED_MANIFEST_STATE = "helper_slice_test_survey_manifest_checker_anchor"
EXPECTED_MANIFEST_NEXT_BOUNDED_STEP = (
    "Keep same-lane follow-through limited to the returned helper-local survey-manifest-checker "
    "truthfulness packet or one bounded parsing replay proof while shared-control routes stay "
    "parked outside this helper-local lane."
)
EXPECTED_REVIEW_SURFACES = [
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/phase7-cmdline-slice.md",
    "lib/cmdline.zig",
    "zigux/tests/phase7_cmdline.zig",
    "zigux/tests/phase7_cmdline_survey.zig",
    "zigux/tests/phase7_cmdline_manifest.json",
    "zigux/tests/phase7_cmdline_survey_build.zig",
    "scripts/zigux/check-phase7-cmdline-packet.py",
    "samples/zigux/README.md",
]
EXPECTED_COVERED_HELPERS = [
    "parseOptionStr",
    "parse_option_str",
    "getOption",
    "get_option",
    "getOptions",
    "get_options",
    "nextArg",
    "next_arg",
    "memparse",
]
EXPECTED_OWNERSHIP_FOCUS = [
    "parseOptionStr() stays bounded to exact comma-delimited bare options inside the exported C-string prefix",
    "getOption() and getOptions() keep caller-provided state explicit while preserving Linux-style malformed-input, range, and wraparound behavior",
    "the dedicated `get_option` alias replay keeps leading-plus and range-style cursor movement explicit beside the primary `getOption()` entry point",
    "nextArg() and next_arg() keep parameter, optional value, and remaining text borrowed from the caller slice without widening beyond the exported C-string boundary",
    "nextArg() also keeps `rest` and `remaining` as the same borrowed suffix view, including quoted-empty-value paths, so post-token cursor handling stays on one ownership track",
    "memparse() keeps no-conversion, suffix handling, and signed-clamp posture reviewable without widening into separate allocator-backed helper ownership",
    "the dedicated `zig build phase7-cmdline-survey --build-file zigux/tests/phase7_cmdline_survey_build.zig` route keeps this helper-local survey replay runnable without widening into shared Phase 7 tests-root ownership",
    "the no-standalone-cmdline sample boundary stays explicit only while `samples/zigux/README.md` keeps `*cmdline*` listed among the no-extra-sample reminders",
]

REQUIRED_FILES = [
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/phase7-cmdline-slice.md",
    "lib/cmdline.zig",
    "zigux/tests/phase7_cmdline.zig",
    "zigux/tests/phase7_cmdline_survey.zig",
    "zigux/tests/phase7_cmdline_manifest.json",
    "zigux/tests/phase7_cmdline_survey_build.zig",
    "scripts/zigux/check-phase7-cmdline-packet.py",
    "samples/zigux/README.md",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-helper-lane-sequencing.md": [
        "Documentation/zigux/phase7-cmdline-slice.md",
        "samples/zigux/README.md",
        "Fresh helper-local reread for this slot confirmed the dedicated cmdline slice, companion replay, survey, manifest, checker, and no-sample-boundary now directly materialize on current `master`",
        "Current lane evidence also keeps `P7-L10` inside that same helper-local cleanup family, so cmdline-local review-noise, survey-checker-manifest drift, and no-sample-boundary upkeep should stay inside the returned cmdline packet instead of being rerouted as a second helper owner or shared-control drift.",
    ],
    "Documentation/zigux/phase7-cmdline-slice.md": [
        "`PHASE7_STATUS=helper_local_test_survey_manifest_checker_anchor`",
        "`PHASE7_SLICE=cmdline-runtime-leaf`",
        "`PHASE7_LANE_KEY=P7-L08`",
        "`zigux/tests/phase7_cmdline_survey_build.zig`",
        "`scripts/zigux/check-phase7-cmdline-packet.py`",
        "Treat those surfaces as the current helper-local packet for this slice and keep same-lane follow-through inside that returned survey-backed packet.",
        "Keep same-lane follow-through limited to the returned helper-local survey-manifest-checker truthfulness packet or one bounded parsing replay proof.",
        "including leading equals-prefixed bare tokens that must not be rewritten into synthetic key-value pairs",
        "nextArg() also keeps `rest` and `remaining` as the same borrowed suffix view, including quoted-empty-value paths, so post-token cursor handling stays on one ownership track",
        "dedicated `getOption()` and `get_option` cursor replay across leading-plus and range-style inputs so alias-only call sites stay reviewable beside the primary helper entry point",
        "zig build phase7-cmdline-survey --build-file zigux/tests/phase7_cmdline_survey_build.zig",
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
        "test \"nextArg keeps whitespace-only input as an empty sentinel before the first NUL\" {",
        "test \"nextArg keeps leading equals tokens as bare parameters\" {",
        "test \"nextArg keeps quoted leading equals tokens as bare parameters\" {",
        "test \"nextArg parses bare parameters and keeps the remaining text\" {",
        "test \"nextArg keeps quoted empty values explicit without swallowing the next token\" {",
        "test \"nextArg keeps unterminated quoted values inside the current token\" {",
        "test \"nextArg keeps rest and remaining as the same borrowed suffix view\" {",
        "test \"getOption preserves incomplete hex-prefix, leading-plus parity, and descending-range behavior\" {",
        "test \"getOptions expands negative ranges and negative upper bounds\" {",
        "test \"memparse saturates signed overflow instead of trapping\" {",
        "test \"memparse keeps leading-plus incomplete hex and no-digit fallbacks reviewable\" {",
    ],
    "zigux/tests/phase7_cmdline.zig": [
        "const cmdline = @import(\"cmdline\");",
        "test \"phase 7 cmdline companion replays exact bare-option matching boundaries\" {",
        "try std.testing.expect(!cmdline.parseOptionStr(\"quiet,debug\\x00,nohlt\", \"nohlt\"));",
        "try std.testing.expect(cmdline.parseOptionStr(\"debug,,quiet\", \"\"));",
        "try std.testing.expect(!cmdline.parseOptionStr(\"debug,\", \"\"));",
        "test \"phase 7 cmdline companion replays option decoding, ranges, and malformed-input posture\" {",
        "test \"phase 7 cmdline companion replays incomplete-hex, leading-plus parity, and descending-range boundaries\" {",
        "try std.testing.expectEqualStrings(\"2,9\", descending_rest);",
        "test \"phase 7 cmdline companion replays negative range expansion and negative upper-bound posture\" {",
        "test \"phase 7 cmdline companion replays validator-only getOption cursor movement\" {",
        "test \"phase 7 cmdline companion replays get_option alias cursor parity\" {",
        "test \"phase 7 cmdline companion replays quoted argument splitting and memparse boundaries\" {",
        "test \"phase 7 cmdline companion replays leading-plus fallback boundaries\" {",
        "test \"phase 7 cmdline companion replays memparse signed clamp saturation\" {",
        "test \"phase 7 cmdline companion replays borrowed nextArg suffix ownership\" {",
    ],
    "zigux/tests/phase7_cmdline_survey.zig": [
        "try std.testing.expectEqualStrings(\"helper_slice_test_survey_manifest_checker_anchor\", manifest.current_master_state);",
        "try expectContains(checker, \"PHASE7_CMDLINE_PACKET=pass\");",
        "try expectContains(slice_note, \"including leading equals-prefixed bare tokens that must not be rewritten into synthetic key-value pairs\");",
        "try expectContains(sequencing_note, \"Current lane evidence also keeps `P7-L10` inside that same helper-local cleanup family, so cmdline-local review-noise, survey-checker-manifest drift, and no-sample-boundary upkeep should stay inside the returned cmdline packet instead of being rerouted as a second helper owner or shared-control drift.\");",
        "try expectContains(helper, \"test \\\"getOption preserves incomplete hex-prefix, leading-plus parity, and descending-range behavior\\\" {\");",
        "try expectContains(helper_companion, \"phase 7 cmdline companion replays incomplete-hex, leading-plus parity, and descending-range boundaries\");",
    ],
    "zigux/tests/phase7_cmdline_manifest.json": [
        "\"current_master_state\": \"helper_slice_test_survey_manifest_checker_anchor\"",
        "\"zigux/tests/phase7_cmdline_survey_build.zig\"",
        "\"scripts/zigux/check-phase7-cmdline-packet.py\"",
        "\"parseOptionStr\"",
        "\"memparse\"",
        "helper-local survey-manifest-checker truthfulness packet",
        "zig build phase7-cmdline-survey --build-file zigux/tests/phase7_cmdline_survey_build.zig",
    ],
    "zigux/tests/phase7_cmdline_survey_build.zig": [
        "phase7_cmdline_survey.zig",
        "phase7-cmdline-survey",
        "Run the Phase 7 cmdline survey anchor from the shared tests root",
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
        "MISMATCHED_PHASE7_CMDLINE_COUNTS_START",
        "MISMATCHED_PHASE7_CMDLINE_COUNTS_END",
        "\\\"Documentation/zigux/phase7-cmdline-slice.md\\\",",
        "\\\"lib/cmdline.zig\\\",",
        "\\\"zigux/tests/phase7_cmdline_survey_build.zig\\\",",
        "EXPECTED_MANIFEST_LANE_KEY = \"P7-L08\"",
        "EXPECTED_MANIFEST_PHASE = \"Phase 7\"",
        "EXPECTED_MANIFEST_ANCHOR = \"lib/cmdline.c\"",
        "EXPECTED_MANIFEST_STATE = \"helper_slice_test_survey_manifest_checker_anchor\"",
        "EXPECTED_MANIFEST_NEXT_BOUNDED_STEP = (",
        "EXPECTED_REVIEW_SURFACES = [",
        "EXPECTED_COVERED_HELPERS = [",
        "EXPECTED_OWNERSHIP_FOCUS = [",
        "the dedicated `zig build phase7-cmdline-survey --build-file zigux/tests/phase7_cmdline_survey_build.zig` route keeps this helper-local survey replay runnable without widening into shared Phase 7 tests-root ownership",
    ],
    "samples/zigux/README.md": [
        "Current `master` still ships no standalone Phase 5 sample-root files here for:",
        "* `*cmdline*`",
    ],
}

COUNTED_MARKERS = {
    "samples/zigux/README.md": [
        ("* `*cmdline*`", 1),
    ],
}

SELF_TEST_CASE_COUNT = 69


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


def collect_mismatched_counts(root: Path) -> list[str]:
    mismatches: list[str] = []
    for rel, markers in COUNTED_MARKERS.items():
        text = read_text(root / rel)
        for marker, expected in markers:
            actual = text.count(marker)
            if actual != expected:
                mismatches.append(f"{rel}: expected {expected} occurrence(s) of {marker!r}, found {actual}")
    return mismatches


def collect_missing_manifest_entries(manifest: dict[str, object]) -> list[str]:
    missing: list[str] = []

    review_surfaces = manifest.get("review_surfaces")
    if not isinstance(review_surfaces, list):
        return ["zigux/tests/phase7_cmdline_manifest.json: review_surfaces"]
    for item in EXPECTED_REVIEW_SURFACES:
        if item not in review_surfaces:
            missing.append(f"zigux/tests/phase7_cmdline_manifest.json: review_surfaces: {item}")

    covered_helpers = manifest.get("covered_helpers")
    if not isinstance(covered_helpers, list):
        return ["zigux/tests/phase7_cmdline_manifest.json: covered_helpers"]
    for item in EXPECTED_COVERED_HELPERS:
        if item not in covered_helpers:
            missing.append(f"zigux/tests/phase7_cmdline_manifest.json: covered_helpers: {item}")

    ownership_focus = manifest.get("ownership_focus")
    if not isinstance(ownership_focus, list):
        return ["zigux/tests/phase7_cmdline_manifest.json: ownership_focus"]
    for item in EXPECTED_OWNERSHIP_FOCUS:
        if item not in ownership_focus:
            missing.append(f"zigux/tests/phase7_cmdline_manifest.json: ownership_focus: {item}")

    missing_paths = manifest.get("missing_paths")
    if missing_paths != []:
        missing.append("zigux/tests/phase7_cmdline_manifest.json: missing_paths")

    if manifest.get("next_bounded_step") != EXPECTED_MANIFEST_NEXT_BOUNDED_STEP:
        missing.append("zigux/tests/phase7_cmdline_manifest.json: next_bounded_step")

    return missing


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []

    manifest = json.loads(read_text(root / "zigux/tests/phase7_cmdline_manifest.json"))
    if manifest.get("lane_key") != EXPECTED_MANIFEST_LANE_KEY:
        return [], ["zigux/tests/phase7_cmdline_manifest.json: lane_key"], []
    if manifest.get("phase") != EXPECTED_MANIFEST_PHASE:
        return [], ["zigux/tests/phase7_cmdline_manifest.json: phase"], []
    if manifest.get("anchor") != EXPECTED_MANIFEST_ANCHOR:
        return [], ["zigux/tests/phase7_cmdline_manifest.json: anchor"], []
    if manifest.get("current_master_state") != EXPECTED_MANIFEST_STATE:
        return [], ["zigux/tests/phase7_cmdline_manifest.json: current_master_state"], []

    missing_manifest_entries = collect_missing_manifest_entries(manifest)
    if missing_manifest_entries:
        return [], missing_manifest_entries, []

    return [], collect_missing_markers(root), collect_mismatched_counts(root)


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
                "lane_key": EXPECTED_MANIFEST_LANE_KEY,
                "phase": EXPECTED_MANIFEST_PHASE,
                "verified_on_utc": "2026-05-24T17:30:01Z",
                "anchor": EXPECTED_MANIFEST_ANCHOR,
                "current_master_state": EXPECTED_MANIFEST_STATE,
                "review_surfaces": EXPECTED_REVIEW_SURFACES,
                "covered_helpers": EXPECTED_COVERED_HELPERS,
                "missing_paths": [],
                "ownership_focus": EXPECTED_OWNERSHIP_FOCUS,
                "next_bounded_step": EXPECTED_MANIFEST_NEXT_BOUNDED_STEP,
            },
            indent=2,
        )
        + "\n",
    )


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers, mismatched_counts = validate(tmp_root)
    assert missing_markers == [], case
    assert mismatched_counts == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers, mismatched_counts = validate(tmp_root)
    assert missing_files == [], case
    assert mismatched_counts == [], case
    assert missing_markers == [marker], case


def expect_mismatched_count(case: str, tmp_root: Path, mismatch: str) -> None:
    missing_files, missing_markers, mismatched_counts = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [], case
    assert mismatched_counts == [mismatch], case


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [], [])
        cases_run = 0

        checker_path = tmp_root / "scripts" / "zigux" / "check-phase7-cmdline-packet.py"
        checker_path.unlink()
        expect_missing_file("missing_checker_file", tmp_root, "scripts/zigux/check-phase7-cmdline-packet.py")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_build_path = tmp_root / "zigux" / "tests" / "phase7_cmdline_survey_build.zig"
        survey_build_path.unlink()
        expect_missing_file("missing_survey_build_file", tmp_root, "zigux/tests/phase7_cmdline_survey_build.zig")
        cases_run += 1
        write_fixture_root(tmp_root)

        mutations = [
            ("Documentation/zigux/phase7-cmdline-slice.md", "`PHASE7_STATUS=helper_local_test_survey_manifest_checker_anchor`", ""),
            ("Documentation/zigux/phase7-cmdline-slice.md", "`zigux/tests/phase7_cmdline_survey_build.zig`", ""),
            ("Documentation/zigux/phase7-cmdline-slice.md", "`scripts/zigux/check-phase7-cmdline-packet.py`", ""),
            ("Documentation/zigux/phase7-cmdline-slice.md", "including leading equals-prefixed bare tokens that must not be rewritten into synthetic key-value pairs", ""),
            ("Documentation/zigux/phase7-cmdline-slice.md", "nextArg() also keeps `rest` and `remaining` as the same borrowed suffix view, including quoted-empty-value paths, so post-token cursor handling stays on one ownership track", ""),
            ("Documentation/zigux/phase7-cmdline-slice.md", "Keep same-lane follow-through limited to the returned helper-local survey-manifest-checker truthfulness packet or one bounded parsing replay proof.", ""),
            ("Documentation/zigux/phase7-cmdline-slice.md", "dedicated `getOption()` and `get_option` cursor replay across leading-plus and range-style inputs so alias-only call sites stay reviewable beside the primary helper entry point", ""),
            ("Documentation/zigux/phase7-cmdline-slice.md", "zig build phase7-cmdline-survey --build-file zigux/tests/phase7_cmdline_survey_build.zig", ""),
            ("lib/cmdline.zig", "pub const parse_option_str = parseOptionStr;", ""),
            ("lib/cmdline.zig", "test \"nextArg keeps leading equals tokens as bare parameters\" {", ""),
            ("lib/cmdline.zig", "test \"getOption preserves incomplete hex-prefix, leading-plus parity, and descending-range behavior\" {", ""),
            ("lib/cmdline.zig", "test \"memparse keeps leading-plus incomplete hex and no-digit fallbacks reviewable\" {", ""),
            ("zigux/tests/phase7_cmdline.zig", "test \"phase 7 cmdline companion replays incomplete-hex, leading-plus parity, and descending-range boundaries\" {", ""),
            ("zigux/tests/phase7_cmdline.zig", "try std.testing.expectEqualStrings(\"2,9\", descending_rest);", ""),
            ("zigux/tests/phase7_cmdline.zig", "test \"phase 7 cmdline companion replays get_option alias cursor parity\" {", ""),
            ("zigux/tests/phase7_cmdline.zig", "test \"phase 7 cmdline companion replays borrowed nextArg suffix ownership\" {", ""),
            ("zigux/tests/phase7_cmdline_survey.zig", "try std.testing.expectEqualStrings(\"helper_slice_test_survey_manifest_checker_anchor\", manifest.current_master_state);", ""),
            ("zigux/tests/phase7_cmdline_survey.zig", "try expectContains(checker, \"PHASE7_CMDLINE_PACKET=pass\");", ""),
            ("zigux/tests/phase7_cmdline_survey.zig", "try expectContains(slice_note, \"including leading equals-prefixed bare tokens that must not be rewritten into synthetic key-value pairs\");", ""),
            ("zigux/tests/phase7_cmdline_survey.zig", "try expectContains(sequencing_note, \"Current lane evidence also keeps `P7-L10` inside that same helper-local cleanup family, so cmdline-local review-noise, survey-checker-manifest drift, and no-sample-boundary upkeep should stay inside the returned cmdline packet instead of being rerouted as a second helper owner or shared-control drift.\");", ""),
            ("samples/zigux/README.md", "Current `master` still ships no standalone Phase 5 sample-root files here for:", ""),
            ("Documentation/zigux/phase7-helper-lane-sequencing.md", "Documentation/zigux/phase7-cmdline-slice.md", ""),
            ("Documentation/zigux/phase7-helper-lane-sequencing.md", "samples/zigux/README.md", ""),
            ("Documentation/zigux/phase7-helper-lane-sequencing.md", "Fresh helper-local reread for this slot confirmed the dedicated cmdline slice, companion replay, survey, manifest, checker, and no-sample-boundary now directly materialize on current `master`", ""),
            ("Documentation/zigux/phase7-helper-lane-sequencing.md", "Current lane evidence also keeps `P7-L10` inside that same helper-local cleanup family, so cmdline-local review-noise, survey-checker-manifest drift, and no-sample-boundary upkeep should stay inside the returned cmdline packet instead of being rerouted as a second helper owner or shared-control drift.", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "--self-test", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "PHASE7_CMDLINE_PACKET_SELF_TEST=pass", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "PHASE7_CMDLINE_PACKET=pass", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "PHASE7_CMDLINE_PACKET=fail", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "MISSING_PHASE7_CMDLINE_FILES_START", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "MISSING_PHASE7_CMDLINE_FILES_END", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "MISSING_PHASE7_CMDLINE_MARKERS_START", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "MISSING_PHASE7_CMDLINE_MARKERS_END", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "MISMATCHED_PHASE7_CMDLINE_COUNTS_START", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "MISMATCHED_PHASE7_CMDLINE_COUNTS_END", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "\\\"Documentation/zigux/phase7-cmdline-slice.md\\\",", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "\\\"lib/cmdline.zig\\\",", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", "\\\"zigux/tests/phase7_cmdline_survey_build.zig\\\",", ""),
            ("zigux/tests/phase7_cmdline.zig", "test \"phase 7 cmdline companion replays leading-plus fallback boundaries\" {", ""),
            ("lib/cmdline.zig", "test \"memparse saturates signed overflow instead of trapping\" {", ""),
            ("zigux/tests/phase7_cmdline_survey_build.zig", "phase7-cmdline-survey", ""),
            ("scripts/zigux/check-phase7-cmdline-packet.py", 'EXPECTED_MANIFEST_LANE_KEY = \\\"P7-L08\\\"', 'EXPECTED_MANIFEST_LANE_KEY = \\\"P7-L07\\\"'),
            ("scripts/zigux/check-phase7-cmdline-packet.py", 'EXPECTED_MANIFEST_PHASE = \\\"Phase 7\\\"', 'EXPECTED_MANIFEST_PHASE = \\\"Phase 8\\\"'),
            ("scripts/zigux/check-phase7-cmdline-packet.py", 'EXPECTED_MANIFEST_ANCHOR = \\\"lib/cmdline.c\\\"', 'EXPECTED_MANIFEST_ANCHOR = \\\"lib/string_helpers.c\\\"'),
            ("scripts/zigux/check-phase7-cmdline-packet.py", 'EXPECTED_MANIFEST_STATE = \\\"helper_slice_test_survey_manifest_checker_anchor\\\"', 'EXPECTED_MANIFEST_STATE = \\\"helper_slice_test_survey_manifest_anchor\\\"'),
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

        manifest = json.loads(read_text(manifest_path))
        manifest["review_surfaces"].remove("scripts/zigux/check-phase7-cmdline-packet.py")
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_checker_path_guard",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: review_surfaces: scripts/zigux/check-phase7-cmdline-packet.py",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["review_surfaces"].remove("zigux/tests/phase7_cmdline_survey_build.zig")
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_survey_build_path_guard",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: review_surfaces: zigux/tests/phase7_cmdline_survey_build.zig",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["review_surfaces"].remove("samples/zigux/README.md")
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_samples_readme_guard",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: review_surfaces: samples/zigux/README.md",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["review_surfaces"] = "scripts/zigux/check-phase7-cmdline-packet.py"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_review_surfaces_type_guard",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: review_surfaces",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["ownership_focus"].remove(
            "parseOptionStr() stays bounded to exact comma-delimited bare options inside the exported C-string prefix"
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_parse_option_ownership_guard",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: ownership_focus: parseOptionStr() stays bounded to exact comma-delimited bare options inside the exported C-string prefix",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["covered_helpers"] = "parseOptionStr"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_covered_helpers_type_guard",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: covered_helpers",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["ownership_focus"] = "parseOptionStr() stays bounded to exact comma-delimited bare options inside the exported C-string prefix"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_ownership_focus_type_guard",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: ownership_focus",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["ownership_focus"].remove(
            "getOption() and getOptions() keep caller-provided state explicit while preserving Linux-style malformed-input, range, and wraparound behavior"
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_get_options_ownership_guard",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: ownership_focus: getOption() and getOptions() keep caller-provided state explicit while preserving Linux-style malformed-input, range, and wraparound behavior",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["ownership_focus"].remove(
            "nextArg() and next_arg() keep parameter, optional value, and remaining text borrowed from the caller slice without widening beyond the exported C-string boundary"
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_next_arg_ownership_guard",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: ownership_focus: nextArg() and next_arg() keep parameter, optional value, and remaining text borrowed from the caller slice without widening beyond the exported C-string boundary",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["ownership_focus"].remove(
            "the dedicated `get_option` alias replay keeps leading-plus and range-style cursor movement explicit beside the primary `getOption()` entry point"
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_get_option_alias_replay_guard",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: ownership_focus: the dedicated `get_option` alias replay keeps leading-plus and range-style cursor movement explicit beside the primary `getOption()` entry point",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["ownership_focus"].remove(
            "nextArg() also keeps `rest` and `remaining` as the same borrowed suffix view, including quoted-empty-value paths, so post-token cursor handling stays on one ownership track"
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_suffix_cursor_ownership_guard",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: ownership_focus: nextArg() also keeps `rest` and `remaining` as the same borrowed suffix view, including quoted-empty-value paths, so post-token cursor handling stays on one ownership track",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["ownership_focus"].remove(
            "memparse() keeps no-conversion, suffix handling, and signed-clamp posture reviewable without widening into separate allocator-backed helper ownership"
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_memparse_ownership_guard",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: ownership_focus: memparse() keeps no-conversion, suffix handling, and signed-clamp posture reviewable without widening into separate allocator-backed helper ownership",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["ownership_focus"].remove(
            "the dedicated `zig build phase7-cmdline-survey --build-file zigux/tests/phase7_cmdline_survey_build.zig` route keeps this helper-local survey replay runnable without widening into shared Phase 7 tests-root ownership"
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_survey_build_route_guard",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: ownership_focus: the dedicated `zig build phase7-cmdline-survey --build-file zigux/tests/phase7_cmdline_survey_build.zig` route keeps this helper-local survey replay runnable without widening into shared Phase 7 tests-root ownership",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["ownership_focus"].remove(
            "the no-standalone-cmdline sample boundary stays explicit only while `samples/zigux/README.md` keeps `*cmdline*` listed among the no-extra-sample reminders"
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_no_sample_boundary_guard",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: ownership_focus: the no-standalone-cmdline sample boundary stays explicit only while `samples/zigux/README.md` keeps `*cmdline*` listed among the no-extra-sample reminders",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["missing_paths"] = ["samples/zigux/cmdline_example.zig"]
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_missing_paths_must_stay_empty",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: missing_paths",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["next_bounded_step"] = (
            "Keep same-lane follow-through limited to the returned helper-local survey-manifest-checker "
            "truthfulness packet or one bounded parsing replay proof while sample-root routes stay parked "
            "outside this helper-local lane."
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_next_bounded_step_truthfulness_guard",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: next_bounded_step",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["covered_helpers"].remove("parseOptionStr")
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_covered_helper_guard",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: covered_helpers: parseOptionStr",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["covered_helpers"].remove("memparse")
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_memparse_helper_guard",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json: covered_helpers: memparse",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["lane_key"] = "P7-L07"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker("manifest_lane_key_guard", tmp_root, "zigux/tests/phase7_cmdline_manifest.json: lane_key")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["phase"] = "Phase 8"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker("manifest_phase_guard", tmp_root, "zigux/tests/phase7_cmdline_manifest.json: phase")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["anchor"] = "lib/string_helpers.c"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker("manifest_anchor_guard", tmp_root, "zigux/tests/phase7_cmdline_manifest.json: anchor")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["current_master_state"] = "helper_slice_test_survey_manifest_anchor"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker("manifest_state_guard", tmp_root, "zigux/tests/phase7_cmdline_manifest.json: current_master_state")
        cases_run += 1
        write_fixture_root(tmp_root)

        samples_path = tmp_root / "samples/zigux/README.md"
        samples_path.write_text(read_text(samples_path) + "* `*cmdline*`\n", encoding="utf-8")
        expect_mismatched_count(
            "duplicate_samples_cmdline_boundary",
            tmp_root,
            "samples/zigux/README.md: expected 1 occurrence(s) of '* `*cmdline*`', found 2",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

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

    missing_files, missing_markers, mismatched_counts = validate(args.repo_root)
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

    if mismatched_counts:
        print("PHASE7_CMDLINE_PACKET=fail")
        print("MISMATCHED_PHASE7_CMDLINE_COUNTS_START")
        for item in mismatched_counts:
            print(item)
        print("MISMATCHED_PHASE7_CMDLINE_COUNTS_END")
        return 1

    print("PHASE7_CMDLINE_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
