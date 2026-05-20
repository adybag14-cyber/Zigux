#!/usr/bin/env python3
"""Validate the current Phase 7 string-helpers helper-local packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

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
    "on the still-parked `devm_kasprintf_strarray()` follow-on"
)

NO_EXTRA_SAMPLE_BULLETS = [
    "* `*string*`",
    "* `*cmdline*`",
    "* `*argv*`",
    "* `*rbtree*`",
    "* `*kasprintf*`",
    "* `*strarray*`",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-string-helpers-slice.md": [
        "`PHASE7_STATUS=starter_landed`",
        "`scripts/zigux/check-phase7-string-helpers-packet.py`",
        "quoted file-path duplication that keeps an explicit `<unknown>` fallback for missing inputs while still escaping special characters through the same quotable path",
        "`stringUpper()`, `string_upper()`, `stringLower()`, and `string_lower()` keep case-conversion writes inside caller-provided destination storage and stop at the exported C-string boundary",
        "quoted cmdline duplication that collapses trailing NULs",
        DEVM_FOLLOW_ON_MARKER,
    ],
    "scripts/zigux/check-phase7-string-helpers-packet.py": [
        "--self-test",
        "PHASE7_STRING_HELPERS_PACKET_SELF_TEST=pass",
        '"zigux/tests/phase7_string_helpers_sample_boundary.zig",',
        '"lib/string_helpers.zig": [',
        '"pub fn devmKasprintfStrarray("',
        '"pub fn devm_kasprintf_strarray("',
        '"zigux/tests/phase7_string_helpers_manifest.json": [',
        '"\\\\\\"devmKasprintfStrarray\\\\\\""',
        '"\\\\\\"devm_kasprintf_strarray\\\\\\""',
        "MISMATCHED_PHASE7_STRING_HELPERS_COUNTS_START",
        "MISMATCHED_PHASE7_STRING_HELPERS_COUNTS_END",
        "UNEXPECTED_PHASE7_STRING_HELPERS_MARKERS_START",
        "UNEXPECTED_PHASE7_STRING_HELPERS_MARKERS_END",
    ],
    "lib/string_helpers.zig": [
        "pub fn kstrdupQuotable(",
        "pub fn kstrdup_quotable(",
        "pub fn kstrdupQuotableFile(",
        "pub fn kstrdup_quotable_file(",
        "pub fn kstrdupQuotableCmdline(",
        "pub fn kstrdup_quotable_cmdline(",
        "pub fn parseIntArray(",
        "pub fn parse_int_array(",
        "pub fn stringUpper(",
        "pub fn string_upper(",
        "pub fn stringLower(",
        "pub fn string_lower(",
    ],
    "zigux/tests/phase7_string_helpers.zig": [
        'test "phase 7 string helpers starter quotes special log-hazard bytes without widening beyond the exported c-string prefix" {',
        'test "phase 7 string helpers starter quotes already-materialized file paths and keeps the missing-file fallback explicit" {',
        'test "phase 7 string helpers starter quotes cmdlines after collapsing trailing NULs and replacing inter-argument separators" {',
        'test "phase 7 string helpers starter reports empty parse-int-array input as no entry" {',
        'test "phase 7 string helpers starter reports parse-int-array allocation failure cleanly" {',
        'test "phase 7 string helpers starter uppercases and lowercases only through the exported c-string boundary" {',
        'test "phase 7 string helpers starter reports kstrdupQuotableFile allocation failure cleanly" {',
        'test "phase 7 string helpers starter reports kstrdupQuotableCmdline allocation failure cleanly" {',
        'test "phase 7 string helpers starter reports duplicate-and-replace allocation failure cleanly" {',
    ],
    "zigux/tests/phase7_string_helpers_manifest.json": [
        '"scripts/zigux/check-phase7-string-helpers-packet.py"',
        "quoted file-path duplication with explicit missing-file fallback and quotable escaping for already-materialized path strings",
        "bounded uppercase and lowercase copies through the exported C-string boundary",
        "quoted cmdline duplication that collapses trailing NULL separators into spaces before escaping special characters",
        "dedicated helper-local checker-backed packet reviewability",
        DEVM_FOLLOW_ON_MARKER,
    ],
    "zigux/tests/phase7_string_helpers_survey.zig": [
        'const checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-string-helpers-packet.py");',
        'try expectContains(checker, "PHASE7_STRING_HELPERS_PACKET_SELF_TEST=pass");',
        'try expectContains(manifest, "\\\\"scripts/zigux/check-phase7-string-helpers-packet.py\\\\"");',
        'try expectContains(manifest, "dedicated helper-local checker-backed packet reviewability");',
        'try expectContains(manifest, "\\\\"next_bounded_step\\\\": \\\\\"Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on");',
        'try expectContains(sample_boundary, "Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on");',
    ],
    "zigux/tests/phase7_string_helpers_sample_boundary.zig": [
        "phase 7 string helper boundary keeps the no-string-sample policy lane-local",
        "the broader full-family packet that still leaves `devm_kasprintf_strarray()` outside the current `master` helper packet",
        "Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on",
    ],
    "samples/zigux/README.md": [
        "Current `master` still ships no standalone Phase 5 sample-root files here for:",
        *NO_EXTRA_SAMPLE_BULLETS,
    ],
}

COUNTED_MARKERS = {
    "Documentation/zigux/phase7-string-helpers-slice.md": [
        (DEVM_FOLLOW_ON_MARKER, 1),
    ],
    "zigux/tests/phase7_string_helpers_manifest.json": [
        (
            "Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on",
            1,
        ),
    ],
    "zigux/tests/phase7_string_helpers_sample_boundary.zig": [
        (
            "Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on",
            1,
        ),
    ],
    "samples/zigux/README.md": [(marker, 1) for marker in NO_EXTRA_SAMPLE_BULLETS],
}

FORBIDDEN_MARKERS = {
    "lib/string_helpers.zig": [
        "pub fn devmKasprintfStrarray(",
        "pub fn devm_kasprintf_strarray(",
    ],
    "zigux/tests/phase7_string_helpers.zig": [
        "devmKasprintfStrarray",
        "devm_kasprintf_strarray",
    ],
    "zigux/tests/phase7_string_helpers_manifest.json": [
        '"devmKasprintfStrarray"',
        '"devm_kasprintf_strarray"',
    ],
}

SELF_TEST_CASE_COUNT = 26


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_root(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES:
        lines = list(REQUIRED_MARKERS[rel])
        for marker, expected in COUNTED_MARKERS.get(rel, []):
            if marker not in lines:
                lines.extend([marker] * expected)
        write(tmp_root / rel, "\n".join(lines) + "\n")


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


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_string_helpers_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [], [], [])

        checker_path = tmp_root / "scripts" / "zigux" / "check-phase7-string-helpers-packet.py"
        checker_path.unlink()
        expect_missing_file("missing_checker", tmp_root, "scripts/zigux/check-phase7-string-helpers-packet.py")
        write_fixture_root(tmp_root)

        slice_path = tmp_root / "Documentation" / "zigux" / "phase7-string-helpers-slice.md"
        slice_marker = "`scripts/zigux/check-phase7-string-helpers-packet.py`"
        slice_path.write_text(read_text(slice_path).replace(slice_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_slice_checker_marker", tmp_root, f"Documentation/zigux/phase7-string-helpers-slice.md: {slice_marker}")
        write_fixture_root(tmp_root)

        slice_path.write_text(read_text(slice_path).replace(DEVM_FOLLOW_ON_MARKER + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_slice_devm_follow_on_marker", tmp_root, f"Documentation/zigux/phase7-string-helpers-slice.md: {DEVM_FOLLOW_ON_MARKER}")
        write_fixture_root(tmp_root)

        helper_path = tmp_root / "lib" / "string_helpers.zig"
        helper_marker = "pub fn kstrdupQuotableCmdline("
        helper_path.write_text(read_text(helper_path).replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_cmdline_marker", tmp_root, f"lib/string_helpers.zig: {helper_marker}")
        write_fixture_root(tmp_root)

        helper_alias_marker = "pub fn kstrdup_quotable("
        helper_path.write_text(read_text(helper_path).replace(helper_alias_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_quotable_alias_marker", tmp_root, f"lib/string_helpers.zig: {helper_alias_marker}")
        write_fixture_root(tmp_root)

        helper_parse_alias_marker = "pub fn parse_int_array("
        helper_path.write_text(read_text(helper_path).replace(helper_parse_alias_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_parse_alias_marker", tmp_root, f"lib/string_helpers.zig: {helper_parse_alias_marker}")
        write_fixture_root(tmp_root)

        tests_path = tmp_root / "zigux" / "tests" / "phase7_string_helpers.zig"
        tests_marker = 'test "phase 7 string helpers starter quotes already-materialized file paths and keeps the missing-file fallback explicit" {'
        tests_path.write_text(read_text(tests_path).replace(tests_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_tests_file_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_marker}")
        write_fixture_root(tmp_root)

        tests_no_entry_marker = 'test "phase 7 string helpers starter reports empty parse-int-array input as no entry" {'
        tests_path.write_text(read_text(tests_path).replace(tests_no_entry_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_tests_parse_no_entry_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_no_entry_marker}")
        write_fixture_root(tmp_root)

        tests_alloc_marker = 'test "phase 7 string helpers starter reports kstrdupQuotableFile allocation failure cleanly" {'
        tests_path.write_text(read_text(tests_path).replace(tests_alloc_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_tests_file_alloc_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_alloc_marker}")
        write_fixture_root(tmp_root)

        tests_cmdline_alloc_marker = 'test "phase 7 string helpers starter reports kstrdupQuotableCmdline allocation failure cleanly" {'
        tests_path.write_text(read_text(tests_path).replace(tests_cmdline_alloc_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_tests_cmdline_alloc_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_cmdline_alloc_marker}")
        write_fixture_root(tmp_root)

        tests_special_quoted_marker = 'test "phase 7 string helpers starter quotes special log-hazard bytes without widening beyond the exported c-string prefix" {'
        tests_path.write_text(read_text(tests_path).replace(tests_special_quoted_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_tests_special_quoted_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_special_quoted_marker}")
        write_fixture_root(tmp_root)

        tests_cmdline_replay_marker = 'test "phase 7 string helpers starter quotes cmdlines after collapsing trailing NULs and replacing inter-argument separators" {'
        tests_path.write_text(read_text(tests_path).replace(tests_cmdline_replay_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_tests_cmdline_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_cmdline_replay_marker}")
        write_fixture_root(tmp_root)

        tests_parse_alloc_marker = 'test "phase 7 string helpers starter reports parse-int-array allocation failure cleanly" {'
        tests_path.write_text(read_text(tests_path).replace(tests_parse_alloc_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_tests_parse_alloc_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_parse_alloc_marker}")
        write_fixture_root(tmp_root)

        tests_case_boundary_marker = 'test "phase 7 string helpers starter uppercases and lowercases only through the exported c-string boundary" {'
        tests_path.write_text(read_text(tests_path).replace(tests_case_boundary_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_tests_case_boundary_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_case_boundary_marker}")
        write_fixture_root(tmp_root)

        tests_replace_alloc_marker = 'test "phase 7 string helpers starter reports duplicate-and-replace allocation failure cleanly" {'
        tests_path.write_text(read_text(tests_path).replace(tests_replace_alloc_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_tests_replace_alloc_replay", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_replace_alloc_marker}")
        write_fixture_root(tmp_root)

        manifest_path = tmp_root / "zigux" / "tests" / "phase7_string_helpers_manifest.json"
        manifest_marker = "dedicated helper-local checker-backed packet reviewability"
        manifest_path.write_text(read_text(manifest_path).replace(manifest_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_manifest_checker_focus", tmp_root, f"zigux/tests/phase7_string_helpers_manifest.json: {manifest_marker}")
        write_fixture_root(tmp_root)

        survey_path = tmp_root / "zigux" / "tests" / "phase7_string_helpers_survey.zig"
        survey_marker = 'try expectContains(checker, "PHASE7_STRING_HELPERS_PACKET_SELF_TEST=pass");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_checker_selftest_marker", tmp_root, f"zigux/tests/phase7_string_helpers_survey.zig: {survey_marker}")
        write_fixture_root(tmp_root)

        survey_follow_on_marker = 'try expectContains(sample_boundary, "Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on");'
        survey_path.write_text(read_text(survey_path).replace(survey_follow_on_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_devm_follow_on_marker", tmp_root, f"zigux/tests/phase7_string_helpers_survey.zig: {survey_follow_on_marker}")
        write_fixture_root(tmp_root)

        boundary_path = tmp_root / "zigux" / "tests" / "phase7_string_helpers_sample_boundary.zig"
        boundary_marker = "Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked `devm_kasprintf_strarray()` follow-on"
        boundary_path.write_text(read_text(boundary_path).replace(boundary_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_boundary_devm_follow_on_marker", tmp_root, f"zigux/tests/phase7_string_helpers_sample_boundary.zig: {boundary_marker}")
        write_fixture_root(tmp_root)

        samples_path = tmp_root / "samples" / "zigux" / "README.md"
        samples_marker = "* `*cmdline*`"
        samples_path.write_text(read_text(samples_path).replace(samples_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_samples_cmdline_boundary_marker", tmp_root, f"samples/zigux/README.md: {samples_marker}")
        write_fixture_root(tmp_root)

        helper_forbidden = "pub fn devmKasprintfStrarray("
        helper_path.write_text(read_text(helper_path) + helper_forbidden + "\n", encoding="utf-8")
        expect_unexpected_marker("unexpected_helper_devm_helper", tmp_root, f"lib/string_helpers.zig: {helper_forbidden}")
        write_fixture_root(tmp_root)

        tests_forbidden = "devm_kasprintf_strarray"
        tests_path.write_text(read_text(tests_path) + tests_forbidden + "\n", encoding="utf-8")
        expect_unexpected_marker("unexpected_tests_devm_helper", tmp_root, f"zigux/tests/phase7_string_helpers.zig: {tests_forbidden}")
        write_fixture_root(tmp_root)

        manifest_forbidden = '"devmKasprintfStrarray"'
        manifest_path.write_text(read_text(manifest_path) + manifest_forbidden + "\n", encoding="utf-8")
        expect_unexpected_marker("unexpected_manifest_devm_helper", tmp_root, f'zigux/tests/phase7_string_helpers_manifest.json: {manifest_forbidden}')
        write_fixture_root(tmp_root)

        slice_path.write_text(read_text(slice_path) + DEVM_FOLLOW_ON_MARKER + "\n", encoding="utf-8")
        expect_mismatched_count(
            "duplicate_slice_devm_follow_on_marker",
            tmp_root,
            "Documentation/zigux/phase7-string-helpers-slice.md: expected 1 occurrence(s) of "
            f"{DEVM_FOLLOW_ON_MARKER!r}, found 2",
        )
        write_fixture_root(tmp_root)

        boundary_path.write_text(read_text(boundary_path) + boundary_marker + "\n", encoding="utf-8")
        expect_mismatched_count(
            "duplicate_boundary_devm_follow_on_marker",
            tmp_root,
            "zigux/tests/phase7_string_helpers_sample_boundary.zig: expected 1 occurrence(s) of "
            f"{boundary_marker!r}, found 2",
        )
        write_fixture_root(tmp_root)

        samples_path.write_text(read_text(samples_path) + "* `*kasprintf*`\n", encoding="utf-8")
        expect_mismatched_count(
            "duplicate_samples_kasprintf_boundary_marker",
            tmp_root,
            "samples/zigux/README.md: expected 1 occurrence(s) of '* `*kasprintf*`', found 2",
        )
        write_fixture_root(tmp_root)

        manifest_next_marker = (
            "Keep the dedicated checker, survey, and sample-boundary replays fail-closed on the still-parked "
            "`devm_kasprintf_strarray()` follow-on"
        )
        manifest_path.write_text(read_text(manifest_path) + manifest_next_marker + "\n", encoding="utf-8")
        expect_mismatched_count(
            "duplicate_manifest_next_step_marker",
            tmp_root,
            "zigux/tests/phase7_string_helpers_manifest.json: expected 1 occurrence(s) of "
            f"{manifest_next_marker!r}, found 2",
        )

    print("PHASE7_STRING_HELPERS_PACKET_SELF_TEST=pass")
    print(f"PHASE7_STRING_HELPERS_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to validate (default: current repository root)")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests instead of validating the repository")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers, mismatched_counts, unexpected_markers = validate(args.repo_root)
    if missing_files:
        print("PHASE7_STRING_HELPERS_PACKET=fail")
        print("MISSING_PHASE7_STRING_HELPERS_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_STRING_HELPERS_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_STRING_HELPERS_PACKET=fail")
        print("MISSING_PHASE7_STRING_HELPERS_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_STRING_HELPERS_MARKERS_END")
        return 1

    if mismatched_counts:
        print("PHASE7_STRING_HELPERS_PACKET=fail")
        print("MISMATCHED_PHASE7_STRING_HELPERS_COUNTS_START")
        for item in mismatched_counts:
            print(item)
        print("MISMATCHED_PHASE7_STRING_HELPERS_COUNTS_END")
        return 1

    if unexpected_markers:
        print("PHASE7_STRING_HELPERS_PACKET=fail")
        print("UNEXPECTED_PHASE7_STRING_HELPERS_MARKERS_START")
        for item in unexpected_markers:
            print(item)
        print("UNEXPECTED_PHASE7_STRING_HELPERS_MARKERS_END")
        return 1

    print("PHASE7_STRING_HELPERS_PACKET=pass")
    print(f"PHASE7_STRING_HELPERS_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print("PHASE7_STRING_HELPERS_PACKET_REQUIRED_MARKER_COUNT=" f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    print("PHASE7_STRING_HELPERS_PACKET_COUNTED_MARKER_COUNT=" f"{sum(len(markers) for markers in COUNTED_MARKERS.values())}")
    print("PHASE7_STRING_HELPERS_PACKET_FORBIDDEN_MARKER_COUNT=" f"{sum(len(markers) for markers in FORBIDDEN_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
