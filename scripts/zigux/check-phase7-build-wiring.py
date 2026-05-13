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
        "PHONY += phase7-validate phase7-string-helpers-survey phase7-string-helpers-sample-boundary phase7-cmdline-survey phase7-argv-split-survey phase7-rbtree-survey phase7-test phase7",
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
        ".root_source_file = b.path(\"../../lib/string_helpers.zig\"),",
        ".root_source_file = b.path(\"phase7_string_helpers.zig\"),",
        "string_helpers_root_module.addImport(\"string_helpers\", string_helpers_module);",
        "const string_helpers_survey_step = b.step(",
        "\"phase7-string-helpers-survey\",",
        "\"Run the Phase 7 string helpers survey replay\",",
        "string_helpers_survey_step.dependOn(&run_string_helpers_survey_tests.step);",
        "phase7-string-helpers-survey-tests",
        "\"phase7_string_helpers_survey.zig\"",
        "const string_helpers_sample_boundary_step = b.step(",
        "\"phase7-string-helpers-sample-boundary\",",
        "\"Run the Phase 7 string helpers sample-boundary replay\",",
        "string_helpers_sample_boundary_step.dependOn(&run_string_helpers_sample_boundary_tests.step);",
        "phase7-string-helpers-sample-boundary-tests",
        "\"phase7_string_helpers_sample_boundary.zig\"",
        ".root_source_file = b.path(\"../../lib/cmdline.zig\"),",
        ".root_source_file = b.path(\"phase7_cmdline.zig\"),",
        "cmdline_root_module.addImport(\"cmdline\", cmdline_module);",
        "const cmdline_step = b.step(",
        "\"phase7-cmdline-test\",",
        "\"Run the Phase 7 cmdline helper tests\",",
        "cmdline_step.dependOn(&run_cmdline_tests.step);",
        "const cmdline_survey_step = b.step(",
        "\"phase7-cmdline-survey\",",
        "\"Run the Phase 7 cmdline survey replay\",",
        "cmdline_survey_step.dependOn(&run_cmdline_survey_tests.step);",
        "phase7-cmdline-survey-tests",
        "\"phase7_cmdline_survey.zig\"",
        ".root_source_file = b.path(\"../../lib/argv_split.zig\"),",
        ".root_source_file = b.path(\"phase7_argv_split.zig\"),",
        "argv_split_root_module.addImport(\"argv_split\", argv_split_module);",
        "const argv_split_step = b.step(",
        "\"phase7-argv-split-test\",",
        "\"Run the Phase 7 argv split helper tests\",",
        "argv_split_step.dependOn(&run_argv_split_tests.step);",
        "const argv_split_survey_step = b.step(",
        "\"phase7-argv-split-survey\",",
        "\"Run the Phase 7 argv split survey replay\",",
        "argv_split_survey_step.dependOn(&run_argv_split_survey_tests.step);",
        "phase7-argv-split-survey-tests",
        "\"phase7_argv_split_survey.zig\"",
        ".root_source_file = b.path(\"../../lib/rbtree.zig\"),",
        ".root_source_file = b.path(\"phase7_rbtree.zig\"),",
        "rbtree_root_module.addImport(\"rbtree\", rbtree_module);",
        "const rbtree_step = b.step(",
        "\"phase7-rbtree-test\",",
        "\"Run the Phase 7 rbtree helper tests\",",
        "rbtree_step.dependOn(&run_rbtree_tests.step);",
        "const rbtree_survey_step = b.step(",
        "\"phase7-rbtree-survey\",",
        "\"Run the Phase 7 rbtree survey replay\",",
        "rbtree_survey_step.dependOn(&run_rbtree_survey_tests.step);",
        "phase7-rbtree-survey-tests",
        "\"phase7_rbtree_survey.zig\"",
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
            "docs_readme_tests_readme_marker",
            "Documentation/zigux/README.md",
            "zigux/tests/README.md",
            "",
            "Documentation/zigux/README.md: zigux/tests/README.md",
        ),
        (
            "docs_readme_string_helpers_test_marker",
            "Documentation/zigux/README.md",
            "zigux/tests/phase7_string_helpers.zig",
            "",
            "Documentation/zigux/README.md: zigux/tests/phase7_string_helpers.zig",
        ),
        (
            "docs_readme_string_helpers_survey_marker",
            "Documentation/zigux/README.md",
            "zigux/tests/phase7_string_helpers_survey.zig",
            "",
            "Documentation/zigux/README.md: zigux/tests/phase7_string_helpers_survey.zig",
        ),
        (
            "docs_readme_string_helpers_sample_boundary_marker",
            "Documentation/zigux/README.md",
            "zigux/tests/phase7_string_helpers_sample_boundary.zig",
            "",
            "Documentation/zigux/README.md: zigux/tests/phase7_string_helpers_sample_boundary.zig",
        ),
        (
            "docs_readme_cmdline_test_marker",
            "Documentation/zigux/README.md",
            "zigux/tests/phase7_cmdline.zig",
            "",
            "Documentation/zigux/README.md: zigux/tests/phase7_cmdline.zig",
        ),
        (
            "docs_readme_cmdline_survey_marker",
            "Documentation/zigux/README.md",
            "zigux/tests/phase7_cmdline_survey.zig",
            "",
            "Documentation/zigux/README.md: zigux/tests/phase7_cmdline_survey.zig",
        ),
        (
            "docs_readme_argv_split_test_marker",
            "Documentation/zigux/README.md",
            "zigux/tests/phase7_argv_split.zig",
            "",
            "Documentation/zigux/README.md: zigux/tests/phase7_argv_split.zig",
        ),
        (
            "docs_readme_argv_split_survey_marker",
            "Documentation/zigux/README.md",
            "zigux/tests/phase7_argv_split_survey.zig",
            "",
            "Documentation/zigux/README.md: zigux/tests/phase7_argv_split_survey.zig",
        ),
        (
            "docs_readme_rbtree_test_marker",
            "Documentation/zigux/README.md",
            "zigux/tests/phase7_rbtree.zig",
            "",
            "Documentation/zigux/README.md: zigux/tests/phase7_rbtree.zig",
        ),
        (
            "docs_readme_rbtree_survey_marker",
            "Documentation/zigux/README.md",
            "zigux/tests/phase7_rbtree_survey.zig",
            "",
            "Documentation/zigux/README.md: zigux/tests/phase7_rbtree_survey.zig",
        ),
        (
            "tests_readme_argv_split_survey_marker",
            "zigux/tests/README.md",
            "zigux/tests/phase7_argv_split_survey.zig",
            "",
            "zigux/tests/README.md: zigux/tests/phase7_argv_split_survey.zig",
        ),
        (
            "build_string_helpers_root_source_path",
            "zigux/tests/phase7_build.zig",
            ".root_source_file = b.path(\"../../lib/string_helpers.zig\"),",
            ".root_source_file = b.path(\"../../lib/string_helpers_drift.zig\"),",
            "zigux/tests/phase7_build.zig: .root_source_file = b.path(\"../../lib/string_helpers.zig\"),",
        ),
        (
            "build_string_helpers_direct_source_path",
            "zigux/tests/phase7_build.zig",
            ".root_source_file = b.path(\"phase7_string_helpers.zig\"),",
            ".root_source_file = b.path(\"phase7_string_helpers_drift.zig\"),",
            "zigux/tests/phase7_build.zig: .root_source_file = b.path(\"phase7_string_helpers.zig\"),",
        ),
        (
            "build_string_helpers_import_alias",
            "zigux/tests/phase7_build.zig",
            "string_helpers_root_module.addImport(\"string_helpers\", string_helpers_module);",
            "",
            "zigux/tests/phase7_build.zig: string_helpers_root_module.addImport(\"string_helpers\", string_helpers_module);",
        ),
        (
            "build_string_helpers_survey_step_name",
            "zigux/tests/phase7_build.zig",
            "\"phase7-string-helpers-survey\",",
            "\"phase7-string-helpers-survey-drift\",",
            "zigux/tests/phase7_build.zig: \"phase7-string-helpers-survey\",",
        ),
        (
            "build_string_helpers_survey_step_dependson",
            "zigux/tests/phase7_build.zig",
            "string_helpers_survey_step.dependOn(&run_string_helpers_survey_tests.step);",
            "string_helpers_survey_step.dependOn(&run_string_helpers_tests.step);",
            "zigux/tests/phase7_build.zig: string_helpers_survey_step.dependOn(&run_string_helpers_survey_tests.step);",
        ),
        (
            "build_string_helpers_survey_cwd",
            "zigux/tests/phase7_build.zig",
            "run_string_helpers_survey_tests.setCwd(b.path(\"../..\"));",
            "",
            "zigux/tests/phase7_build.zig: run_string_helpers_survey_tests.setCwd(b.path(\"../..\"));",
        ),
        (
            "build_string_helpers_sample_boundary_step_name",
            "zigux/tests/phase7_build.zig",
            "\"phase7-string-helpers-sample-boundary\",",
            "\"phase7-string-helpers-sample-boundary-drift\",",
            "zigux/tests/phase7_build.zig: \"phase7-string-helpers-sample-boundary\",",
        ),
        (
            "build_string_helpers_sample_boundary_step_dependson",
            "zigux/tests/phase7_build.zig",
            "string_helpers_sample_boundary_step.dependOn(&run_string_helpers_sample_boundary_tests.step);",
            "string_helpers_sample_boundary_step.dependOn(&run_string_helpers_survey_tests.step);",
            "zigux/tests/phase7_build.zig: string_helpers_sample_boundary_step.dependOn(&run_string_helpers_sample_boundary_tests.step);",
        ),
        (
            "build_cmdline_root_source_path",
            "zigux/tests/phase7_build.zig",
            ".root_source_file = b.path(\"../../lib/cmdline.zig\"),",
            ".root_source_file = b.path(\"../../lib/cmdline_drift.zig\"),",
            "zigux/tests/phase7_build.zig: .root_source_file = b.path(\"../../lib/cmdline.zig\"),",
        ),
        (
            "build_cmdline_direct_source_path",
            "zigux/tests/phase7_build.zig",
            ".root_source_file = b.path(\"phase7_cmdline.zig\"),",
            ".root_source_file = b.path(\"phase7_cmdline_drift.zig\"),",
            "zigux/tests/phase7_build.zig: .root_source_file = b.path(\"phase7_cmdline.zig\"),",
        ),
        (
            "build_cmdline_import_alias",
            "zigux/tests/phase7_build.zig",
            "cmdline_root_module.addImport(\"cmdline\", cmdline_module);",
            "",
            "zigux/tests/phase7_build.zig: cmdline_root_module.addImport(\"cmdline\", cmdline_module);",
        ),
        (
            "build_cmdline_direct_step_name",
            "zigux/tests/phase7_build.zig",
            "\"phase7-cmdline-test\",",
            "\"phase7-cmdline-drift-test\",",
            "zigux/tests/phase7_build.zig: \"phase7-cmdline-test\",",
        ),
        (
            "build_cmdline_direct_step_dependson",
            "zigux/tests/phase7_build.zig",
            "cmdline_step.dependOn(&run_cmdline_tests.step);",
            "",
            "zigux/tests/phase7_build.zig: cmdline_step.dependOn(&run_cmdline_tests.step);",
        ),
        (
            "build_cmdline_survey_step_name",
            "zigux/tests/phase7_build.zig",
            "\"phase7-cmdline-survey\",",
            "\"phase7-cmdline-survey-drift\",",
            "zigux/tests/phase7_build.zig: \"phase7-cmdline-survey\",",
        ),
        (
            "build_cmdline_survey_step_dependson",
            "zigux/tests/phase7_build.zig",
            "cmdline_survey_step.dependOn(&run_cmdline_survey_tests.step);",
            "cmdline_survey_step.dependOn(&run_cmdline_tests.step);",
            "zigux/tests/phase7_build.zig: cmdline_survey_step.dependOn(&run_cmdline_survey_tests.step);",
        ),
        (
            "build_cmdline_survey_gate",
            "zigux/tests/phase7_build.zig",
            "phase7-cmdline-survey-tests",
            "",
            "zigux/tests/phase7_build.zig: phase7-cmdline-survey-tests",
        ),
        (
            "build_argv_split_root_source_path",
            "zigux/tests/phase7_build.zig",
            ".root_source_file = b.path(\"../../lib/argv_split.zig\"),",
            ".root_source_file = b.path(\"../../lib/argv_split_drift.zig\"),",
            "zigux/tests/phase7_build.zig: .root_source_file = b.path(\"../../lib/argv_split.zig\"),",
        ),
        (
            "build_argv_split_direct_source_path",
            "zigux/tests/phase7_build.zig",
            ".root_source_file = b.path(\"phase7_argv_split.zig\"),",
            ".root_source_file = b.path(\"phase7_argv_split_drift.zig\"),",
            "zigux/tests/phase7_build.zig: .root_source_file = b.path(\"phase7_argv_split.zig\"),",
        ),
        (
            "build_argv_split_import_alias",
            "zigux/tests/phase7_build.zig",
            "argv_split_root_module.addImport(\"argv_split\", argv_split_module);",
            "",
            "zigux/tests/phase7_build.zig: argv_split_root_module.addImport(\"argv_split\", argv_split_module);",
        ),
        (
            "build_argv_split_direct_step_name",
            "zigux/tests/phase7_build.zig",
            "\"phase7-argv-split-test\",",
            "\"phase7-argv-split-drift-test\",",
            "zigux/tests/phase7_build.zig: \"phase7-argv-split-test\",",
        ),
        (
            "build_argv_split_direct_step_dependson",
            "zigux/tests/phase7_build.zig",
            "argv_split_step.dependOn(&run_argv_split_tests.step);",
            "",
            "zigux/tests/phase7_build.zig: argv_split_step.dependOn(&run_argv_split_tests.step);",
        ),
        (
            "build_argv_split_survey_step_name",
            "zigux/tests/phase7_build.zig",
            "\"phase7-argv-split-survey\",",
            "\"phase7-argv-split-survey-drift\",",
            "zigux/tests/phase7_build.zig: \"phase7-argv-split-survey\",",
        ),
        (
            "build_argv_split_survey_step_dependson",
            "zigux/tests/phase7_build.zig",
            "argv_split_survey_step.dependOn(&run_argv_split_survey_tests.step);",
            "argv_split_survey_step.dependOn(&run_argv_split_tests.step);",
            "zigux/tests/phase7_build.zig: argv_split_survey_step.dependOn(&run_argv_split_survey_tests.step);",
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
            "build_rbtree_root_source_path",
            "zigux/tests/phase7_build.zig",
            ".root_source_file = b.path(\"../../lib/rbtree.zig\"),",
            ".root_source_file = b.path(\"../../lib/rbtree_drift.zig\"),",
            "zigux/tests/phase7_build.zig: .root_source_file = b.path(\"../../lib/rbtree.zig\"),",
        ),
        (
            "build_rbtree_direct_source_path",
            "zigux/tests/phase7_build.zig",
            ".root_source_file = b.path(\"phase7_rbtree.zig\"),",
            ".root_source_file = b.path(\"phase7_rbtree_drift.zig\"),",
            "zigux/tests/phase7_build.zig: .root_source_file = b.path(\"phase7_rbtree.zig\"),",
        ),
        (
            "build_rbtree_import_alias",
            "zigux/tests/phase7_build.zig",
            "rbtree_root_module.addImport(\"rbtree\", rbtree_module);",
            "",
            "zigux/tests/phase7_build.zig: rbtree_root_module.addImport(\"rbtree\", rbtree_module);",
        ),
        (
            "build_rbtree_direct_step_name",
            "zigux/tests/phase7_build.zig",
            "\"phase7-rbtree-test\",",
            "\"phase7-rbtree-drift-test\",",
            "zigux/tests/phase7_build.zig: \"phase7-rbtree-test\",",
        ),
        (
            "build_rbtree_direct_step_dependson",
            "zigux/tests/phase7_build.zig",
            "rbtree_step.dependOn(&run_rbtree_tests.step);",
            "",
            "zigux/tests/phase7_build.zig: rbtree_step.dependOn(&run_rbtree_tests.step);",
        ),
        (
            "build_rbtree_survey_step_name",
            "zigux/tests/phase7_build.zig",
            "\"phase7-rbtree-survey\",",
            "\"phase7-rbtree-survey-drift\",",
            "zigux/tests/phase7_build.zig: \"phase7-rbtree-survey\",",
        ),
        (
            "build_rbtree_survey_step_dependson",
            "zigux/tests/phase7_build.zig",
            "rbtree_survey_step.dependOn(&run_rbtree_survey_tests.step);",
            "rbtree_survey_step.dependOn(&run_rbtree_tests.step);",
            "zigux/tests/phase7_build.zig: rbtree_survey_step.dependOn(&run_rbtree_survey_tests.step);",
        ),
        (
            "build_rbtree_survey_gate",
            "zigux/tests/phase7_build.zig",
            "phase7-rbtree-survey-tests",
            "",
            "zigux/tests/phase7_build.zig: phase7-rbtree-survey-tests",
        ),
        (
            "build_shared_test_step",
            "zigux/tests/phase7_build.zig",
            "const test_step = b.step(\"test\", \"Run Phase 7 runtime helper tests\");",
            "",
            "zigux/tests/phase7_build.zig: const test_step = b.step(\"test\", \"Run Phase 7 runtime helper tests\");",
        ),
        (
            "build_test_depends_on_string_helpers",
            "zigux/tests/phase7_build.zig",
            "test_step.dependOn(&run_string_helpers_tests.step);",
            "",
            "zigux/tests/phase7_build.zig: test_step.dependOn(&run_string_helpers_tests.step);",
        ),
        (
            "build_test_depends_on_string_helpers_survey",
            "zigux/tests/phase7_build.zig",
            "test_step.dependOn(&run_string_helpers_survey_tests.step);",
            "",
            "zigux/tests/phase7_build.zig: test_step.dependOn(&run_string_helpers_survey_tests.step);",
        ),
        (
            "build_test_depends_on_string_helpers_sample_boundary",
            "zigux/tests/phase7_build.zig",
            "test_step.dependOn(&run_string_helpers_sample_boundary_tests.step);",
            "",
            "zigux/tests/phase7_build.zig: test_step.dependOn(&run_string_helpers_sample_boundary_tests.step);",
        ),
        (
            "build_test_depends_on_cmdline",
            "zigux/tests/phase7_build.zig",
            "test_step.dependOn(&run_cmdline_tests.step);",
            "",
            "zigux/tests/phase7_build.zig: test_step.dependOn(&run_cmdline_tests.step);",
        ),
        (
            "build_test_depends_on_cmdline_survey",
            "zigux/tests/phase7_build.zig",
            "test_step.dependOn(&run_cmdline_survey_tests.step);",
            "",
            "zigux/tests/phase7_build.zig: test_step.dependOn(&run_cmdline_survey_tests.step);",
        ),
        (
            "build_test_depends_on_argv_split",
            "zigux/tests/phase7_build.zig",
            "test_step.dependOn(&run_argv_split_tests.step);",
            "",
            "zigux/tests/phase7_build.zig: test_step.dependOn(&run_argv_split_tests.step);",
        ),
        (
            "build_test_depends_on_argv_split_survey",
            "zigux/tests/phase7_build.zig",
            "test_step.dependOn(&run_argv_split_survey_tests.step);",
            "",
            "zigux/tests/phase7_build.zig: test_step.dependOn(&run_argv_split_survey_tests.step);",
        ),
        (
            "build_test_depends_on_rbtree",
            "zigux/tests/phase7_build.zig",
            "test_step.dependOn(&run_rbtree_tests.step);",
            "",
            "zigux/tests/phase7_build.zig: test_step.dependOn(&run_rbtree_tests.step);",
        ),
        (
            "build_test_depends_on_rbtree_survey",
            "zigux/tests/phase7_build.zig",
            "test_step.dependOn(&run_rbtree_survey_tests.step);",
            "",
            "zigux/tests/phase7_build.zig: test_step.dependOn(&run_rbtree_survey_tests.step);",
        ),
        (
            "scripts_readme_string_helpers_survey_route",
            "scripts/zigux/README.md",
            "make -C zigux phase7-string-helpers-survey",
            "",
            "scripts/zigux/README.md: make -C zigux phase7-string-helpers-survey",
        ),
        (
            "scripts_readme_string_helpers_sample_boundary_route",
            "scripts/zigux/README.md",
            "make -C zigux phase7-string-helpers-sample-boundary",
            "",
            "scripts/zigux/README.md: make -C zigux phase7-string-helpers-sample-boundary",
        ),
        (
            "scripts_readme_cmdline_survey_route",
            "scripts/zigux/README.md",
            "make -C zigux phase7-cmdline-survey",
            "",
            "scripts/zigux/README.md: make -C zigux phase7-cmdline-survey",
        ),
        (
            "scripts_readme_argv_split_survey_route",
            "scripts/zigux/README.md",
            "make -C zigux phase7-argv-split-survey",
            "",
            "scripts/zigux/README.md: make -C zigux phase7-argv-split-survey",
        ),
        (
            "scripts_readme_rbtree_survey_route",
            "scripts/zigux/README.md",
            "make -C zigux phase7-rbtree-survey",
            "",
            "scripts/zigux/README.md: make -C zigux phase7-rbtree-survey",
        ),
        (
            "makefile_phase7_phony_packet",
            "zigux/Makefile",
            "PHONY += phase7-validate phase7-string-helpers-survey phase7-string-helpers-sample-boundary phase7-cmdline-survey phase7-argv-split-survey phase7-rbtree-survey phase7-test phase7",
            "PHONY += phase7-validate phase7-string-helpers-survey phase7-string-helpers-sample-boundary phase7-cmdline-survey phase7-argv-split-survey phase7-rbtree-survey phase7",
            "zigux/Makefile: PHONY += phase7-validate phase7-string-helpers-survey phase7-string-helpers-sample-boundary phase7-cmdline-survey phase7-argv-split-survey phase7-rbtree-survey phase7-test phase7",
        ),
        (
            "makefile_string_helpers_survey_route",
            "zigux/Makefile",
            "phase7-string-helpers-survey:",
            "",
            "zigux/Makefile: phase7-string-helpers-survey:",
        ),
        (
            "makefile_string_helpers_sample_boundary_route",
            "zigux/Makefile",
            "phase7-string-helpers-sample-boundary:",
            "",
            "zigux/Makefile: phase7-string-helpers-sample-boundary:",
        ),
        (
            "makefile_cmdline_survey_route",
            "zigux/Makefile",
            "phase7-cmdline-survey:",
            "",
            "zigux/Makefile: phase7-cmdline-survey:",
        ),
        (
            "makefile_argv_split_survey_route",
            "zigux/Makefile",
            "phase7-argv-split-survey:",
            "",
            "zigux/Makefile: phase7-argv-split-survey:",
        ),
        (
            "makefile_rbtree_survey_route",
            "zigux/Makefile",
            "phase7-rbtree-survey:",
            "",
            "zigux/Makefile: phase7-rbtree-survey:",
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
