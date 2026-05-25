#!/usr/bin/env python3
"""Validate the current Phase 7 string-helpers helper-local packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

EXPECTED_MANIFEST_LANE_KEY = "helper-local"
EXPECTED_MANIFEST_PHASE = "Phase 7"
EXPECTED_MANIFEST_ANCHOR = "lib/string_helpers.c"
EXPECTED_MANIFEST_STATE = "expanded_starter_packet"

REQUIRED_FILES = [
    "Documentation/zigux/phase7-string-helpers-slice.md",
    "scripts/zigux/check-phase7-string-helpers-packet.py",
    "lib/string_helpers.zig",
    "zigux/tests/phase7_string_helpers.zig",
    "zigux/tests/phase7_string_helpers_manifest.json",
    "zigux/tests/phase7_string_helpers_survey.zig",
    "zigux/tests/phase7_string_helpers_sample_boundary.zig",
    "samples/zigux/README.md",
]

DEVM_FOLLOW_ON_MARKER = (
    "Keep the dedicated checker, survey, and sample-boundary replays fail-closed "
    "on the still-parked `parse_int_array_user()` and `devm_kasprintf_strarray()` follow-ons"
)

NEXT_BOUNDED_STEP_MARKER = (
    "Keep the dedicated checkers, survey, sample-boundary, and format-boundary replays fail-closed "
    "on the still-parked `parse_int_array_user()` and `devm_kasprintf_strarray()` follow-ons"
)

FULL_FAMILY_GAP_MARKER = (
    "the broader full-family packet that still leaves `parse_int_array_user()` and "
    "`devm_kasprintf_strarray()` outside the current `master` helper packet"
)

NO_EXTRA_SAMPLE_BULLETS = [
    "* `*string*`",
    "* `*cmdline*`",
    "* `*argv*`",
    "* `*rbtree*`",
    "* `*kasprintf*`",
    "* `*strarray*`",
    "* `*printf*`",
    "* `*vsprintf*`",
]

NO_EXTRA_SAMPLE_EXCLUSIONS_MARKER = (
    "the shared no-sample boundary stays reviewable only while `samples/zigux/README.md` keeps "
    "the explicit `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*kasprintf*`, and `*strarray*` exclusions aligned"
)

FORMAT_BOUNDARY_MARKER = (
    "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here."
)

CMDLINE_OWNERSHIP_MARKER = (
    "kstrdupQuotableCmdline() keeps returned storage caller-owned, leaves the caller source buffer untouched, "
    "collapses trailing and inter-argument NULL separators only inside duplicated command-line storage, and only "
    "then applies quotable escaping"
)

TERMINATION_OWNERSHIP_MARKER = (
    "stringIsTerminated() and string_is_terminated() keep caller-provided bounds explicit and only scan inside the requested prefix"
)

MANIFEST_LANE_KEY_MARKER = '"lane_key": "helper-local"'
MANIFEST_PHASE_MARKER = '"phase": "Phase 7"'
MANIFEST_ANCHOR_MARKER = '"anchor": "lib/string_helpers.c"'
MANIFEST_STATE_MARKER = '"current_master_state": "expanded_starter_packet"'

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-string-helpers-slice.md": [
        "`PHASE7_STATUS=starter_landed`",
        "`scripts/zigux/check-phase7-string-helpers-packet.py`",
        "quoted file-path duplication that keeps an explicit `<unknown>` fallback for missing inputs while still escaping special characters through the same quotable path",
        "`stringUpper()`, `string_upper()`, `stringLower()`, and `string_lower()` keep case-conversion writes inside caller-provided destination storage and stop at the exported C-string boundary",
        "quoted cmdline duplication that collapses trailing NULs",
        NO_EXTRA_SAMPLE_EXCLUSIONS_MARKER,
        NEXT_BOUNDED_STEP_MARKER,
    ],
    "scripts/zigux/check-phase7-string-helpers-packet.py": [
        "--self-test",
        "PHASE7_STRING_HELPERS_PACKET_SELF_TEST=pass",
        'print("PHASE7_STRING_HELPERS_PACKET=pass")',
        'print("PHASE7_STRING_HELPERS_PACKET=fail")',
        '"zigux/tests/phase7_string_helpers_sample_boundary.zig",',
        '"lib/string_helpers.zig": [',
        '"pub fn devmKasprintfStrarray("',
        '"pub fn devm_kasprintf_strarray("',
        '"pub fn parseIntArrayUser("',
        '"pub fn parse_int_array_user("',
        '"zigux/tests/phase7_string_helpers_manifest.json": [',
        '"\\\\\\"devmKasprintfStrarray\\\\\\""',
        '"\\\\\\"devm_kasprintf_strarray\\\\\\""',
        '"\\\\\\"parseIntArrayUser\\\\\\""',
        '"\\\\\\"parse_int_array_user\\\\\\""',
        '"* `*printf*`"',
        '"* `*vsprintf*`"',
        FORMAT_BOUNDARY_MARKER,
        FULL_FAMILY_GAP_MARKER,
        DEVM_FOLLOW_ON_MARKER,
        NEXT_BOUNDED_STEP_MARKER,
        TERMINATION_OWNERSHIP_MARKER,
        MANIFEST_LANE_KEY_MARKER,
        MANIFEST_PHASE_MARKER,
        MANIFEST_ANCHOR_MARKER,
        MANIFEST_STATE_MARKER,
        "EXPECTED_MANIFEST_LANE_KEY = \"helper-local\"",
        "EXPECTED_MANIFEST_PHASE = \"Phase 7\"",
        "EXPECTED_MANIFEST_ANCHOR = \"lib/string_helpers.c\"",
        "EXPECTED_MANIFEST_STATE = \"expanded_starter_packet\"",
        "MISSING_PHASE7_STRING_HELPERS_FILES_START",
        "MISSING_PHASE7_STRING_HELPERS_FILES_END",
        "MISSING_PHASE7_STRING_HELPERS_MARKERS_START",
        "MISSING_PHASE7_STRING_HELPERS_MARKERS_END",
        "MISMATCHED_PHASE7_STRING_HELPERS_COUNTS_START",
        "MISMATCHED_PHASE7_STRING_HELPERS_COUNTS_END",
        "UNEXPECTED_PHASE7_STRING_HELPERS_MARKERS_START",
        "UNEXPECTED_PHASE7_STRING_HELPERS_MARKERS_END",
    ],
    "lib/string_helpers.zig": [
        "pub fn kasprintfStrarray(",
        "pub fn kstrdupQuotable(",
        "pub fn kstrdup_quotable(",
        "pub fn kstrdupQuotableFile(",
        "pub fn kstrdup_quotable_file(",
        "pub fn kstrdupQuotableCmdline(",
        "pub fn kstrdup_quotable_cmdline(",
        "pub fn parseIntArray(",
        "pub fn parse_int_array(",
        "pub fn stringIsTerminated(",
        "pub fn string_is_terminated(",
        "pub fn stringUpper(",
        "pub fn string_upper(",
        "pub fn stringLower(",
        "pub fn string_lower(",
    ],
    "zigux/tests/phase7_string_helpers.zig": [
        'test "phase 7 string helpers starter quotes special log-hazard bytes without widening beyond the exported c-string prefix" {',
        'test "phase 7 string helpers starter quotes already-materialized file paths and keeps the missing-file fallback explicit" {',
        'test "phase 7 string helpers starter quotes cmdlines after collapsing trailing NULs and replacing inter-argument separators" {',
        'test "phase 7 string helpers starter keeps termination checks bounded by the caller limit" {',
        'test "phase 7 string helpers starter reports empty parse-int-array input as no entry" {',
        'test "phase 7 string helpers starter reports parse-int-array allocation failure cleanly" {',
        'test "phase 7 string helpers starter frees partially built arrays when allocator failure interrupts setup" {',
        'test "phase 7 string helpers starter reports overflow before sizing the null-terminated string-array view" {',
        'test "phase 7 string helpers starter reuses the blank string-array sentinel when no names are requested" {',
        'test "phase 7 string helpers starter keeps sibling zero-count results on the shared sentinel after one owner deinitializes" {',
        'test "phase 7 string helpers starter keeps sibling string arrays intact when one owner frees its result" {',
        'test "phase 7 string helpers starter mirrors kfree_strarray teardown and stays idempotent" {',
        'test "phase 7 string helpers starter uppercases and lowercases only through the exported c-string boundary" {',
        'test "phase 7 string helpers starter reports kstrdupQuotable allocation failure cleanly" {',
        'test "phase 7 string helpers starter reports kstrdupQuotableFile allocation failure cleanly" {',
        'test "phase 7 string helpers starter reports kstrdupQuotableCmdline allocation failure cleanly" {',
        'test "phase 7 string helpers starter reports duplicate-and-replace allocation failure cleanly" {',
        'test "phase 7 string helpers starter pads bounded copies without reading past the provided source slice" {',
        'test "phase 7 string helpers starter replaces bytes only inside the exported c-string prefix" {',
    ],
    "zigux/tests/phase7_string_helpers_manifest.json": [
        '"scripts/zigux/check-phase7-string-helpers-packet.py"',
        "quoted file-path duplication with explicit missing-file fallback and quotable escaping for already-materialized path strings",
        "bounded uppercase and lowercase copies through the exported C-string boundary",
        "quoted cmdline duplication that collapses trailing NULL separators into spaces before escaping special characters",
        CMDLINE_OWNERSHIP_MARKER,
        TERMINATION_OWNERSHIP_MARKER,
        "dedicated helper-local checker-backed packet reviewability",
        NO_EXTRA_SAMPLE_EXCLUSIONS_MARKER,
        NEXT_BOUNDED_STEP_MARKER,
    ],
    "zigux/tests/phase7_string_helpers_survey.zig": [
        'const checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-string-helpers-packet.py");',
        'try expectContains(checker, "PHASE7_STRING_HELPERS_PACKET_SELF_TEST=pass");',
        'try expectContains(checker, "* `*printf*`");',
        'try expectContains(checker, "* `*vsprintf*`");',
        'try expectContains(sample_boundary, "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here.");',
        'try expectContains(manifest, "\\\\\\\"scripts/zigux/check-phase7-string-helpers-packet.py\\\\\\\"");',
        'try expectContains(manifest, "dedicated helper-local checker-backed packet reviewability");',
        'try expectContains(manifest, "kstrdupQuotableCmdline() keeps returned storage caller-owned, leaves the caller source buffer untouched, collapses trailing and inter-argument NULL separators only inside duplicated command-line storage, and only then applies quotable escaping");',
        'try expectContains(manifest, "\\\\\\\"next_bounded_step\\\\\\\": \\\\\\\"Keep the dedicated checkers, survey, sample-boundary, and format-boundary replays fail-closed on the still-parked `parse_int_array_user()` and `devm_kasprintf_strarray()` follow-ons\\\\\\\"");',
        'try expectContains(sample_boundary, "Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `parse_int_array_user()` and `devm_kasprintf_strarray()` follow-ons");',
        'try expectContains(checker, "EXPECTED_MANIFEST_LANE_KEY = \\"helper-local\\"");',
        'try expectContains(checker, "EXPECTED_MANIFEST_PHASE = \\"Phase 7\\"");',
        'try expectContains(checker, "EXPECTED_MANIFEST_ANCHOR = \\"lib/string_helpers.c\\"");',
        'try expectContains(checker, "EXPECTED_MANIFEST_STATE = \\"expanded_starter_packet\\"");',
        'try expectContains(checker, "try expectContains(helper, \\\\\\"pub fn stringIsTerminated(\\\\\\");");',
        'try expectContains(checker, "try expectContains(helper, \\\\\\"pub fn string_is_terminated(\\\\\\");");',
        'try expectContains(checker, "try expectContains(helper_tests, \\\\\\"test \\\\\\\\\\\\\\"phase 7 string helpers starter keeps termination checks bounded by the caller limit\\\\\\\\\\\\\\" {\\\\\\");");',
        'try expectContains(checker, "try expectContains(manifest, \\\\\\"stringIsTerminated() and string_is_terminated() keep caller-provided bounds explicit and only scan inside the requested prefix\\\\\\");");',
        'try expectNotContains(helper, "pub fn devmKasprintfStrarray");',
        'try expectNotContains(helper, "pub fn devm_kasprintf_strarray");',
        'try expectNotContains(helper, "pub fn parseIntArrayUser(");',
        'try expectNotContains(helper, "pub fn parse_int_array_user(");',
        'try expectNotContains(helper_tests, "devmKasprintfStrarray");',
        'try expectNotContains(helper_tests, "devm_kasprintf_strarray");',
        'try expectNotContains(helper_tests, "parseIntArrayUser");',
        'try expectNotContains(helper_tests, "parse_int_array_user");',
        'try expectNotContains(manifest, "\\\\\\\"devmKasprintfStrarray\\\\\\\"");',
        'try expectNotContains(manifest, "\\\\\\\"devm_kasprintf_strarray\\\\\\\"");',
        'try expectNotContains(manifest, "\\\\\\\"parseIntArrayUser\\\\\\\"");',
        'try expectNotContains(manifest, "\\\\\\\"parse_int_array_user\\\\\\\"");',
    ],
    "zigux/tests/phase7_string_helpers_sample_boundary.zig": [
        "phase 7 string helper boundary keeps the no-standalone-string-helper-sample policy lane-local",
        FULL_FAMILY_GAP_MARKER,
        DEVM_FOLLOW_ON_MARKER,
        FORMAT_BOUNDARY_MARKER,
        "* `*printf*`",
        "* `*vsprintf*`",
    ],
    "samples/zigux/README.md": [
        "Current `master` still ships no standalone Phase 5 sample-root files here for:",
        *NO_EXTRA_SAMPLE_BULLETS,
        FORMAT_BOUNDARY_MARKER,
    ],
}

COUNTED_MARKERS = {
    "Documentation/zigux/phase7-string-helpers-slice.md": [
        (NEXT_BOUNDED_STEP_MARKER, 1),
    ],
    "zigux/tests/phase7_string_helpers_manifest.json": [
        (
            NEXT_BOUNDED_STEP_MARKER,
            1,
        ),
    ],
    "zigux/tests/phase7_string_helpers_sample_boundary.zig": [
        (
            DEVM_FOLLOW_ON_MARKER,
            1,
        ),
        (FORMAT_BOUNDARY_MARKER, 1),
    ],
    "samples/zigux/README.md": [(marker, 1) for marker in NO_EXTRA_SAMPLE_BULLETS] + [(FORMAT_BOUNDARY_MARKER, 1)],
}

FORBIDDEN_MARKERS = {
    "lib/string_helpers.zig": [
        "pub fn devmKasprintfStrarray(",
        "pub fn devm_kasprintf_strarray(",
        "pub fn parseIntArrayUser(",
        "pub fn parse_int_array_user(",
    ],
    "zigux/tests/phase7_string_helpers.zig": [
        "devmKasprintfStrarray",
        "devm_kasprintf_strarray",
        "parseIntArrayUser",
        "parse_int_array_user",
    ],
    "zigux/tests/phase7_string_helpers_manifest.json": [
        '"devmKasprintfStrarray"',
        '"devm_kasprintf_strarray"',
        '"parseIntArrayUser"',
        '"parse_int_array_user"',
    ],
}

SELF_TEST_CASE_COUNT = 67


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_root(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES:
        if rel == "zigux/tests/phase7_string_helpers_manifest.json":
            continue
        lines = list(REQUIRED_MARKERS[rel])
        for marker, expected in COUNTED_MARKERS.get(rel, []):
            if marker not in lines:
                lines.extend([marker] * expected)
        write(tmp_root / rel, "\n".join(lines) + "\n")

    manifest = {
        "lane_key": EXPECTED_MANIFEST_LANE_KEY,
        "phase": EXPECTED_MANIFEST_PHASE,
        "verified_on_utc": "2026-05-25T16:43:22Z",
        "anchor": EXPECTED_MANIFEST_ANCHOR,
        "current_master_state": EXPECTED_MANIFEST_STATE,
        "review_surfaces": [
            "Documentation/zigux/phase7-string-helpers-slice.md",
            "scripts/zigux/check-phase7-string-helpers-packet.py",
            "lib/string_helpers.zig",
            "zigux/tests/phase7_string_helpers.zig",
            "zigux/tests/phase7_string_helpers_manifest.json",
            "zigux/tests/phase7_string_helpers_survey.zig",
            "zigux/tests/phase7_string_helpers_sample_boundary.zig",
            "samples/zigux/README.md",
        ],
        "ownership_focus": [
            "quoted file-path duplication with explicit missing-file fallback and quotable escaping for already-materialized path strings",
            "bounded uppercase and lowercase copies through the exported C-string boundary",
            "quoted cmdline duplication that collapses trailing NULL separators into spaces before escaping special characters",
            CMDLINE_OWNERSHIP_MARKER,
            TERMINATION_OWNERSHIP_MARKER,
            "dedicated helper-local checker-backed packet reviewability",
            NO_EXTRA_SAMPLE_EXCLUSIONS_MARKER,
        ],
        "next_bounded_step": NEXT_BOUNDED_STEP_MARKER,
    }
    write(
        tmp_root / "zigux/tests/phase7_string_helpers_manifest.json",
        json.dumps(manifest, indent=2) + "\n",
    )


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


def collect_unexpected_markers(root: Path) -> list[str]:
    unexpected: list[str] = []
    for rel, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root / rel)
        for marker in markers:
            if marker in text:
                unexpected.append(f"{rel}: {marker}")
    return unexpected


def validate(root: Path) -> tuple[list[str], list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], [], []

    manifest = json.loads(read_text(root / "zigux/tests/phase7_string_helpers_manifest.json"))
    if manifest.get("lane_key") != EXPECTED_MANIFEST_LANE_KEY:
        return [], ["zigux/tests/phase7_string_helpers_manifest.json: lane_key"], [], []
    if manifest.get("phase") != EXPECTED_MANIFEST_PHASE:
        return [], ["zigux/tests/phase7_string_helpers_manifest.json: phase"], [], []
    if manifest.get("anchor") != EXPECTED_MANIFEST_ANCHOR:
        return [], ["zigux/tests/phase7_string_helpers_manifest.json: anchor"], [], []
    if manifest.get("current_master_state") != EXPECTED_MANIFEST_STATE:
        return [], ["zigux/tests/phase7_string_helpers_manifest.json: current_master_state"], [], []

    return (
        missing_files,
        collect_missing_markers(root),
        collect_mismatched_counts(root),
        collect_unexpected_markers(root),
    )


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers, mismatched_counts, unexpected_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert mismatched_counts == [], case
    assert unexpected_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers, mismatched_counts, unexpected_markers = validate(tmp_root)
    assert missing_files == [], case
    assert unexpected_markers == [], case
    assert missing_markers == [marker], case


def expect_mismatched_count(case: str, tmp_root: Path, mismatch: str) -> None:
    missing_files, missing_markers, mismatched_counts, unexpected_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [], case
    assert unexpected_markers == [], case
    assert mismatched_counts == [mismatch], case


def expect_unexpected_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers, mismatched_counts, unexpected_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [], case
    assert mismatched_counts == [], case
    assert unexpected_markers == [marker], case


def remove_once(path: Path, marker: str) -> None:
    text = read_text(path)
    if marker + "\n" in text:
        text = text.replace(marker + "\n", "", 1)
    else:
        text = text.replace(marker, "", 1)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_string_helpers_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [], [], [])
        cases_run = 0

        checker_path = tmp_root / "scripts" / "zigux" / "check-phase7-string-helpers-packet.py"
        checker_path.unlink()
        expect_missing_file("missing_checker", tmp_root, "scripts/zigux/check-phase7-string-helpers-packet.py")
        cases_run += 1
        write_fixture_root(tmp_root)

        slice_path = tmp_root / "Documentation" / "zigux" / "phase7-string-helpers-slice.md"
        slice_marker = "`scripts/zigux/check-phase7-string-helpers-packet.py`"
        remove_once(slice_path, slice_marker)
        expect_missing_marker("missing_slice_checker_marker", tmp_root, f"Documentation/zigux/phase7-string-helpers-slice.md: {slice_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        slice_exclusions_marker = NO_EXTRA_SAMPLE_EXCLUSIONS_MARKER
        remove_once(slice_path, slice_exclusions_marker)
        expect_missing_marker("missing_slice_no_extra_sample_exclusions_marker", tmp_root, f"Documentation/zigux/phase7-string-helpers-slice.md: {slice_exclusions_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        remove_once(slice_path, NEXT_BOUNDED_STEP_MARKER)
        expect_missing_marker("missing_slice_next_bounded_step_marker", tmp_root, f"Documentation/zigux/phase7-string-helpers-slice.md: {NEXT_BOUNDED_STEP_MARKER}")
        cases_run += 1
        write_fixture_root(tmp_root)

        remove_once(checker_path, "--self-test")
        expect_missing_marker("missing_checker_selftest_flag_marker", tmp_root, "scripts/zigux/check-phase7-string-helpers-packet.py: --self-test")
        cases_run += 1
        write_fixture_root(tmp_root)

        remove_once(checker_path, "PHASE7_STRING_HELPERS_PACKET_SELF_TEST=pass")
        expect_missing_marker(
            "missing_checker_selftest_pass_marker",
            tmp_root,
            "scripts/zigux/check-phase7-string-helpers-packet.py: PHASE7_STRING_HELPERS_PACKET_SELF_TEST=pass",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        remove_once(checker_path, 'print("PHASE7_STRING_HELPERS_PACKET=pass")')
        expect_missing_marker(
            "missing_checker_pass_output_marker",
            tmp_root,
            'scripts/zigux/check-phase7-string-helpers-packet.py: print("PHASE7_STRING_HELPERS_PACKET=pass")',
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        remove_once(checker_path, 'print("PHASE7_STRING_HELPERS_PACKET=fail")')
        expect_missing_marker(
            "missing_checker_fail_output_marker",
            tmp_root,
            'scripts/zigux/check-phase7-string-helpers-packet.py: print("PHASE7_STRING_HELPERS_PACKET=fail")',
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_printf_marker = '"* `*printf*`"'
        remove_once(checker_path, checker_printf_marker)
        expect_missing_marker(
            "missing_checker_printf_boundary_marker",
            tmp_root,
            f"scripts/zigux/check-phase7-string-helpers-packet.py: {checker_printf_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_vsprintf_marker = '"* `*vsprintf*`"'
        remove_once(checker_path, checker_vsprintf_marker)
        expect_missing_marker(
            "missing_checker_vsprintf_boundary_marker",
            tmp_root,
            f"scripts/zigux/check-phase7-string-helpers-packet.py: {checker_vsprintf_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        for marker in [
            "MISSING_PHASE7_STRING_HELPERS_FILES_START",
            "MISSING_PHASE7_STRING_HELPERS_FILES_END",
            "MISSING_PHASE7_STRING_HELPERS_MARKERS_START",
            "MISSING_PHASE7_STRING_HELPERS_MARKERS_END",
            "MISMATCHED_PHASE7_STRING_HELPERS_COUNTS_START",
            "MISMATCHED_PHASE7_STRING_HELPERS_COUNTS_END",
            "UNEXPECTED_PHASE7_STRING_HELPERS_MARKERS_START",
            "UNEXPECTED_PHASE7_STRING_HELPERS_MARKERS_END",
        ]:
            remove_once(checker_path, marker)
            expect_missing_marker(
                f"missing_checker_output_marker_{marker.lower()}",
                tmp_root,
                f"scripts/zigux/check-phase7-string-helpers-packet.py: {marker}",
            )
            cases_run += 1
            write_fixture_root(tmp_root)

        helper_path = tmp_root / "lib" / "string_helpers.zig"
        helper_string_array_marker = "pub fn kasprintfStrarray("
        remove_once(helper_path, helper_string_array_marker)
        expect_missing_marker("missing_helper_string_array_marker", tmp_root, f"lib/string_helpers.zig: {helper_string_array_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_marker = "pub fn kstrdupQuotableCmdline("
        remove_once(helper_path, helper_marker)
        expect_missing_marker("missing_helper_cmdline_marker", tmp_root, f"lib/string_helpers.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_alias_marker = "pub fn kstrdup_quotable("
        remove_once(helper_path, helper_alias_marker)
        expect_missing_marker("missing_helper_quotable_alias_marker", tmp_root, f"lib/string_helpers.zig: {helper_alias_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_parse_alias_marker = "pub fn parse_int_array("
        remove_once(helper_path, helper_parse_alias_marker)
        expect_missing_marker("missing_helper_parse_alias_marker", tmp_root, f"lib/string_helpers.zig: {helper_parse_alias_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        tests_path = tmp_root / "zigux" / "tests" / "phase7_string_helpers.zig"
        tests_marker = 'test "phase 7 string helpers starter quotes already-materialized file paths and keeps the missing-file fallback explicit" {'
        remove_once(tests_path, tests_marker)
        expect_missing_marker("missing_tests_file_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        tests_no_entry_marker = 'test "phase 7 string helpers starter reports empty parse-int-array input as no entry" {'
        remove_once(tests_path, tests_no_entry_marker)
        expect_missing_marker("missing_tests_parse_no_entry_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_no_entry_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        tests_alloc_marker = 'test "phase 7 string helpers starter reports kstrdupQuotableFile allocation failure cleanly" {'
        remove_once(tests_path, tests_alloc_marker)
        expect_missing_marker("missing_tests_file_alloc_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_alloc_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        tests_cmdline_alloc_marker = 'test "phase 7 string helpers starter reports kstrdupQuotableCmdline allocation failure cleanly" {'
        remove_once(tests_path, tests_cmdline_alloc_marker)
        expect_missing_marker("missing_tests_cmdline_alloc_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_cmdline_alloc_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        tests_special_quoted_marker = 'test "phase 7 string helpers starter quotes special log-hazard bytes without widening beyond the exported c-string prefix" {'
        remove_once(tests_path, tests_special_quoted_marker)
        expect_missing_marker("missing_tests_special_quoted_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_special_quoted_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        tests_cmdline_replay_marker = 'test "phase 7 string helpers starter quotes cmdlines after collapsing trailing NULs and replacing inter-argument separators" {'
        remove_once(tests_path, tests_cmdline_replay_marker)
        expect_missing_marker("missing_tests_cmdline_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_cmdline_replay_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        tests_partial_cleanup_marker = 'test "phase 7 string helpers starter frees partially built arrays when allocator failure interrupts setup" {'
        remove_once(tests_path, tests_partial_cleanup_marker)
        expect_missing_marker("missing_tests_partial_cleanup_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_partial_cleanup_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        tests_overflow_marker = 'test "phase 7 string helpers starter reports overflow before sizing the null-terminated string-array view" {'
        remove_once(tests_path, tests_overflow_marker)
        expect_missing_marker("missing_tests_overflow_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_overflow_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        tests_blank_sentinel_marker = 'test "phase 7 string helpers starter reuses the blank string-array sentinel when no names are requested" {'
        remove_once(tests_path, tests_blank_sentinel_marker)
        expect_missing_marker("missing_tests_blank_sentinel_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_blank_sentinel_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        tests_sibling_zero_count_marker = 'test "phase 7 string helpers starter keeps sibling zero-count results on the shared sentinel after one owner deinitializes" {'
        remove_once(tests_path, tests_sibling_zero_count_marker)
        expect_missing_marker("missing_tests_sibling_zero_count_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_sibling_zero_count_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        tests_sibling_string_arrays_marker = 'test "phase 7 string helpers starter keeps sibling string arrays intact when one owner frees its result" {'
        remove_once(tests_path, tests_sibling_string_arrays_marker)
        expect_missing_marker("missing_tests_sibling_string_arrays_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_sibling_string_arrays_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        tests_idempotent_kfree_marker = 'test "phase 7 string helpers starter mirrors kfree_strarray teardown and stays idempotent" {'
        remove_once(tests_path, tests_idempotent_kfree_marker)
        expect_missing_marker("missing_tests_idempotent_kfree_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_idempotent_kfree_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        tests_case_boundary_marker = 'test "phase 7 string helpers starter uppercases and lowercases only through the exported c-string boundary" {'
        remove_once(tests_path, tests_case_boundary_marker)
        expect_missing_marker("missing_tests_case_boundary_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_case_boundary_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_path = tmp_root / "zigux" / "tests" / "phase7_string_helpers_manifest.json"
        manifest_marker = "dedicated helper-local checker-backed packet reviewability"
        remove_once(manifest_path, manifest_marker)
        expect_missing_marker("missing_manifest_checker_reviewability", tmp_root, f"zigux/tests/phase7_string_helpers_manifest.json: {manifest_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_exclusions_marker = NO_EXTRA_SAMPLE_EXCLUSIONS_MARKER
        remove_once(manifest_path, manifest_exclusions_marker)
        expect_missing_marker("missing_manifest_no_extra_sample_exclusions_marker", tmp_root, f"zigux/tests/phase7_string_helpers_manifest.json: {manifest_exclusions_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_next_bounded_step_marker = NEXT_BOUNDED_STEP_MARKER
        remove_once(manifest_path, manifest_next_bounded_step_marker)
        expect_missing_marker("missing_manifest_next_bounded_step_marker", tmp_root, f"zigux/tests/phase7_string_helpers_manifest.json: {manifest_next_bounded_step_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_cmdline_ownership_marker = CMDLINE_OWNERSHIP_MARKER
        remove_once(manifest_path, manifest_cmdline_ownership_marker)
        expect_missing_marker("missing_manifest_cmdline_ownership_marker", tmp_root, f"zigux/tests/phase7_string_helpers_manifest.json: {manifest_cmdline_ownership_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["lane_key"] = "P7-L09"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker("missing_manifest_lane_key_marker", tmp_root, "zigux/tests/phase7_string_helpers_manifest.json: lane_key")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["phase"] = "Phase 8"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker("missing_manifest_phase_marker", tmp_root, "zigux/tests/phase7_string_helpers_manifest.json: phase")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["anchor"] = "lib/cmdline.c"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker("missing_manifest_anchor_marker", tmp_root, "zigux/tests/phase7_string_helpers_manifest.json: anchor")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["current_master_state"] = "starter_packet"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker("missing_manifest_state_marker", tmp_root, "zigux/tests/phase7_string_helpers_manifest.json: current_master_state")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_path = tmp_root / "zigux" / "tests" / "phase7_string_helpers_survey.zig"
        survey_marker = 'try expectContains(sample_boundary, "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here.");'
        remove_once(survey_path, survey_marker)
        expect_missing_marker("missing_survey_format_boundary_replay", tmp_root, f"zigux/tests/phase7_string_helpers_survey.zig: {survey_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_marker = 'try expectContains(manifest, "kstrdupQuotableCmdline() keeps returned storage caller-owned, leaves the caller source buffer untouched, collapses trailing and inter-argument NULL separators only inside duplicated command-line storage, and only then applies quotable escaping");'
        remove_once(survey_path, survey_marker)
        expect_missing_marker("missing_survey_cmdline_ownership_replay", tmp_root, f"zigux/tests/phase7_string_helpers_survey.zig: {survey_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_marker = 'try expectContains(manifest, "\\\\\\\"next_bounded_step\\\\\\\": \\\\\\\"Keep the dedicated checkers, survey, sample-boundary, and format-boundary replays fail-closed on the still-parked `parse_int_array_user()` and `devm_kasprintf_strarray()` follow-ons\\\\\\\"");'
        remove_once(survey_path, survey_marker)
        expect_missing_marker("missing_survey_manifest_next_bounded_step_replay", tmp_root, f"zigux/tests/phase7_string_helpers_survey.zig: {survey_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        sample_boundary_path = tmp_root / "zigux" / "tests" / "phase7_string_helpers_sample_boundary.zig"
        sample_boundary_marker = DEVM_FOLLOW_ON_MARKER
        remove_once(sample_boundary_path, sample_boundary_marker)
        expect_missing_marker("missing_sample_boundary_follow_on_marker", tmp_root, f"zigux/tests/phase7_string_helpers_sample_boundary.zig: {sample_boundary_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        sample_boundary_marker = FULL_FAMILY_GAP_MARKER
        remove_once(sample_boundary_path, sample_boundary_marker)
        expect_missing_marker("missing_sample_boundary_non_goal_marker", tmp_root, f"zigux/tests/phase7_string_helpers_sample_boundary.zig: {sample_boundary_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        sample_boundary_printf_marker = "* `*printf*`"
        remove_once(sample_boundary_path, sample_boundary_printf_marker)
        expect_missing_marker("missing_sample_boundary_printf_marker", tmp_root, f"zigux/tests/phase7_string_helpers_sample_boundary.zig: {sample_boundary_printf_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        sample_boundary_vsprintf_marker = "* `*vsprintf*`"
        remove_once(sample_boundary_path, sample_boundary_vsprintf_marker)
        expect_missing_marker("missing_sample_boundary_vsprintf_marker", tmp_root, f"zigux/tests/phase7_string_helpers_sample_boundary.zig: {sample_boundary_vsprintf_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        sample_boundary_marker = FORMAT_BOUNDARY_MARKER
        remove_once(sample_boundary_path, sample_boundary_marker)
        expect_missing_marker("missing_sample_boundary_format_boundary_marker", tmp_root, f"zigux/tests/phase7_string_helpers_sample_boundary.zig: {sample_boundary_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        samples_readme_path = tmp_root / "samples" / "zigux" / "README.md"
        samples_readme_marker = "* `*rbtree*`"
        remove_once(samples_readme_path, samples_readme_marker)
        expect_missing_marker("missing_samples_readme_rbtree_boundary", tmp_root, f"samples/zigux/README.md: {samples_readme_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        samples_readme_marker = "* `*kasprintf*`"
        remove_once(samples_readme_path, samples_readme_marker)
        expect_missing_marker("missing_samples_readme_kasprintf_boundary", tmp_root, f"samples/zigux/README.md: {samples_readme_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        samples_readme_duplicate_marker = "* `*string*`\n"
        samples_readme_path.write_text(read_text(samples_readme_path) + samples_readme_duplicate_marker, encoding="utf-8")
        expect_mismatched_count(
            "duplicate_samples_readme_string_boundary",
            tmp_root,
            "samples/zigux/README.md: expected 1 occurrence(s) of " + repr("* `*string*`") + ", found 2",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        sample_boundary_duplicate = DEVM_FOLLOW_ON_MARKER + "\n"
        sample_boundary_path.write_text(read_text(sample_boundary_path) + sample_boundary_duplicate, encoding="utf-8")
        expect_mismatched_count(
            "duplicate_sample_boundary_follow_on_marker",
            tmp_root,
            "zigux/tests/phase7_string_helpers_sample_boundary.zig: expected 1 occurrence(s) of "
            + repr(DEVM_FOLLOW_ON_MARKER)
            + ", found 2",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_forbidden_marker = "pub fn devmKasprintfStrarray("
        helper_path.write_text(read_text(helper_path) + helper_forbidden_marker + "\n", encoding="utf-8")
        expect_unexpected_marker("unexpected_helper_devm_marker", tmp_root, f"lib/string_helpers.zig: {helper_forbidden_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_forbidden_alias_marker = "pub fn devm_kasprintf_strarray("
        helper_path.write_text(read_text(helper_path) + helper_forbidden_alias_marker + "\n", encoding="utf-8")
        expect_unexpected_marker("unexpected_helper_devm_alias_marker", tmp_root, f"lib/string_helpers.zig: {helper_forbidden_alias_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_forbidden_parse_marker = "pub fn parseIntArrayUser("
        helper_path.write_text(read_text(helper_path) + helper_forbidden_parse_marker + "\n", encoding="utf-8")
        expect_unexpected_marker("unexpected_helper_parse_marker", tmp_root, f"lib/string_helpers.zig: {helper_forbidden_parse_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_forbidden_parse_alias_marker = "pub fn parse_int_array_user("
        helper_path.write_text(read_text(helper_path) + helper_forbidden_parse_alias_marker + "\n", encoding="utf-8")
        expect_unexpected_marker("unexpected_helper_parse_alias_marker", tmp_root, f"lib/string_helpers.zig: {helper_forbidden_parse_alias_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        tests_forbidden_marker = "devmKasprintfStrarray"
        tests_path.write_text(read_text(tests_path) + tests_forbidden_marker + "\n", encoding="utf-8")
        expect_unexpected_marker("unexpected_tests_devm_marker", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_forbidden_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        tests_forbidden_alias_marker = "devm_kasprintf_strarray"
        tests_path.write_text(read_text(tests_path) + tests_forbidden_alias_marker + "\n", encoding="utf-8")
        expect_unexpected_marker("unexpected_tests_devm_alias_marker", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_forbidden_alias_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        tests_forbidden_parse_marker = "parseIntArrayUser"
        tests_path.write_text(read_text(tests_path) + tests_forbidden_parse_marker + "\n", encoding="utf-8")
        expect_unexpected_marker("unexpected_tests_parse_marker", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_forbidden_parse_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        tests_forbidden_parse_alias_marker = "parse_int_array_user"
        tests_path.write_text(read_text(tests_path) + tests_forbidden_parse_alias_marker + "\n", encoding="utf-8")
        expect_unexpected_marker("unexpected_tests_parse_alias_marker", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_forbidden_parse_alias_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_forbidden_marker = '"devmKasprintfStrarray"'
        manifest = json.loads(read_text(manifest_path))
        manifest["review_surfaces"].append("devmKasprintfStrarray")
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_unexpected_marker("unexpected_manifest_devm_marker", tmp_root, f"zigux/tests/phase7_string_helpers_manifest.json: {manifest_forbidden_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_forbidden_alias_marker = '"devm_kasprintf_strarray"'
        manifest = json.loads(read_text(manifest_path))
        manifest["review_surfaces"].append("devm_kasprintf_strarray")
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_unexpected_marker("unexpected_manifest_devm_alias_marker", tmp_root, f"zigux/tests/phase7_string_helpers_manifest.json: {manifest_forbidden_alias_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_forbidden_parse_marker = '"parseIntArrayUser"'
        manifest = json.loads(read_text(manifest_path))
        manifest["review_surfaces"].append("parseIntArrayUser")
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_unexpected_marker("unexpected_manifest_parse_marker", tmp_root, f"zigux/tests/phase7_string_helpers_manifest.json: {manifest_forbidden_parse_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_forbidden_parse_alias_marker = '"parse_int_array_user"'
        manifest = json.loads(read_text(manifest_path))
        manifest["review_surfaces"].append("parse_int_array_user")
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_unexpected_marker("unexpected_manifest_parse_alias_marker", tmp_root, f"zigux/tests/phase7_string_helpers_manifest.json: {manifest_forbidden_parse_alias_marker}")
        cases_run += 1

        assert cases_run == SELF_TEST_CASE_COUNT, cases_run


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run checker self-test instead of validating the repository")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("PHASE7_STRING_HELPERS_PACKET_SELF_TEST=pass")
        print(f"PHASE7_STRING_HELPERS_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
        return 0

    missing_files, missing_markers, mismatched_counts, unexpected_markers = validate(args.root)
    if not any((missing_files, missing_markers, mismatched_counts, unexpected_markers)):
        print("PHASE7_STRING_HELPERS_PACKET=pass")
        return 0

    print("PHASE7_STRING_HELPERS_PACKET=fail")
    if missing_files:
        print("MISSING_PHASE7_STRING_HELPERS_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_STRING_HELPERS_FILES_END")
    if missing_markers:
        print("MISSING_PHASE7_STRING_HELPERS_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_STRING_HELPERS_MARKERS_END")
    if mismatched_counts:
        print("MISMATCHED_PHASE7_STRING_HELPERS_COUNTS_START")
        for item in mismatched_counts:
            print(item)
        print("MISMATCHED_PHASE7_STRING_HELPERS_COUNTS_END")
    if unexpected_markers:
        print("UNEXPECTED_PHASE7_STRING_HELPERS_MARKERS_START")
        for item in unexpected_markers:
            print(item)
        print("UNEXPECTED_PHASE7_STRING_HELPERS_MARKERS_END")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
