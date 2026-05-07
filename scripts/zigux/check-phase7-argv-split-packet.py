#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase7-argv-split-slice.md",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "zigux/Makefile",
    "zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_argv_split.zig",
    "zigux/tests/phase7_argv_split_survey.zig",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    "lib/argv_split.zig",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-argv-split-slice.md": [
        "null-terminated pointer-vector access through `cArgv()`",
        "blank-input sentinel reuse and repeatable teardown through both `deinit()` and `argvFree()`",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
    ],
    "scripts/zigux/check-phase7-argv-split-packet.py": [
        "--self-test",
        "PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass",
    ],
    "zigux/Makefile": [
        "scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "scripts/zigux/check-phase7-argv-split-packet.py",
    ],
    "zigux/tests/phase7_build.zig": [
        "phase7-argv-split-tests",
        "\"phase7_argv_split.zig\"",
        "phase7-argv-split-survey-tests",
        "\"phase7_argv_split_survey.zig\"",
        "run_argv_split_survey_tests.setCwd(b.path(\"../..\"));",
    ],
    "zigux/tests/phase7_argv_split.zig": [
        '@import("fixtures/phase7_argv_split_vectors.zig")',
        "split.cArgv()",
        "phase 7 argvSplit token buffer does not alias the source text",
        "phase 7 blank argvSplit input reuses the empty exported argv view",
        "phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space",
        "phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable",
        "phase 7 argvSplit deinit stays safe when called after teardown already cleared the result",
        "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable",
    ],
    "zigux/tests/phase7_argv_split_survey.zig": [
        "Documentation/zigux/phase7-argv-split-slice.md",
        "zigux/tests/phase7_argv_split_manifest.json",
        "PHASE7_LANE_KEY=",
    ],
    "zigux/tests/phase7_argv_split_manifest.json": [
        "\"id\": \"phase7-argv-split-packet-checker\"",
        "\"zigux_destination\": \"scripts/zigux/check-phase7-argv-split-packet.py\"",
    ],
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig": [
        "repeated whitespace collapses into separators",
        "blank input stays empty",
        "whitespace before first NUL stays blank",
        "leading NUL truncates to zero argv entries",
        "first NUL stops counting and splitting",
        "quote characters stay inside returned tokens",
    ],
}

EXACT_COUNT_MARKERS = {
    "zigux/tests/phase7_argv_split_survey.zig": [
        ("Documentation/zigux/phase7-argv-split-slice.md", 1),
        ("zigux/tests/phase7_argv_split_manifest.json", 1),
        ("PHASE7_LANE_KEY=", 1),
    ],
    "zigux/tests/phase7_argv_split_manifest.json": [
        ('\"id\": \"phase7-argv-split-packet-checker\"', 1),
        ('\"zigux_destination\": \"scripts/zigux/check-phase7-argv-split-packet.py\"', 1),
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    for rel, marker_counts in EXACT_COUNT_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker, expected_count in marker_counts:
            actual_count = text.count(marker)
            if actual_count != expected_count:
                missing.append(f"{rel}: {marker}:expected={expected_count}:actual={actual_count}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return missing_files, collect_missing_markers(root)


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {
        "Documentation/zigux/phase7-argv-split-slice.md": "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase7-argv-split-slice.md"]) + "\n",
        "scripts/zigux/check-phase7-argv-split-packet.py": "\n".join(REQUIRED_MARKERS["scripts/zigux/check-phase7-argv-split-packet.py"]) + "\n",
        "zigux/Makefile": "\n".join(REQUIRED_MARKERS["zigux/Makefile"]) + "\n",
        "zigux/tests/phase7_build.zig": "\n".join(REQUIRED_MARKERS["zigux/tests/phase7_build.zig"]) + "\n",
        "zigux/tests/phase7_argv_split.zig": "\n".join(REQUIRED_MARKERS["zigux/tests/phase7_argv_split.zig"]) + "\n",
        "zigux/tests/phase7_argv_split_survey.zig": "\n".join(REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"]) + "\n",
        "zigux/tests/phase7_argv_split_manifest.json": "\n".join(REQUIRED_MARKERS["zigux/tests/phase7_argv_split_manifest.json"]) + "\n",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig": "\n".join(REQUIRED_MARKERS["zigux/tests/fixtures/phase7_argv_split_vectors.zig"]) + "\n",
        "lib/argv_split.zig": "// fixture\n",
    }

    for rel, marker_counts in EXACT_COUNT_MARKERS.items():
        text = fixture_text.get(rel, "")
        for marker, _expected_count in marker_counts:
            if marker not in text:
                text += marker + "\n"
        fixture_text[rel] = text

    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text.get(rel, "// fixture\n"), encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [marker], case


def remove_first_marker(text: str, marker: str) -> str:
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if marker in line:
            updated = "".join(lines[:index] + lines[index + 1 :])
            assert updated != text
            return updated
    updated = text.replace(marker, "", 1)
    assert updated != text
    return updated


def duplicate_first_marker(text: str, marker: str) -> str:
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if marker in line:
            updated = "".join(lines[: index + 1] + [line] + lines[index + 1 :])
            assert updated != text
            return updated
    updated = text.replace(marker, f"{marker}\n{marker}", 1)
    assert updated != text
    return updated


def run_self_test() -> None:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_argv_split_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        checker_path = tmp_root / "scripts" / "zigux" / "check-phase7-argv-split-packet.py"
        checker_path.unlink()
        expect_missing_file(
            "missing_argv_split_packet_checker",
            tmp_root,
            "scripts/zigux/check-phase7-argv-split-packet.py",
        )
        case_count += 1
        write_fixture_root(tmp_root)

        survey_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_survey.zig"
        survey_path.unlink()
        expect_missing_file(
            "missing_argv_split_survey",
            tmp_root,
            "zigux/tests/phase7_argv_split_survey.zig",
        )
        case_count += 1
        write_fixture_root(tmp_root)

        manifest_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_manifest.json"
        manifest_path.unlink()
        expect_missing_file(
            "missing_argv_split_manifest",
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json",
        )
        case_count += 1
        write_fixture_root(tmp_root)

        fixture_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase7_argv_split_vectors.zig"
        fixture_path.unlink()
        expect_missing_file(
            "missing_argv_split_vectors_fixture",
            tmp_root,
            "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        )
        case_count += 1
        write_fixture_root(tmp_root)

        slice_path = tmp_root / "Documentation" / "zigux" / "phase7-argv-split-slice.md"
        original_slice = slice_path.read_text(encoding="utf-8")
        slice_path.write_text(
            original_slice.replace("python3 scripts/zigux/check-phase7-argv-split-packet.py", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_slice_packet_checker_marker",
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md: python3 scripts/zigux/check-phase7-argv-split-packet.py",
        )
        case_count += 1
        slice_path.write_text(original_slice, encoding="utf-8")

        build_path = tmp_root / "zigux" / "tests" / "phase7_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace("phase7-argv-split-survey-tests", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_build_survey_gate_marker",
            tmp_root,
            "zigux/tests/phase7_build.zig: phase7-argv-split-survey-tests",
        )
        case_count += 1
        build_path.write_text(original_build, encoding="utf-8")

        makefile_path = tmp_root / "zigux" / "Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace("scripts/zigux/check-phase7-argv-split-packet.py --self-test", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_makefile_self_test_marker",
            tmp_root,
            "zigux/Makefile: scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        )
        case_count += 1
        makefile_path.write_text(original_makefile, encoding="utf-8")

        survey_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_survey.zig"
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            remove_first_marker(original_survey, "zigux/tests/phase7_argv_split_manifest.json"),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_survey_manifest_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split_survey.zig: zigux/tests/phase7_argv_split_manifest.json",
        )
        case_count += 1
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            remove_first_marker(original_survey, "PHASE7_LANE_KEY="),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_survey_lane_key_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split_survey.zig: PHASE7_LANE_KEY=",
        )
        case_count += 1
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            duplicate_first_marker(original_survey, "zigux/tests/phase7_argv_split_manifest.json"),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_survey_manifest_duplicate_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split_survey.zig: zigux/tests/phase7_argv_split_manifest.json:expected=1:actual=2",
        )
        case_count += 1
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            duplicate_first_marker(original_survey, "PHASE7_LANE_KEY="),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_survey_lane_key_duplicate_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split_survey.zig: PHASE7_LANE_KEY=:expected=1:actual=2",
        )
        case_count += 1
        survey_path.write_text(original_survey, encoding="utf-8")

        tests_path = tmp_root / "zigux" / "tests" / "phase7_argv_split.zig"
        original_tests = tests_path.read_text(encoding="utf-8")
        tests_path.write_text(original_tests.replace("split.cArgv()", "split.argv", 1), encoding="utf-8")
        expect_missing_marker(
            "argv_split_cargv_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig: split.cArgv()",
        )
        case_count += 1
        tests_path.write_text(original_tests, encoding="utf-8")

        fixture_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase7_argv_split_vectors.zig"
        original_fixture = fixture_path.read_text(encoding="utf-8")
        fixture_path.write_text(
            original_fixture.replace("whitespace before first NUL stays blank", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_whitespace_before_nul_fixture_marker",
            tmp_root,
            "zigux/tests/fixtures/phase7_argv_split_vectors.zig: whitespace before first NUL stays blank",
        )
        case_count += 1
        fixture_path.write_text(original_fixture, encoding="utf-8")

        fixture_path.write_text(
            original_fixture.replace("leading NUL truncates to zero argv entries", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_leading_nul_fixture_marker",
            tmp_root,
            "zigux/tests/fixtures/phase7_argv_split_vectors.zig: leading NUL truncates to zero argv entries",
        )
        case_count += 1
        fixture_path.write_text(original_fixture, encoding="utf-8")

        fixture_path.write_text(
            original_fixture.replace("quote characters stay inside returned tokens", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_quote_fixture_marker",
            tmp_root,
            "zigux/tests/fixtures/phase7_argv_split_vectors.zig: quote characters stay inside returned tokens",
        )
        case_count += 1
        fixture_path.write_text(original_fixture, encoding="utf-8")

        manifest_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_manifest.json"
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(
            original_manifest.replace("\"id\": \"phase7-argv-split-packet-checker\"", "\"id\": \"phase7-argv-split-missing-checker\"", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_manifest_checker_id_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json: \"id\": \"phase7-argv-split-packet-checker\"",
        )
        case_count += 1
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            original_manifest.replace(
                "\"zigux_destination\": \"scripts/zigux/check-phase7-argv-split-packet.py\"",
                "\"zigux_destination\": \"scripts/zigux/check-phase7-argv-split-packet-drift.py\"",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_manifest_checker_destination_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json: \"zigux_destination\": \"scripts/zigux/check-phase7-argv-split-packet.py\"",
        )
        case_count += 1
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            duplicate_first_marker(original_manifest, '"id": "phase7-argv-split-packet-checker"'),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_manifest_checker_id_duplicate_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json: \"id\": \"phase7-argv-split-packet-checker\":expected=1:actual=2",
        )
        case_count += 1
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            duplicate_first_marker(
                original_manifest,
                '"zigux_destination": "scripts/zigux/check-phase7-argv-split-packet.py"',
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_manifest_checker_destination_duplicate_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json: \"zigux_destination\": \"scripts/zigux/check-phase7-argv-split-packet.py\":expected=1:actual=2",
        )
        case_count += 1

    print("PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass")
    print(f"PHASE7_ARGV_SPLIT_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the dedicated Phase 7 argv_split packet surface.")
    parser.add_argument("--self-test", action="store_true", help="Run packet checker self-tests without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
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
    print(f"PHASE7_ARGV_SPLIT_PACKET_REQUIRED_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())