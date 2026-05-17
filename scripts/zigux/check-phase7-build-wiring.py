#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

BUILD_PATH = Path("zigux/tests/phase7_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

BUILD_MARKERS = [
    '"../../lib/string_helpers.zig"',
    '"../../lib/cmdline.zig"',
    '"../../lib/argv_split.zig"',
    '"../../lib/rbtree.zig"',
    'run_string_helpers_sample_boundary_tests.setCwd(b.path("../.."));',
    'run_cmdline_survey_tests.setCwd(b.path("../.."));',
    'run_argv_split_survey_tests.setCwd(b.path("../.."));',
    'run_rbtree_survey_tests.setCwd(b.path("../.."));',
    '"phase7-string-helpers-test"',
    '"phase7-string-helpers-survey"',
    '"phase7-string-helpers-sample-boundary"',
    '"phase7-cmdline-test"',
    '"phase7-cmdline-survey"',
    '"phase7-argv-split-test"',
    '"phase7-argv-split-survey"',
    '"phase7-rbtree-test"',
    '"phase7-rbtree-survey"',
    'test_step.dependOn(&run_string_helpers_tests.step);',
    'test_step.dependOn(&run_string_helpers_survey_tests.step);',
    'test_step.dependOn(&run_string_helpers_sample_boundary_tests.step);',
    'test_step.dependOn(&run_cmdline_tests.step);',
    'test_step.dependOn(&run_cmdline_survey_tests.step);',
    'test_step.dependOn(&run_argv_split_tests.step);',
    'test_step.dependOn(&run_argv_split_survey_tests.step);',
    'test_step.dependOn(&run_rbtree_tests.step);',
    'test_step.dependOn(&run_rbtree_survey_tests.step);',
]

MAKEFILE_MARKERS = [
    "PHONY += phase7-validate phase7-string-helpers-test phase7-string-helpers-survey phase7-string-helpers-sample-boundary phase7-cmdline-test phase7-cmdline-survey phase7-argv-split-test phase7-argv-split-survey phase7-rbtree-test phase7-rbtree-survey phase7-test phase7",
    "phase7-string-helpers-test:",
    "phase7-string-helpers-survey:",
    "phase7-string-helpers-sample-boundary:",
    "phase7-cmdline-test:",
    "phase7-cmdline-survey:",
    "phase7-argv-split-test:",
    "phase7-argv-split-survey:",
    "phase7-rbtree-test:",
    "phase7-rbtree-survey:",
    "phase7-test:",
    "phase7: phase7-validate phase7-test",
]

REQUIRED_FILES = (BUILD_PATH, MAKEFILE_PATH)
REQUIRED_MARKERS = {
    BUILD_PATH: BUILD_MARKERS,
    MAKEFILE_PATH: MAKEFILE_MARKERS,
}


def _read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files: list[str] = []
    missing_markers: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            missing_files.append(str(rel))

    if missing_files:
        return missing_files, missing_markers

    for rel, markers in REQUIRED_MARKERS.items():
        text = _read_text(root, rel)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{rel}: {marker}")

    return missing_files, missing_markers


def _write_fixture_root(root: Path) -> None:
    for rel, markers in REQUIRED_MARKERS.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(markers) + "\n", encoding="utf-8")


def _mutate_marker(root: Path, rel: Path, old: str, new: str, case: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    updated = text.replace(old, new, 1)
    assert updated != text, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [(f"missing_{rel.name}", rel) for rel in REQUIRED_FILES]
    marker_cases = [
        ("phony_packet_drift", MAKEFILE_PATH, MAKEFILE_MARKERS[0], "PHONY += phase7-validate phase7-string-helpers-survey phase7-string-helpers-sample-boundary phase7-cmdline-survey phase7-argv-split-survey phase7-rbtree-survey phase7-test phase7"),
        ("string_helpers_direct_route_drift", MAKEFILE_PATH, "phase7-string-helpers-test:", "phase7-string-helpers-check:"),
        ("cmdline_direct_route_drift", MAKEFILE_PATH, "phase7-cmdline-test:", "phase7-cmdline-check:"),
        ("argv_split_direct_route_drift", MAKEFILE_PATH, "phase7-argv-split-test:", "phase7-argv-split-check:"),
        ("rbtree_direct_route_drift", MAKEFILE_PATH, "phase7-rbtree-test:", "phase7-rbtree-check:"),
        ("build_root_string_helpers_drift", BUILD_PATH, '"../../lib/string_helpers.zig"', '"../../tools/lib/string_helpers.zig"'),
        ("build_root_cmdline_drift", BUILD_PATH, '"../../lib/cmdline.zig"', '"../../tools/lib/cmdline.zig"'),
        ("build_root_argv_split_drift", BUILD_PATH, '"../../lib/argv_split.zig"', '"../../tools/lib/argv_split.zig"'),
        ("build_root_rbtree_drift", BUILD_PATH, '"../../lib/rbtree.zig"', '"../../tools/lib/rbtree.zig"'),
        ("stale_shared_build_fallback", BUILD_PATH, '"phase7-rbtree-survey"', '"zigux/tests/build.zig"'),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_build_wiring_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        _write_fixture_root(root)
        assert validate(root) == ([], [])

        for case, rel in missing_file_cases:
            (root / rel).unlink()
            assert validate(root) == ([str(rel)], []), case
            _write_fixture_root(root)

        for case, rel, old, new in marker_cases:
            _mutate_marker(root, rel, old, new, case)
            assert validate(root) == ([], [f"{rel}: {old}"]), case
            _write_fixture_root(root)

    print("PHASE7_BUILD_WIRING=pass")
    print(
        "PHASE7_BUILD_WIRING_CASE_COUNT=%d"
        % (len(missing_file_cases) + len(marker_cases))
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shipped Phase 7 build graph and Makefile wiring stay aligned."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-tests without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(Path("."))
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
    print(
        "PHASE7_BUILD_WIRING_MARKER_COUNT=%d"
        % sum(len(markers) for markers in REQUIRED_MARKERS.values())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
