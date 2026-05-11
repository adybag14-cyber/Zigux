#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase7-build-wiring.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase7_build.zig",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/README.md": [
        "zigux/tests/phase7_build.zig",
        "make -C zigux phase7",
    ],
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md": [
        "zigux/tests/phase7_build.zig",
        "python3 scripts/zigux/check-phase7-build-wiring.py",
    ],
    "samples/zigux/README.md": [
        "zigux/tests/phase7_build.zig",
        "scripts/zigux/check-phase7-build-wiring.py",
    ],
    "scripts/zigux/README.md": [
        "scripts/zigux/check-phase7-build-wiring.py",
        "zigux/tests/phase7_build.zig",
        "make -C zigux phase7-test",
    ],
    "zigux/tests/README.md": [
        "zigux/tests/phase7_build.zig",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        "zigux/tests/phase7_cmdline_survey.zig",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_rbtree_survey.zig",
    ],
    "zigux/Makefile": [
        "phase7-string-helpers-survey:",
        "phase7-string-helpers-sample-boundary:",
        "phase7-cmdline-survey:",
        "phase7-argv-split-survey:",
        "phase7-rbtree-survey:",
        "phase7-test:",
        "scripts/zigux/check-phase7-build-wiring.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py",
    ],
    "zigux/tests/phase7_build.zig": [
        "phase7-string-helpers-survey-tests",
        "\"phase7_string_helpers_survey.zig\"",
        "phase7-string-helpers-sample-boundary-tests",
        "\"phase7_string_helpers_sample_boundary.zig\"",
        "phase7-cmdline-survey-tests",
        "\"phase7_cmdline_survey.zig\"",
        "phase7-argv-split-survey-tests",
        "\"phase7_argv_split_survey.zig\"",
        "phase7-rbtree-survey-tests",
        "\"phase7_rbtree_survey.zig\"",
        "run_string_helpers_survey_tests.setCwd(b.path(\"../..\"));",
        "run_string_helpers_sample_boundary_tests.setCwd(b.path(\"../..\"));",
        "run_cmdline_survey_tests.setCwd(b.path(\"../..\"));",
        "run_argv_split_survey_tests.setCwd(b.path(\"../..\"));",
        "run_rbtree_survey_tests.setCwd(b.path(\"../..\"));",
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return [], collect_missing_markers(root)


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {rel: "\n".join(markers) + "\n" for rel, markers in REQUIRED_MARKERS.items()}
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text.get(rel, "# fixture\n"), encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [
        ("missing_build_wiring_checker", "scripts/zigux/check-phase7-build-wiring.py"),
        ("missing_phase7_build_file", "zigux/tests/phase7_build.zig"),
    ]
    marker_cases = [
        (
            "tests_readme_argv_split_survey_marker",
            "zigux/tests/README.md",
            "zigux/tests/phase7_argv_split_survey.zig",
            "",
            "zigux/tests/README.md: zigux/tests/phase7_argv_split_survey.zig",
        ),
        (
            "build_string_helpers_survey_cwd",
            "zigux/tests/phase7_build.zig",
            "run_string_helpers_survey_tests.setCwd(b.path(\"../..\"));",
            "",
            "zigux/tests/phase7_build.zig: run_string_helpers_survey_tests.setCwd(b.path(\"../..\"));",
        ),
        (
            "build_cmdline_survey_gate",
            "zigux/tests/phase7_build.zig",
            "phase7-cmdline-survey-tests",
            "",
            "zigux/tests/phase7_build.zig: phase7-cmdline-survey-tests",
        ),
        (
            "build_argv_split_survey_source",
            "zigux/tests/phase7_build.zig",
            "\"phase7_argv_split_survey.zig\"",
            "\"phase7_argv_split_survey_drift.zig\"",
            "zigux/tests/phase7_build.zig: \"phase7_argv_split_survey.zig\"",
        ),
        (
            "build_argv_split_survey_cwd",
            "zigux/tests/phase7_build.zig",
            "run_argv_split_survey_tests.setCwd(b.path(\"../..\"));",
            "",
            "zigux/tests/phase7_build.zig: run_argv_split_survey_tests.setCwd(b.path(\"../..\"));",
        ),
        (
            "build_rbtree_survey_gate",
            "zigux/tests/phase7_build.zig",
            "phase7-rbtree-survey-tests",
            "",
            "zigux/tests/phase7_build.zig: phase7-rbtree-survey-tests",
        ),
        (
            "makefile_string_helpers_survey_route",
            "zigux/Makefile",
            "phase7-string-helpers-survey:",
            "",
            "zigux/Makefile: phase7-string-helpers-survey:",
        ),
        (
            "makefile_argv_split_survey_route",
            "zigux/Makefile",
            "phase7-argv-split-survey:",
            "",
            "zigux/Makefile: phase7-argv-split-survey:",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_build_wiring_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        for case, rel in missing_file_cases:
            (tmp_root / rel).unlink()
            assert validate(tmp_root) == ([rel], []), case
            write_fixture_root(tmp_root)

        for case, rel, old, new, expected in marker_cases:
            path = tmp_root / rel
            text = path.read_text(encoding="utf-8")
            updated = text.replace(old, new, 1)
            assert updated != text, case
            path.write_text(updated, encoding="utf-8")
            assert validate(tmp_root) == ([], [expected]), case
            write_fixture_root(tmp_root)

    case_count = len(missing_file_cases) + len(marker_cases)
    print("PHASE7_BUILD_WIRING=pass")
    print(f"PHASE7_BUILD_WIRING_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the shared Phase 7 build wiring stays aligned.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE7_BUILD_WIRING=fail")
        print("MISSING_PHASE7_BUILD_WIRING_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_BUILD_WIRING_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_BUILD_WIRING=fail")
        print("MISSING_PHASE7_BUILD_WIRING_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_BUILD_WIRING_MARKERS_END")
        return 1

    print("PHASE7_BUILD_WIRING=pass")
    print(f"PHASE7_BUILD_WIRING_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE7_BUILD_WIRING_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
