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
        "zigux/tests/README.md",
        "zigux/tests/phase7_build.zig",
        "zigux/tests/phase7_string_helpers.zig",
        "zigux/tests/phase7_string_helpers_survey.zig",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        "zigux/tests/phase7_cmdline.zig",
        "zigux/tests/phase7_cmdline_survey.zig",
        "zigux/tests/phase7_argv_split.zig",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_rbtree.zig",
        "zigux/tests/phase7_rbtree_survey.zig",
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
        "scripts/zigux/check-phase7-cmdline-packet.py",
        "zigux/tests/phase7_build.zig",
        "make -C zigux phase7-string-helpers-survey",
        "make -C zigux phase7-string-helpers-sample-boundary",
        "make -C zigux phase7-cmdline-survey",
        "make -C zigux phase7-argv-split-survey",
        "make -C zigux phase7-rbtree-survey",
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
        "scripts/zigux/check-phase7-build-wiring.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py",
    ],
    "zigux/tests/phase7_build.zig": [
        "fn createStandaloneRootModule(",
        "fn createImportedRootModule(",
        "const helper_module = createStandaloneRootModule(b, target, optimize, helper_source_file);",
        "const root_module = createStandaloneRootModule(b, target, optimize, root_source_file);",
        "root_module.addImport(import_name, helper_module);",
        "const string_helpers_root_module = createImportedRootModule(",
        "\"../../lib/string_helpers.zig\",",
        "\"phase7_string_helpers.zig\",",
        "\"string_helpers\",",
        "const string_helpers_step = b.step(",
        "\"phase7-string-helpers-test\",",
        "\"Run the Phase 7 string helpers tests\",",
        "string_helpers_step.dependOn(&run_string_helpers_tests.step);",
        "phase7-string-helpers-tests",
        "const string_helpers_survey_root_module = createStandaloneRootModule(",
        "\"phase7_string_helpers_survey.zig\",",
        "const string_helpers_survey_step = b.step(",
        "\"phase7-string-helpers-survey\",",
        "\"Run the Phase 7 string helpers survey replay\",",
        "string_helpers_survey_step.dependOn(&run_string_helpers_survey_tests.step);",
        "phase7-string-helpers-survey-tests",
        "const string_helpers_sample_boundary_root_module = createStandaloneRootModule(",
        "\"phase7_string_helpers_sample_boundary.zig\",",
        "const string_helpers_sample_boundary_step = b.step(",
        "\"phase7-string-helpers-sample-boundary\",",
        "\"Run the Phase 7 string helpers sample-boundary replay\",",
        "string_helpers_sample_boundary_step.dependOn(&run_string_helpers_sample_boundary_tests.step);",
        "phase7-string-helpers-sample-boundary-tests",
        "const cmdline_root_module = createImportedRootModule(",
        "\"../../lib/cmdline.zig\",",
        "\"phase7_cmdline.zig\",",
        "\"cmdline\",",
        "const cmdline_step = b.step(",
        "\"phase7-cmdline-test\",",
        "\"Run the Phase 7 cmdline helper tests\",",
        "cmdline_step.dependOn(&run_cmdline_tests.step);",
        "const cmdline_survey_root_module = createStandaloneRootModule(",
        "\"phase7_cmdline_survey.zig\",",
        "const cmdline_survey_step = b.step(",
        "\"phase7-cmdline-survey\",",
        "\"Run the Phase 7 cmdline survey replay\",",
        "cmdline_survey_step.dependOn(&run_cmdline_survey_tests.step);",
        "phase7-cmdline-survey-tests",
        "const argv_split_root_module = createImportedRootModule(",
        "\"../../lib/argv_split.zig\",",
        "\"phase7_argv_split.zig\",",
        "\"argv_split\",",
        "const argv_split_step = b.step(",
        "\"phase7-argv-split-test\",",
        "\"Run the Phase 7 argv split helper tests\",",
        "argv_split_step.dependOn(&run_argv_split_tests.step);",
        "const argv_split_survey_root_module = createStandaloneRootModule(",
        "\"phase7_argv_split_survey.zig\",",
        "const argv_split_survey_step = b.step(",
        "\"phase7-argv-split-survey\",",
        "\"Run the Phase 7 argv split survey replay\",",
        "argv_split_survey_step.dependOn(&run_argv_split_survey_tests.step);",
        "phase7-argv-split-survey-tests",
        "const rbtree_root_module = createImportedRootModule(",
        "\"../../lib/rbtree.zig\",",
        "\"phase7_rbtree.zig\",",
        "\"rbtree\",",
        "const rbtree_step = b.step(",
        "\"phase7-rbtree-test\",",
        "\"Run the Phase 7 rbtree helper tests\",",
        "rbtree_step.dependOn(&run_rbtree_tests.step);",
        "const rbtree_survey_root_module = createStandaloneRootModule(",
        "\"phase7_rbtree_survey.zig\",",
        "const rbtree_survey_step = b.step(",
        "\"phase7-rbtree-survey\",",
        "\"Run the Phase 7 rbtree survey replay\",",
        "rbtree_survey_step.dependOn(&run_rbtree_survey_tests.step);",
        "phase7-rbtree-survey-tests",
        "run_string_helpers_survey_tests.setCwd(b.path(\"../..\"));",
        "run_string_helpers_sample_boundary_tests.setCwd(b.path(\"../..\"));",
        "run_cmdline_survey_tests.setCwd(b.path(\"../..\"));",
        "run_argv_split_survey_tests.setCwd(b.path(\"../..\"));",
        "run_rbtree_survey_tests.setCwd(b.path(\"../..\"));",
        "const test_step = b.step(\"test\", \"Run Phase 7 runtime helper tests\");",
        "test_step.dependOn(&run_string_helpers_tests.step);",
        "test_step.dependOn(&run_string_helpers_survey_tests.step);",
        "test_step.dependOn(&run_string_helpers_sample_boundary_tests.step);",
        "test_step.dependOn(&run_cmdline_tests.step);",
        "test_step.dependOn(&run_cmdline_survey_tests.step);",
        "test_step.dependOn(&run_argv_split_tests.step);",
        "test_step.dependOn(&run_argv_split_survey_tests.step);",
        "test_step.dependOn(&run_rbtree_tests.step);",
        "test_step.dependOn(&run_rbtree_survey_tests.step);",
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
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        markers = REQUIRED_MARKERS.get(rel, ["# fixture"])
        path.write_text("\n".join(markers) + "\n", encoding="utf-8")


def run_self_test() -> None:
    cases = [
        ("missing_checker", "scripts/zigux/check-phase7-build-wiring.py", None, "scripts/zigux/check-phase7-build-wiring.py"),
        ("missing_build_file", "zigux/tests/phase7_build.zig", None, "zigux/tests/phase7_build.zig"),
        (
            "missing_helper_def",
            "zigux/tests/phase7_build.zig",
            "fn createImportedRootModule(",
            "zigux/tests/phase7_build.zig: fn createImportedRootModule(",
        ),
        (
            "missing_string_helpers_imported_call",
            "zigux/tests/phase7_build.zig",
            "const string_helpers_root_module = createImportedRootModule(",
            "zigux/tests/phase7_build.zig: const string_helpers_root_module = createImportedRootModule(",
        ),
        (
            "missing_string_helpers_import_name",
            "zigux/tests/phase7_build.zig",
            "\"string_helpers\",",
            "zigux/tests/phase7_build.zig: \"string_helpers\",",
        ),
        (
            "missing_string_helpers_sample_boundary_call",
            "zigux/tests/phase7_build.zig",
            "const string_helpers_sample_boundary_root_module = createStandaloneRootModule(",
            "zigux/tests/phase7_build.zig: const string_helpers_sample_boundary_root_module = createStandaloneRootModule(",
        ),
        (
            "missing_string_helpers_sample_boundary_step_name",
            "zigux/tests/phase7_build.zig",
            "\"phase7-string-helpers-sample-boundary\",",
            "zigux/tests/phase7_build.zig: \"phase7-string-helpers-sample-boundary\",",
        ),
        (
            "missing_cmdline_root_call",
            "zigux/tests/phase7_build.zig",
            "const cmdline_root_module = createImportedRootModule(",
            "zigux/tests/phase7_build.zig: const cmdline_root_module = createImportedRootModule(",
        ),
        (
            "missing_cmdline_survey_dependency",
            "zigux/tests/phase7_build.zig",
            "cmdline_survey_step.dependOn(&run_cmdline_survey_tests.step);",
            "zigux/tests/phase7_build.zig: cmdline_survey_step.dependOn(&run_cmdline_survey_tests.step);",
        ),
        (
            "missing_argv_split_survey_cwd",
            "zigux/tests/phase7_build.zig",
            "run_argv_split_survey_tests.setCwd(b.path(\"../..\"));",
            "zigux/tests/phase7_build.zig: run_argv_split_survey_tests.setCwd(b.path(\"../..\"));",
        ),
        (
            "missing_rbtree_shared_dependency",
            "zigux/tests/phase7_build.zig",
            "test_step.dependOn(&run_rbtree_survey_tests.step);",
            "zigux/tests/phase7_build.zig: test_step.dependOn(&run_rbtree_survey_tests.step);",
        ),
        (
            "missing_docs_marker",
            "Documentation/zigux/README.md",
            "zigux/tests/phase7_build.zig",
            "Documentation/zigux/README.md: zigux/tests/phase7_build.zig",
        ),
        (
            "missing_scripts_cmdline_checker_marker",
            "scripts/zigux/README.md",
            "scripts/zigux/check-phase7-cmdline-packet.py",
            "scripts/zigux/README.md: scripts/zigux/check-phase7-cmdline-packet.py",
        ),
        (
            "missing_scripts_route",
            "scripts/zigux/README.md",
            "make -C zigux phase7-rbtree-survey",
            "scripts/zigux/README.md: make -C zigux phase7-rbtree-survey",
        ),
        (
            "missing_makefile_route",
            "zigux/Makefile",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py",
            "zigux/Makefile: cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_build_wiring_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        for case, rel, marker, expected in cases:
            path = tmp_root / rel
            if marker is None:
                path.unlink()
                assert validate(tmp_root) == ([expected], []), case
            else:
                text = path.read_text(encoding="utf-8")
                updated = text.replace(marker, "", 1)
                assert updated != text, case
                path.write_text(updated, encoding="utf-8")
                assert validate(tmp_root) == ([], [expected]), case
            write_fixture_root(tmp_root)

    print("PHASE7_BUILD_WIRING=pass")
    print(f"PHASE7_BUILD_WIRING_CASE_COUNT={len(cases)}")


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