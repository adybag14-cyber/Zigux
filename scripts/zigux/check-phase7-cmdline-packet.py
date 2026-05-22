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
        "  - `Documentation/zigux/phase7-cmdline-slice.md`",
        "  - `samples/zigux/README.md`",
        "Fresh helper-local reread for this slot confirmed the dedicated cmdline slice, companion replay, survey, manifest, checker, and no-sample boundary now directly materialize on current `master`",
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
        '"Documentation/zigux/phase7-cmdline-slice.md",',
        "FORBIDDEN_MARKERS = {",
        "MISSING_PHASE7_CMDLINE_FILES_START",
        "MISSING_PHASE7_CMDLINE_FILES_END",
        "MISSING_PHASE7_CMDLINE_MARKERS_START",
        "MISSING_PHASE7_CMDLINE_MARKERS_END",
        "FORBIDDEN_PHASE7_CMDLINE_MARKERS_START",
        "FORBIDDEN_PHASE7_CMDLINE_MARKERS_END",
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
        'test "nextArg keeps the Linux-style empty sentinel token for leading whitespace" {',
        'test "nextArg keeps whitespace-only input as an empty sentinel before the first NUL" {',
        'test "nextArg keeps leading equals tokens as bare parameters" {',
        'test "nextArg keeps quoted leading equals tokens as bare parameters" {',
        'test "nextArg parses bare parameters and keeps the remaining text" {',
        'test "nextArg parses key value pairs and quoted values" {',
        'test "nextArg keeps quoted bare tokens together and preserves the following remainder" {',
        'test "nextArg keeps quoted empty values explicit without swallowing the next token" {',
        'test "nextArg keeps unterminated quoted values inside the current token" {',
        'test "nextArg keeps parameter and value slices borrowed from caller storage" {',
        'test "nextArg keeps rest and remaining as the same borrowed suffix view" {',
        'test "getOption preserves incomplete hex-prefix and descending-range behavior" {',
        'test "getOptions expands negative ranges and negative upper bounds" {',
        'test "parseOptionStr matches only exact bare options" {',
        'test "memparse saturates signed overflow instead of trapping" {',
    ],
    "zigux/tests/phase7_cmdline.zig": [
        'const cmdline = @import("cmdline");',
        'test "phase 7 cmdline companion replays exact bare-option matching boundaries" {',
        'try std.testing.expect(!cmdline.parseOptionStr("quiet,debug=1,nohlt", "debug"));',
        'try std.testing.expect(!cmdline.parseOptionStr("quiet,debug\\x00,nohlt", "nohlt"));',
        'try std.testing.expect(cmdline.parseOptionStr("debug,,quiet", ""));',
        'try std.testing.expect(!cmdline.parseOptionStr("debug,", ""));',
        'test "phase 7 cmdline companion replays option decoding, ranges, and malformed-input posture" {',
        'test "phase 7 cmdline companion replays incomplete-hex and descending-range boundaries" {',
        'try std.testing.expectEqualStrings("2,9", descending_rest);',
        'test "phase 7 cmdline companion replays negative range expansion and negative upper-bound posture" {',
        'test "phase 7 cmdline companion replays validator-only getOption cursor movement" {',
        'test "phase 7 cmdline companion replays quoted argument splitting and memparse boundaries" {',
        'test "phase 7 cmdline companion replays memparse signed clamp saturation" {',
        'test "phase 7 cmdline companion replays leading-whitespace sentinels and quoted full-token boundaries" {',
        'test "phase 7 cmdline companion replays whitespace-only sentinel termination" {',
        'test "phase 7 cmdline companion replays bare leading-equals ownership" {',
        'test "nextArg keeps empty input borrowed from the caller slice" {',
        'test "nextArg stays inside the first NUL for bare and key value tokens" {',
        'test "nextArg keeps rest and remaining as the same borrowed suffix view" {',
        'test "phase 7 cmdline companion replays bare quoted-empty-token ownership" {',
        'test "phase 7 cmdline companion replays quoted bare-token grouping without fabricating a value" {',
        'test "phase 7 cmdline companion replays quoted leading-equals and unterminated-value boundaries" {',
        'test "phase 7 cmdline companion replays quoted-value borrowed slice ownership" {',
    ],
    "zigux/tests/phase7_cmdline_manifest.json": [
        '"anchor": "lib/cmdline.c"',
        '"current_master_state": "helper_slice_test_survey_manifest_anchor"',
        '"scripts/zigux/check-phase7-cmdline-packet.py"',
        "helper-local survey-manifest-checker truthfulness packet",
        "nextArg() and next_arg() keep parameter, optional value, and remaining text borrowed from the caller slice without widening beyond the exported C-string boundary",
        "memparse() keeps no-conversion, suffix handling, and signed-clamp posture reviewable without widening into separate allocator-backed helper ownership",
        "while shared-control routes stay parked outside this helper-local lane.",
    ],
    "zigux/tests/phase7_cmdline_survey.zig": [
        'test "phase 7 cmdline survey keeps the returned helper-local packet truthful" {',
        'try std.testing.expectEqualStrings("helper_slice_test_survey_manifest_anchor", manifest.current_master_state);',
        'const checker = try readRepoFile(allocator, checker_path);',
        'try expectContains(helper, "test \\\"nextArg keeps the Linux-style empty sentinel token for leading whitespace\\\" {");',
        'try expectContains(helper, "test \\\"nextArg keeps whitespace-only input as an empty sentinel before the first NUL\\\" {");',
        'try expectContains(helper, "test \\\"nextArg keeps leading equals tokens as bare parameters\\\" {");',
        'try expectContains(helper, "test \\\"nextArg keeps quoted leading equals tokens as bare parameters\\\" {");',
        'try expectContains(helper, "test \\\"nextArg parses bare parameters and keeps the remaining text\\\" {");',
        'try expectContains(helper, "test \\\"nextArg parses key value pairs and quoted values\\\" {");',
        'try expectContains(helper, "test \\\"nextArg keeps quoted bare tokens together and preserves the following remainder\\\" {");',
        'try expectContains(helper, "test \\\"nextArg keeps quoted empty values explicit without swallowing the next token\\\" {");',
        'try expectContains(helper, "test \\\"nextArg keeps unterminated quoted values inside the current token\\\" {");',
        'try expectContains(helper, "test \\\"nextArg keeps parameter and value slices borrowed from caller storage\\\" {");',
        'try expectContains(helper, "test \\\"nextArg keeps rest and remaining as the same borrowed suffix view\\\" {");',
        'try expectContains(helper, "test \\\"memparse saturates signed overflow instead of trapping\\\" {");',
        'try expectContains(helper_companion, "phase 7 cmdline companion replays bare leading-equals ownership");',
        'try expectContains(helper_companion, "phase 7 cmdline companion replays whitespace-only sentinel termination");',
        'try expectContains(helper_companion, "try std.testing.expect(!cmdline.parseOptionStr(\\\\\"quiet,debug\\\\\\x00,nohlt\\\\\", \\\\\"nohlt\\\\\"));");',
        'try expectContains(helper_companion, "phase 7 cmdline companion replays memparse signed clamp saturation");',
    ],
    "samples/zigux/README.md": [
        "Current `master` still ships no standalone Phase 5 sample-root files here for:",
        "* `*cmdline*`",
    ],
}

FORBIDDEN_MARKERS = {
    "Documentation/zigux/phase7-cmdline-slice.md": [
        "phase7_cmdline_next_arg_vectors",
    ],
    "zigux/tests/phase7_cmdline_manifest.json": [
        "phase7_cmdline_next_arg_vectors",
    ],
}

SELF_TEST_CASE_COUNT = 75


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_root(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES:
        write(tmp_root / rel, "\n".join(REQUIRED_MARKERS[rel]) + "\n")


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


def collect_forbidden_markers(root: Path) -> list[str]:
    forbidden: list[str] = []
    for rel, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root / rel)
        for marker in markers:
            if marker in text:
                forbidden.append(f"{rel}: {marker}")
    return forbidden


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []
    return missing_files, collect_missing_markers(root), collect_forbidden_markers(root)


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers, forbidden_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert forbidden_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers, forbidden_markers = validate(tmp_root)
    assert missing_files == [], case
    assert forbidden_markers == [], case
    assert missing_markers == [marker], case


def expect_forbidden_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers, forbidden_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [], case
    assert forbidden_markers == [marker], case


def remove_once(path: Path, marker: str) -> None:
    text = read_text(path)
    if marker + "\n" in text:
        text = text.replace(marker + "\n", "", 1)
    else:
        text = text.replace(marker, "", 1)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [], [])
        cases_run = 0

        companion_path = tmp_root / "zigux" / "tests" / "phase7_cmdline.zig"
        companion_path.unlink()
        expect_missing_file("missing_cmdline_companion", tmp_root, "zigux/tests/phase7_cmdline.zig")
        cases_run += 1
        write_fixture_root(tmp_root)

        sequencing_path = tmp_root / "Documentation" / "zigux" / "phase7-helper-lane-sequencing.md"
        sequencing_marker = "  - `Documentation/zigux/phase7-cmdline-slice.md`"
        remove_once(sequencing_path, sequencing_marker)
        expect_missing_marker(
            "missing_sequencing_slice_marker",
            tmp_root,
            f"Documentation/zigux/phase7-helper-lane-sequencing.md: {sequencing_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        sequencing_marker = "  - `samples/zigux/README.md`"
        remove_once(sequencing_path, sequencing_marker)
        expect_missing_marker(
            "missing_sequencing_samples_boundary_marker",
            tmp_root,
            f"Documentation/zigux/phase7-helper-lane-sequencing.md: {sequencing_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        slice_path = tmp_root / "Documentation" / "zigux" / "phase7-cmdline-slice.md"
        slice_marker = "Keep same-lane follow-through limited to the returned helper-local survey-manifest-checker truthfulness packet or one bounded parsing replay proof."
        remove_once(slice_path, slice_marker)
        expect_missing_marker(
            "missing_slice_next_step_marker",
            tmp_root,
            f"Documentation/zigux/phase7-cmdline-slice.md: {slice_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        forbidden_fixture_marker = "phase7_cmdline_next_arg_vectors"
        slice_path.write_text(read_text(slice_path) + forbidden_fixture_marker + "\n", encoding="utf-8")
        expect_forbidden_marker(
            "stale_slice_fixture_marker",
            tmp_root,
            f"Documentation/zigux/phase7-cmdline-slice.md: {forbidden_fixture_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_path = tmp_root / "scripts" / "zigux" / "check-phase7-cmdline-packet.py"
        checker_marker = "--self-test"
        remove_once(checker_path, checker_marker)
        expect_missing_marker(
            "missing_checker_selftest_flag_marker",
            tmp_root,
            f"scripts/zigux/check-phase7-cmdline-packet.py: {checker_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_marker = "PHASE7_CMDLINE_PACKET_SELF_TEST=pass"
        remove_once(checker_path, checker_marker)
        expect_missing_marker(
            "missing_checker_selftest_pass_marker",
            tmp_root,
            f"scripts/zigux/check-phase7-cmdline-packet.py: {checker_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_marker = '"Documentation/zigux/phase7-cmdline-slice.md",'
        remove_once(checker_path, checker_marker)
        expect_missing_marker(
            "missing_checker_slice_anchor_marker",
            tmp_root,
            f"scripts/zigux/check-phase7-cmdline-packet.py: {checker_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        for checker_marker in [
            "MISSING_PHASE7_CMDLINE_FILES_START",
            "MISSING_PHASE7_CMDLINE_FILES_END",
            "MISSING_PHASE7_CMDLINE_MARKERS_START",
            "MISSING_PHASE7_CMDLINE_MARKERS_END",
            "FORBIDDEN_PHASE7_CMDLINE_MARKERS_START",
            "FORBIDDEN_PHASE7_CMDLINE_MARKERS_END",
        ]:
            remove_once(checker_path, checker_marker)
            expect_missing_marker(
                f"missing_checker_output_marker_{checker_marker.lower()}",
                tmp_root,
                f"scripts/zigux/check-phase7-cmdline-packet.py: {checker_marker}",
            )
            cases_run += 1
            write_fixture_root(tmp_root)

        helper_path = tmp_root / "lib" / "cmdline.zig"
        helper_markers = [
            ("missing_helper_nextarg_marker", "pub fn nextArg"),
            ("missing_helper_nextarg_alias_marker", "pub const next_arg = nextArg;"),
            (
                "missing_helper_linux_whitespace_sentinel_marker",
                'test "nextArg keeps the Linux-style empty sentinel token for leading whitespace" {',
            ),
            (
                "missing_helper_whitespace_only_sentinel_marker",
                'test "nextArg keeps whitespace-only input as an empty sentinel before the first NUL" {',
            ),
            ("missing_helper_bare_leading_equals_marker", 'test "nextArg keeps leading equals tokens as bare parameters" {'),
            (
                "missing_helper_quoted_leading_equals_marker",
                'test "nextArg keeps quoted leading equals tokens as bare parameters" {',
            ),
            (
                "missing_helper_bare_parameter_remainder_marker",
                'test "nextArg parses bare parameters and keeps the remaining text" {',
            ),
            (
                "missing_helper_key_value_quotes_marker",
                'test "nextArg parses key value pairs and quoted values" {',
            ),
            (
                "missing_helper_quoted_bare_token_marker",
                'test "nextArg keeps quoted bare tokens together and preserves the following remainder" {',
            ),
            (
                "missing_helper_quoted_empty_value_marker",
                'test "nextArg keeps quoted empty values explicit without swallowing the next token" {',
            ),
            (
                "missing_helper_unterminated_quoted_value_marker",
                'test "nextArg keeps unterminated quoted values inside the current token" {',
            ),
            (
                "missing_helper_borrowed_storage_marker",
                'test "nextArg keeps parameter and value slices borrowed from caller storage" {',
            ),
            (
                "missing_helper_borrowed_suffix_marker",
                'test "nextArg keeps rest and remaining as the same borrowed suffix view" {',
            ),
            (
                "missing_helper_incomplete_hex_descending_marker",
                'test "getOption preserves incomplete hex-prefix and descending-range behavior" {',
            ),
            (
                "missing_helper_negative_range_marker",
                'test "getOptions expands negative ranges and negative upper bounds" {',
            ),
            (
                "missing_helper_exact_bare_option_marker",
                'test "parseOptionStr matches only exact bare options" {',
            ),
            (
                "missing_helper_memparse_signed_clamp_marker",
                'test "memparse saturates signed overflow instead of trapping" {',
            ),
        ]
        for case, marker in helper_markers:
            remove_once(helper_path, marker)
            expect_missing_marker(case, tmp_root, f"lib/cmdline.zig: {marker}")
            cases_run += 1
            write_fixture_root(tmp_root)

        manifest_path = tmp_root / "zigux" / "tests" / "phase7_cmdline_manifest.json"
        manifest_markers = [
            ("missing_manifest_checker_marker", '"scripts/zigux/check-phase7-cmdline-packet.py"'),
            (
                "missing_manifest_nextarg_ownership_marker",
                "nextArg() and next_arg() keep parameter, optional value, and remaining text borrowed from the caller slice without widening beyond the exported C-string boundary",
            ),
            (
                "missing_manifest_memparse_ownership_marker",
                "memparse() keeps no-conversion, suffix handling, and signed-clamp posture reviewable without widening into separate allocator-backed helper ownership",
            ),
            (
                "missing_manifest_shared_control_boundary_marker",
                "while shared-control routes stay parked outside this helper-local lane.",
            ),
        ]
        for case, marker in manifest_markers:
            remove_once(manifest_path, marker)
            expect_missing_marker(case, tmp_root, f"zigux/tests/phase7_cmdline_manifest.json: {marker}")
            cases_run += 1
            write_fixture_root(tmp_root)

        manifest_forbidden_marker = "phase7_cmdline_next_arg_vectors"
        manifest_path.write_text(read_text(manifest_path) + manifest_forbidden_marker + "\n", encoding="utf-8")
        expect_forbidden_marker(
            "stale_manifest_fixture_marker",
            tmp_root,
            f"zigux/tests/phase7_cmdline_manifest.json: {manifest_forbidden_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_path = tmp_root / "zigux" / "tests" / "phase7_cmdline_survey.zig"
        survey_markers = [
            ("missing_survey_checker_reader", 'const checker = try readRepoFile(allocator, checker_path);'),
            (
                "missing_survey_helper_linux_whitespace_marker",
                'try expectContains(helper, "test \\\"nextArg keeps the Linux-style empty sentinel token for leading whitespace\\\" {");',
            ),
            (
                "missing_survey_helper_whitespace_only_marker",
                'try expectContains(helper, "test \\\"nextArg keeps whitespace-only input as an empty sentinel before the first NUL\\\" {");',
            ),
            (
                "missing_survey_helper_leading_equals_marker",
                'try expectContains(helper, "test \\\"nextArg keeps leading equals tokens as bare parameters\\\" {");',
            ),
            (
                "missing_survey_helper_quoted_leading_equals_marker",
                'try expectContains(helper, "test \\\"nextArg keeps quoted leading equals tokens as bare parameters\\\" {");',
            ),
            (
                "missing_survey_helper_bare_parameter_remainder_marker",
                'try expectContains(helper, "test \\\"nextArg parses bare parameters and keeps the remaining text\\\" {");',
            ),
            (
                "missing_survey_helper_key_value_quotes_marker",
                'try expectContains(helper, "test \\\"nextArg parses key value pairs and quoted values\\\" {");',
            ),
            (
                "missing_survey_helper_quoted_bare_token_marker",
                'try expectContains(helper, "test \\\"nextArg keeps quoted bare tokens together and preserves the following remainder\\\" {");',
            ),
            (
                "missing_survey_helper_quoted_empty_value_marker",
                'try expectContains(helper, "test \\\"nextArg keeps quoted empty values explicit without swallowing the next token\\\" {");',
            ),
            (
                "missing_survey_helper_unterminated_quoted_value_marker",
                'try expectContains(helper, "test \\\"nextArg keeps unterminated quoted values inside the current token\\\" {");',
            ),
            (
                "missing_survey_helper_borrowed_storage_marker",
                'try expectContains(helper, "test \\\"nextArg keeps parameter and value slices borrowed from caller storage\\\" {");',
            ),
            (
                "missing_survey_helper_borrowed_suffix_marker",
                'try expectContains(helper, "test \\\"nextArg keeps rest and remaining as the same borrowed suffix view\\\" {");',
            ),
            (
                "missing_survey_helper_memparse_signed_clamp_marker",
                'try expectContains(helper, "test \\\"memparse saturates signed overflow instead of trapping\\\" {");',
            ),
            (
                "missing_survey_companion_leading_equals_marker",
                'try expectContains(helper_companion, "phase 7 cmdline companion replays bare leading-equals ownership");',
            ),
            (
                "missing_survey_companion_whitespace_only_marker",
                'try expectContains(helper_companion, "phase 7 cmdline companion replays whitespace-only sentinel termination");',
            ),
            (
                "missing_survey_companion_first_nul_bare_option_marker",
                'try expectContains(helper_companion, "try std.testing.expect(!cmdline.parseOptionStr(\\\\\"quiet,debug\\\\\\x00,nohlt\\\\\", \\\\\"nohlt\\\\\"));");',
            ),
            (
                "missing_survey_companion_memparse_signed_clamp_marker",
                'try expectContains(helper_companion, "phase 7 cmdline companion replays memparse signed clamp saturation");',
            ),
        ]
        for case, marker in survey_markers:
            remove_once(survey_path, marker)
            expect_missing_marker(case, tmp_root, f"zigux/tests/phase7_cmdline_survey.zig: {marker}")
            cases_run += 1
            write_fixture_root(tmp_root)

        companion_markers = [
            ("missing_companion_exact_bare_option_marker", 'test "phase 7 cmdline companion replays exact bare-option matching boundaries" {'),
            (
                "missing_companion_non_bare_option_guard_marker",
                'try std.testing.expect(!cmdline.parseOptionStr("quiet,debug=1,nohlt", "debug"));',
            ),
            (
                "missing_companion_empty_entry_option_marker",
                'try std.testing.expect(cmdline.parseOptionStr("debug,,quiet", ""));',
            ),
            (
                "missing_companion_trailing_empty_option_guard_marker",
                'try std.testing.expect(!cmdline.parseOptionStr("debug,", ""));',
            ),
            (
                "missing_companion_option_decoding_marker",
                'test "phase 7 cmdline companion replays option decoding, ranges, and malformed-input posture" {',
            ),
            (
                "missing_companion_incomplete_hex_descending_marker",
                'test "phase 7 cmdline companion replays incomplete-hex and descending-range boundaries" {',
            ),
            (
                "missing_companion_descending_range_rest_marker",
                'try std.testing.expectEqualStrings("2,9", descending_rest);',
            ),
            (
                "missing_companion_validator_only_cursor_marker",
                'test "phase 7 cmdline companion replays validator-only getOption cursor movement" {',
            ),
            (
                "missing_companion_negative_range_marker",
                'test "phase 7 cmdline companion replays negative range expansion and negative upper-bound posture" {',
            ),
            (
                "missing_companion_quoted_argument_memparse_marker",
                'test "phase 7 cmdline companion replays quoted argument splitting and memparse boundaries" {',
            ),
            (
                "missing_companion_memparse_signed_clamp_marker",
                'test "phase 7 cmdline companion replays memparse signed clamp saturation" {',
            ),
            (
                "missing_companion_leading_whitespace_boundary_marker",
                'test "phase 7 cmdline companion replays leading-whitespace sentinels and quoted full-token boundaries" {',
            ),
            (
                "missing_companion_whitespace_only_boundary_marker",
                'test "phase 7 cmdline companion replays whitespace-only sentinel termination" {',
            ),
            (
                "missing_companion_bare_leading_equals_marker",
                'test "phase 7 cmdline companion replays bare leading-equals ownership" {',
            ),
            (
                "missing_companion_empty_input_borrow_marker",
                'test "nextArg keeps empty input borrowed from the caller slice" {',
            ),
            (
                "missing_companion_first_nul_boundary_marker",
                'test "nextArg stays inside the first NUL for bare and key value tokens" {',
            ),
            (
                "missing_companion_borrowed_suffix_marker",
                'test "nextArg keeps rest and remaining as the same borrowed suffix view" {',
            ),
            (
                "missing_companion_quoted_empty_token_marker",
                'test "phase 7 cmdline companion replays bare quoted-empty-token ownership" {',
            ),
            (
                "missing_companion_quoted_bare_grouping_marker",
                'test "phase 7 cmdline companion replays quoted bare-token grouping without fabricating a value" {',
            ),
            (
                "missing_companion_quoted_equals_and_unterminated_marker",
                'test "phase 7 cmdline companion replays quoted leading-equals and unterminated-value boundaries" {',
            ),
            (
                "missing_companion_quoted_value_borrow_marker",
                'test "phase 7 cmdline companion replays quoted-value borrowed slice ownership" {',
            ),
        ]
        for case, marker in companion_markers:
            remove_once(companion_path, marker)
            expect_missing_marker(case, tmp_root, f"zigux/tests/phase7_cmdline.zig: {marker}")
            cases_run += 1
            write_fixture_root(tmp_root)

        samples_path = tmp_root / "samples" / "zigux" / "README.md"
        samples_marker = "* `*cmdline*`"
        remove_once(samples_path, samples_marker)
        expect_missing_marker(
            "missing_samples_cmdline_boundary",
            tmp_root,
            f"samples/zigux/README.md: {samples_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        assert cases_run == SELF_TEST_CASE_COUNT, cases_run

    print("PHASE7_CMDLINE_PACKET_SELF_TEST=pass")
    print(f"PHASE7_CMDLINE_PACKET_SELF_TEST_CASE_COUNT={cases_run}")


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

    missing_files, missing_markers, forbidden_markers = validate(args.repo_root)
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

    if forbidden_markers:
        print("PHASE7_CMDLINE_PACKET=fail")
        print("FORBIDDEN_PHASE7_CMDLINE_MARKERS_START")
        for item in forbidden_markers:
            print(item)
        print("FORBIDDEN_PHASE7_CMDLINE_MARKERS_END")
        return 1

    print("PHASE7_CMDLINE_PACKET=pass")
    print(f"PHASE7_CMDLINE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE7_CMDLINE_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print(
        "PHASE7_CMDLINE_PACKET_FORBIDDEN_MARKER_COUNT="
        f"{sum(len(markers) for markers in FORBIDDEN_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())