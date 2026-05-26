#!/usr/bin/env python3
"""Validate the Phase 7 string-helpers format-boundary packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase7-string-helpers-slice.md",
    "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py",
    "zigux/tests/phase7_string_helpers_format_boundary.zig",
    "zigux/tests/phase7_string_helpers_survey.zig",
    "zigux/tests/phase7_string_helpers_manifest.json",
    "zigux/tests/phase7_string_helpers_sample_boundary.zig",
    "samples/zigux/README.md",
]

FOLLOW_ON_MARKER = (
    "Keep the dedicated checkers, survey, sample-boundary, and format-boundary replays "
    "fail-closed on the still-parked `parse_int_array_user()` and "
    "`devm_kasprintf_strarray()` follow-ons"
)

FORMAT_BOUNDARY_FOCUS = (
    "dedicated format-boundary replay for the trace-events formatting companion and broad-format exclusion"
)

FORMAT_BOUNDARY_SENTENCE = (
    "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here."
)

SLICE_BOUNDARY_REPLAY_MARKER = (
    "The dedicated sample-boundary and format-boundary replays should keep that distinction explicit while "
    "the expanded starter packet advances through helper-local review surfaces only."
)

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-string-helpers-slice.md": [
        "`zigux/tests/phase7_string_helpers_format_boundary.zig`",
        "`scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`",
        SLICE_BOUNDARY_REPLAY_MARKER,
        FOLLOW_ON_MARKER,
    ],
    "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py": [
        "--self-test",
        "PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET_SELF_TEST=pass",
        'print("PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET=pass")',
        'print("PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET=fail")',
        '"zigux/tests/phase7_string_helpers_format_boundary.zig",',
        "MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_FILES_START",
        "MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_FILES_END",
        "MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_MARKERS_START",
        "MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_MARKERS_END",
    ],
    "zigux/tests/phase7_string_helpers_format_boundary.zig": [
        'test "phase 7 string helper format boundary keeps the trace-events formatting companion as the only sample-root exception" {',
        'test "phase 7 string helper format boundary stays on sample-boundary review surfaces only" {',
        FORMAT_BOUNDARY_SENTENCE,
        "* `*printf*`",
        "* `*vsprintf*`",
    ],
    "zigux/tests/phase7_string_helpers_survey.zig": [
        'const format_boundary_checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py");',
        'try expectContains(format_boundary_checker, "PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET_SELF_TEST=pass");',
        'const format_boundary = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_format_boundary.zig");',
        'try expectContains(format_boundary, "phase 7 string helper format boundary keeps the trace-events formatting companion as the only sample-root exception");',
        'try expectContains(format_boundary, "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here.");',
    ],
    "zigux/tests/phase7_string_helpers_manifest.json": [
        '"scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py"',
        '"zigux/tests/phase7_string_helpers_format_boundary.zig"',
        FORMAT_BOUNDARY_FOCUS,
        FOLLOW_ON_MARKER,
    ],
    "zigux/tests/phase7_string_helpers_sample_boundary.zig": [
        FORMAT_BOUNDARY_SENTENCE,
        "* `*printf*`",
        "* `*vsprintf*`",
    ],
    "samples/zigux/README.md": [
        "Current `master` does ship one bounded `*string*` companion through `samples/zigux/trace_events_string_formatting_sample.zig`",
        FORMAT_BOUNDARY_SENTENCE,
        "* `*printf*`",
        "* `*vsprintf*`",
    ],
}

SELF_TEST_CASE_COUNT = 22


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


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return missing_files, collect_missing_markers(root)


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [marker], case


def remove_once(path: Path, marker: str) -> None:
    text = read_text(path)
    if marker + "\n" in text:
        text = text.replace(marker + "\n", "", 1)
    else:
        text = text.replace(marker, "", 1)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_string_helpers_format_boundary_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])
        cases_run = 0

        format_boundary_path = tmp_root / "zigux" / "tests" / "phase7_string_helpers_format_boundary.zig"
        format_boundary_path.unlink()
        expect_missing_file(
            "missing_format_boundary_replay",
            tmp_root,
            "zigux/tests/phase7_string_helpers_format_boundary.zig",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        slice_path = tmp_root / "Documentation" / "zigux" / "phase7-string-helpers-slice.md"
        slice_marker = "`zigux/tests/phase7_string_helpers_format_boundary.zig`"
        remove_once(slice_path, slice_marker)
        expect_missing_marker(
            "missing_slice_format_boundary_surface",
            tmp_root,
            f"Documentation/zigux/phase7-string-helpers-slice.md: {slice_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        slice_marker = SLICE_BOUNDARY_REPLAY_MARKER
        remove_once(slice_path, slice_marker)
        expect_missing_marker(
            "missing_slice_boundary_replay_marker",
            tmp_root,
            f"Documentation/zigux/phase7-string-helpers-slice.md: {slice_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        slice_marker = FOLLOW_ON_MARKER
        remove_once(slice_path, slice_marker)
        expect_missing_marker(
            "missing_slice_plural_follow_on_marker",
            tmp_root,
            f"Documentation/zigux/phase7-string-helpers-slice.md: {slice_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_path = tmp_root / "scripts" / "zigux" / "check-phase7-string-helpers-format-boundary-packet.py"
        checker_marker = "--self-test"
        remove_once(checker_path, checker_marker)
        expect_missing_marker(
            "missing_checker_selftest_flag",
            tmp_root,
            f"scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py: {checker_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_marker = "PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET_SELF_TEST=pass"
        remove_once(checker_path, checker_marker)
        expect_missing_marker(
            "missing_checker_selftest_pass_marker",
            tmp_root,
            f"scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py: {checker_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_marker = 'print("PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET=pass")'
        remove_once(checker_path, checker_marker)
        expect_missing_marker(
            "missing_checker_pass_output",
            tmp_root,
            f"scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py: {checker_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_marker = 'print("PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET=fail")'
        remove_once(checker_path, checker_marker)
        expect_missing_marker(
            "missing_checker_fail_output",
            tmp_root,
            f"scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py: {checker_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_marker = "MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_FILES_START"
        remove_once(checker_path, checker_marker)
        expect_missing_marker(
            "missing_checker_files_block",
            tmp_root,
            f"scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py: {checker_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_marker = "MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_MARKERS_START"
        remove_once(checker_path, checker_marker)
        expect_missing_marker(
            "missing_checker_markers_block",
            tmp_root,
            f"scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py: {checker_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_path = tmp_root / "zigux" / "tests" / "phase7_string_helpers_survey.zig"
        survey_marker = 'const format_boundary_checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py");'
        remove_once(survey_path, survey_marker)
        expect_missing_marker(
            "missing_survey_checker_readback",
            tmp_root,
            f"zigux/tests/phase7_string_helpers_survey.zig: {survey_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_marker = 'const format_boundary = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_format_boundary.zig");'
        remove_once(survey_path, survey_marker)
        expect_missing_marker(
            "missing_survey_format_boundary_readback",
            tmp_root,
            f"zigux/tests/phase7_string_helpers_survey.zig: {survey_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_path = tmp_root / "zigux" / "tests" / "phase7_string_helpers_manifest.json"
        manifest_marker = '"scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py"'
        remove_once(manifest_path, manifest_marker)
        expect_missing_marker(
            "missing_manifest_checker_surface",
            tmp_root,
            f"zigux/tests/phase7_string_helpers_manifest.json: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_marker = '"zigux/tests/phase7_string_helpers_format_boundary.zig"'
        remove_once(manifest_path, manifest_marker)
        expect_missing_marker(
            "missing_manifest_format_boundary_surface",
            tmp_root,
            f"zigux/tests/phase7_string_helpers_manifest.json: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_marker = FORMAT_BOUNDARY_FOCUS
        remove_once(manifest_path, manifest_marker)
        expect_missing_marker(
            "missing_manifest_format_boundary_focus",
            tmp_root,
            f"zigux/tests/phase7_string_helpers_manifest.json: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_marker = FOLLOW_ON_MARKER
        remove_once(manifest_path, manifest_marker)
        expect_missing_marker(
            "missing_manifest_follow_on_marker",
            tmp_root,
            f"zigux/tests/phase7_string_helpers_manifest.json: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        replay_marker = 'test "phase 7 string helper format boundary keeps the trace-events formatting companion as the only sample-root exception" {'
        remove_once(format_boundary_path, replay_marker)
        expect_missing_marker(
            "missing_format_boundary_exception_test",
            tmp_root,
            f"zigux/tests/phase7_string_helpers_format_boundary.zig: {replay_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        replay_marker = FORMAT_BOUNDARY_SENTENCE
        remove_once(format_boundary_path, replay_marker)
        expect_missing_marker(
            "missing_format_boundary_sentence",
            tmp_root,
            f"zigux/tests/phase7_string_helpers_format_boundary.zig: {replay_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        replay_marker = "* `*printf*`"
        remove_once(format_boundary_path, replay_marker)
        expect_missing_marker(
            "missing_format_boundary_printf_marker",
            tmp_root,
            f"zigux/tests/phase7_string_helpers_format_boundary.zig: {replay_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        replay_marker = "* `*vsprintf*`"
        remove_once(format_boundary_path, replay_marker)
        expect_missing_marker(
            "missing_format_boundary_vsprintf_marker",
            tmp_root,
            f"zigux/tests/phase7_string_helpers_format_boundary.zig: {replay_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        sample_boundary_path = tmp_root / "zigux" / "tests" / "phase7_string_helpers_sample_boundary.zig"
        sample_boundary_marker = FORMAT_BOUNDARY_SENTENCE
        remove_once(sample_boundary_path, sample_boundary_marker)
        expect_missing_marker(
            "missing_sample_boundary_format_sentence",
            tmp_root,
            f"zigux/tests/phase7_string_helpers_sample_boundary.zig: {sample_boundary_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        samples_readme_path = tmp_root / "samples" / "zigux" / "README.md"
        samples_readme_marker = FORMAT_BOUNDARY_SENTENCE
        remove_once(samples_readme_path, samples_readme_marker)
        expect_missing_marker(
            "missing_samples_readme_format_sentence",
            tmp_root,
            f"samples/zigux/README.md: {samples_readme_marker}",
        )
        cases_run += 1

        assert cases_run == SELF_TEST_CASE_COUNT, cases_run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run checker self-test instead of validating the repository")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        print("PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET_SELF_TEST=pass")
        print(f"PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
        return 0

    missing_files, missing_markers = validate(args.root)
    if not any((missing_files, missing_markers)):
        print("PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET=pass")
        return 0

    print("PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET=fail")
    if missing_files:
        print("MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_FILES_END")
    if missing_markers:
        print("MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_MARKERS_END")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
