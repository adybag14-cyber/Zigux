#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent
TARGET = ROOT / "zigux/tests/phase7_build.zig"
MAKEFILE = ROOT / "zigux/Makefile"

HELPER_SPECS = [
    {
        "key": "string_helpers",
        "helper_path": '"../../lib/string_helpers.zig"',
        "helper_module_marker": """const string_helpers_module = b.createModule(.{
        .root_source_file = b.path("../../lib/string_helpers.zig"),
        .target = target,
        .optimize = optimize,
    });""",
        "root_path": '"phase7_string_helpers.zig"',
        "root_module_marker": """const string_helpers_root_module = b.createModule(.{
        .root_source_file = b.path("phase7_string_helpers.zig"),
        .target = target,
        .optimize = optimize,
    });""",
        "import_marker": 'string_helpers_root_module.addImport("string_helpers", string_helpers_module);',
        "test_name_marker": '.name = "phase7-string-helpers-tests",',
        "depend_marker": "test_step.dependOn(&run_string_helpers_tests.step);",
    },
    {
        "key": "cmdline",
        "helper_path": '"../../lib/cmdline.zig"',
        "helper_module_marker": """const cmdline_module = b.createModule(.{
        .root_source_file = b.path("../../lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });""",
        "root_path": '"phase7_cmdline.zig"',
        "root_module_marker": """const cmdline_root_module = b.createModule(.{
        .root_source_file = b.path("phase7_cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });""",
        "import_marker": 'cmdline_root_module.addImport("cmdline", cmdline_module);',
        "test_name_marker": '.name = "phase7-cmdline-tests",',
        "depend_marker": "test_step.dependOn(&run_cmdline_tests.step);",
    },
    {
        "key": "argv_split",
        "helper_path": '"../../lib/argv_split.zig"',
        "helper_module_marker": """const argv_split_module = b.createModule(.{
        .root_source_file = b.path("../../lib/argv_split.zig"),
        .target = target,
        .optimize = optimize,
    });""",
        "root_path": '"phase7_argv_split.zig"',
        "root_module_marker": """const argv_split_root_module = b.createModule(.{
        .root_source_file = b.path("phase7_argv_split.zig"),
        .target = target,
        .optimize = optimize,
    });""",
        "import_marker": 'argv_split_root_module.addImport("argv_split", argv_split_module);',
        "test_name_marker": '.name = "phase7-argv-split-tests",',
        "depend_marker": "test_step.dependOn(&run_argv_split_tests.step);",
    },
    {
        "key": "rbtree",
        "helper_path": '"../../lib/rbtree.zig"',
        "helper_module_marker": """const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });""",
        "root_path": '"phase7_rbtree.zig"',
        "root_module_marker": """const rbtree_root_module = b.createModule(.{
        .root_source_file = b.path("phase7_rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });""",
        "import_marker": 'rbtree_root_module.addImport("rbtree", rbtree_module);',
        "test_name_marker": '.name = "phase7-rbtree-tests",',
        "depend_marker": "test_step.dependOn(&run_rbtree_tests.step);",
    },
]

REVIEW_GATE_SPECS = [
    {
        "key": "string_helpers_survey",
        "root_path": '"phase7_string_helpers_survey.zig"',
        "root_module_marker": """const string_helpers_survey_root_module = b.createModule(.{
        .root_source_file = b.path("phase7_string_helpers_survey.zig"),
        .target = target,
        .optimize = optimize,
    });""",
        "test_name_marker": '.name = "phase7-string-helpers-survey-tests",',
        "depend_marker": "test_step.dependOn(&run_string_helpers_survey_tests.step);",
        "cwd_marker": 'run_string_helpers_survey_tests.setCwd(b.path("../.."));',
        "step_name_marker": '"phase7-string-helpers-survey",',
        "step_name": "phase7-string-helpers-survey",
        "step_description_marker": '"Run the dedicated Phase 7 string_helpers survey gate",',
        "step_depend_marker": "string_helpers_survey_step.dependOn(&run_string_helpers_survey_tests.step);",
    },
    {
        "key": "string_helpers_sample_boundary",
        "root_path": '"phase7_string_helpers_sample_boundary.zig"',
        "root_module_marker": """const string_helpers_sample_boundary_root_module = b.createModule(.{
        .root_source_file = b.path("phase7_string_helpers_sample_boundary.zig"),
        .target = target,
        .optimize = optimize,
    });""",
        "test_name_marker": '.name = "phase7-string-helpers-sample-boundary-tests",',
        "depend_marker": "test_step.dependOn(&run_string_helpers_sample_boundary_tests.step);",
        "cwd_marker": 'run_string_helpers_sample_boundary_tests.setCwd(b.path("../.."));',
        "step_name_marker": '"phase7-string-helpers-sample-boundary",',
        "step_name": "phase7-string-helpers-sample-boundary",
        "step_description_marker": '"Run the dedicated Phase 7 string_helpers sample-boundary gate",',
        "step_depend_marker": "string_helpers_sample_boundary_step.dependOn(&run_string_helpers_sample_boundary_tests.step);",
    },
    {
        "key": "cmdline_survey",
        "root_path": '"phase7_cmdline_survey.zig"',
        "root_module_marker": """const cmdline_survey_root_module = b.createModule(.{
        .root_source_file = b.path("phase7_cmdline_survey.zig"),
        .target = target,
        .optimize = optimize,
    });""",
        "test_name_marker": '.name = "phase7-cmdline-survey-tests",',
        "depend_marker": "test_step.dependOn(&run_cmdline_survey_tests.step);",
        "cwd_marker": 'run_cmdline_survey_tests.setCwd(b.path("../.."));',
        "step_name_marker": '"phase7-cmdline-survey",',
        "step_name": "phase7-cmdline-survey",
        "step_description_marker": '"Run the dedicated Phase 7 cmdline survey gate",',
        "step_depend_marker": "cmdline_survey_step.dependOn(&run_cmdline_survey_tests.step);",
    },
    {
        "key": "argv_split_survey",
        "root_path": '"phase7_argv_split_survey.zig"',
        "root_module_marker": """const argv_split_survey_root_module = b.createModule(.{
        .root_source_file = b.path("phase7_argv_split_survey.zig"),
        .target = target,
        .optimize = optimize,
    });""",
        "test_name_marker": '.name = "phase7-argv-split-survey-tests",',
        "depend_marker": "test_step.dependOn(&run_argv_split_survey_tests.step);",
        "cwd_marker": 'run_argv_split_survey_tests.setCwd(b.path("../.."));',
        "step_name_marker": '"phase7-argv-split-survey",',
        "step_name": "phase7-argv-split-survey",
        "step_description_marker": '"Run the dedicated Phase 7 argv_split survey gate",',
        "step_depend_marker": "argv_split_survey_step.dependOn(&run_argv_split_survey_tests.step);",
    },
    {
        "key": "rbtree_survey",
        "root_path": '"phase7_rbtree_survey.zig"',
        "root_module_marker": """const rbtree_survey_root_module = b.createModule(.{
        .root_source_file = b.path("phase7_rbtree_survey.zig"),
        .target = target,
        .optimize = optimize,
    });""",
        "test_name_marker": '.name = "phase7-rbtree-survey-tests",',
        "depend_marker": "test_step.dependOn(&run_rbtree_survey_tests.step);",
        "cwd_marker": 'run_rbtree_survey_tests.setCwd(b.path("../.."));',
        "step_name_marker": '"phase7-rbtree-survey",',
        "step_name": "phase7-rbtree-survey",
        "step_description_marker": '"Run the dedicated Phase 7 rbtree survey gate",',
        "step_depend_marker": "rbtree_survey_step.dependOn(&run_rbtree_survey_tests.step);",
    },
]

BUILD_REQUIRED_MARKERS = [
    marker
    for spec in HELPER_SPECS
    for marker in (
        spec["helper_module_marker"],
        spec["root_module_marker"],
        spec["import_marker"],
        spec["test_name_marker"],
        spec["depend_marker"],
    )
] + [
    marker
    for spec in REVIEW_GATE_SPECS
    for marker in (
        spec["root_module_marker"],
        spec["test_name_marker"],
        spec["depend_marker"],
        spec["cwd_marker"],
        spec["step_name_marker"],
        spec["step_description_marker"],
        spec["step_depend_marker"],
    )
]

BUILD_EXACT_COUNT_MARKERS = [(marker, 1) for marker in BUILD_REQUIRED_MARKERS]


def collect_build_missing_markers(text: str) -> list[str]:
    missing: list[str] = []
    for marker in BUILD_REQUIRED_MARKERS:
        if marker not in text:
            missing.append(f"zigux/tests/phase7_build.zig: {marker}")
    for marker, expected_count in BUILD_EXACT_COUNT_MARKERS:
        actual_count = text.count(marker)
        if actual_count != expected_count:
            missing.append(
                f"zigux/tests/phase7_build.zig: {marker}:expected={expected_count}:actual={actual_count}"
            )
    return missing


def extract_make_target_block(text: str, target: str) -> str:
    block_lines: list[str] = []
    collecting = False
    for line in text.splitlines():
        if not collecting:
            if line == f"{target}:":
                collecting = True
                block_lines.append(line)
            continue
        if line and not line.startswith("\t"):
            break
        block_lines.append(line)
    return "\n".join(block_lines)


def collect_make_phony_counts(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for line in text.splitlines():
        if not line.startswith("PHONY +="):
            continue
        for token in line.split()[2:]:
            counts[token] = counts.get(token, 0) + 1
    return counts


def collect_makefile_missing_markers(text: str) -> list[str]:
    missing: list[str] = []
    phony_counts = collect_make_phony_counts(text)
    for spec in REVIEW_GATE_SPECS:
        target = spec["step_name"]
        phony_count = phony_counts.get(target, 0)
        if phony_count != 1:
            missing.append(
                f"zigux/Makefile PHONY: {target}:expected=1:actual={phony_count}"
            )

        expected_command = (
            f"\tcd $(ZIGUX_ROOT) && $(ZIG) build {target} "
            "--build-file zigux/tests/phase7_build.zig --summary all"
        )
        block = extract_make_target_block(text, target)
        if not block:
            missing.append(f"zigux/Makefile: missing target block {target}")
            continue

        actual_count = sum(1 for line in block.splitlines() if line == expected_command)
        if actual_count != 1:
            missing.append(
                f"zigux/Makefile target {target}: {expected_command}:expected=1:actual={actual_count}"
            )
    return missing


def validate(build_path: Path, makefile_path: Path) -> list[str]:
    missing = collect_build_missing_markers(build_path.read_text(encoding="utf-8"))
    missing.extend(collect_makefile_missing_markers(makefile_path.read_text(encoding="utf-8")))
    return missing


def mutate_text(path: Path, old: str, new: str, case: str) -> None:
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def duplicate_first_marker(text: str, marker: str) -> str:
    return text.replace(marker, f"{marker}\n{marker}", 1)


def remove_phony_token_once(text: str, target: str) -> str:
    marker = f" {target}"
    updated = text.replace(marker, "", 1)
    assert updated != text
    return updated


def duplicate_phony_token_once(text: str, target: str) -> str:
    marker = f" {target}"
    updated = text.replace(marker, f"{marker}{marker}", 1)
    assert updated != text
    return updated


def phase7_makefile_fixture() -> str:
    phony_targets = " ".join(spec["step_name"] for spec in REVIEW_GATE_SPECS)
    target_blocks: list[str] = [f"PHONY += {phony_targets}", ""]
    for spec in REVIEW_GATE_SPECS:
        target = spec["step_name"]
        target_blocks.extend(
            [
                f"{target}:",
                (
                    f"\tcd $(ZIGUX_ROOT) && $(ZIG) build {target} "
                    "--build-file zigux/tests/phase7_build.zig --summary all"
                ),
                "",
            ]
        )
    return "\n".join(target_blocks)


def run_self_test() -> None:
    build_fixture = "\n".join(BUILD_REQUIRED_MARKERS) + "\n"
    makefile_fixture = phase7_makefile_fixture()
    marker_cases = []
    exact_count_cases = []

    for spec in HELPER_SPECS:
        marker_cases.extend(
            [
                (
                    f"{spec['key']}_helper_module_target_drift",
                    spec["helper_module_marker"],
                    spec["helper_module_marker"].replace(".target = target,", ".target = b.graph.host,"),
                    f"zigux/tests/phase7_build.zig: {spec['helper_module_marker']}",
                ),
                (
                    f"{spec['key']}_root_module_optimize_drift",
                    spec["root_module_marker"],
                    spec["root_module_marker"].replace(".optimize = optimize,", ".optimize = .ReleaseSafe,"),
                    f"zigux/tests/phase7_build.zig: {spec['root_module_marker']}",
                ),
                (
                    f"{spec['key']}_import_alias_drift",
                    spec["import_marker"],
                    spec["import_marker"].replace(f'\"{spec["key"]}\"', f'\"{spec["key"]}_drift\"'),
                    f"zigux/tests/phase7_build.zig: {spec['import_marker']}",
                ),
                (
                    f"{spec['key']}_test_name_drift",
                    spec["test_name_marker"],
                    spec["test_name_marker"].replace("-tests", "-tests-drift"),
                    f"zigux/tests/phase7_build.zig: {spec['test_name_marker']}",
                ),
                (
                    f"{spec['key']}_depend_drift",
                    spec["depend_marker"],
                    spec["depend_marker"].replace(".step);", "_drift.step);"),
                    f"zigux/tests/phase7_build.zig: {spec['depend_marker']}",
                ),
            ]
        )
        exact_count_cases.extend(
            [
                (
                    f"{spec['key']}_helper_module_exact_count",
                    spec["helper_module_marker"],
                    f"zigux/tests/phase7_build.zig: {spec['helper_module_marker']}:expected=1:actual=2",
                ),
                (
                    f"{spec['key']}_root_module_exact_count",
                    spec["root_module_marker"],
                    f"zigux/tests/phase7_build.zig: {spec['root_module_marker']}:expected=1:actual=2",
                ),
                (
                    f"{spec['key']}_import_exact_count",
                    spec["import_marker"],
                    f"zigux/tests/phase7_build.zig: {spec['import_marker']}:expected=1:actual=2",
                ),
                (
                    f"{spec['key']}_depend_exact_count",
                    spec["depend_marker"],
                    f"zigux/tests/phase7_build.zig: {spec['depend_marker']}:expected=1:actual=2",
                ),
            ]
        )

    for spec in REVIEW_GATE_SPECS:
        marker_cases.extend(
            [
                (
                    f"{spec['key']}_root_module_target_drift",
                    spec["root_module_marker"],
                    spec["root_module_marker"].replace(".target = target,", ".target = b.graph.host,"),
                    f"zigux/tests/phase7_build.zig: {spec['root_module_marker']}",
                ),
                (
                    f"{spec['key']}_test_name_drift",
                    spec["test_name_marker"],
                    spec["test_name_marker"].replace("-tests", "-tests-drift"),
                    f"zigux/tests/phase7_build.zig: {spec['test_name_marker']}",
                ),
                (
                    f"{spec['key']}_depend_drift",
                    spec["depend_marker"],
                    spec["depend_marker"].replace(".step);", "_drift.step);"),
                    f"zigux/tests/phase7_build.zig: {spec['depend_marker']}",
                ),
                (
                    f"{spec['key']}_cwd_drift",
                    spec["cwd_marker"],
                    spec["cwd_marker"].replace("../..", "."),
                    f"zigux/tests/phase7_build.zig: {spec['cwd_marker']}",
                ),
                (
                    f"{spec['key']}_step_name_drift",
                    spec["step_name_marker"],
                    spec["step_name_marker"].replace('",', '-drift",'),
                    f"zigux/tests/phase7_build.zig: {spec['step_name_marker']}",
                ),
                (
                    f"{spec['key']}_step_description_drift",
                    spec["step_description_marker"],
                    spec["step_description_marker"].replace("dedicated ", "review-only "),
                    f"zigux/tests/phase7_build.zig: {spec['step_description_marker']}",
                ),
                (
                    f"{spec['key']}_step_depend_drift",
                    spec["step_depend_marker"],
                    spec["step_depend_marker"].replace(".step);", "_drift.step);"),
                    f"zigux/tests/phase7_build.zig: {spec['step_depend_marker']}",
                ),
            ]
        )
        exact_count_cases.extend(
            [
                (
                    f"{spec['key']}_root_module_exact_count",
                    spec["root_module_marker"],
                    f"zigux/tests/phase7_build.zig: {spec['root_module_marker']}:expected=1:actual=2",
                ),
                (
                    f"{spec['key']}_test_name_exact_count",
                    spec["test_name_marker"],
                    f"zigux/tests/phase7_build.zig: {spec['test_name_marker']}:expected=1:actual=2",
                ),
                (
                    f"{spec['key']}_depend_exact_count",
                    spec["depend_marker"],
                    f"zigux/tests/phase7_build.zig: {spec['depend_marker']}:expected=1:actual=2",
                ),
                (
                    f"{spec['key']}_cwd_exact_count",
                    spec["cwd_marker"],
                    f"zigux/tests/phase7_build.zig: {spec['cwd_marker']}:expected=1:actual=2",
                ),
                (
                    f"{spec['key']}_step_name_exact_count",
                    spec["step_name_marker"],
                    f"zigux/tests/phase7_build.zig: {spec['step_name_marker']}:expected=1:actual=2",
                ),
                (
                    f"{spec['key']}_step_description_exact_count",
                    spec["step_description_marker"],
                    f"zigux/tests/phase7_build.zig: {spec['step_description_marker']}:expected=1:actual=2",
                ),
                (
                    f"{spec['key']}_step_depend_exact_count",
                    spec["step_depend_marker"],
                    f"zigux/tests/phase7_build.zig: {spec['step_depend_marker']}:expected=1:actual=2",
                ),
            ]
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_build_wiring_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        build_path = tmp_root / "phase7_build.zig"
        makefile_path = tmp_root / "Makefile"
        build_path.write_text(build_fixture, encoding="utf-8")
        makefile_path.write_text(makefile_fixture, encoding="utf-8")
        assert validate(build_path, makefile_path) == []

        for case, old, new, expected in marker_cases:
            mutate_text(build_path, old, new, case)
            assert expected in validate(build_path, makefile_path), case
            build_path.write_text(build_fixture, encoding="utf-8")

        for case, marker, expected in exact_count_cases:
            original = build_path.read_text(encoding="utf-8")
            updated = duplicate_first_marker(original, marker)
            assert updated != original, case
            build_path.write_text(updated, encoding="utf-8")
            assert expected in validate(build_path, makefile_path), case
            build_path.write_text(build_fixture, encoding="utf-8")

        makefile_marker_cases = 0
        for spec in REVIEW_GATE_SPECS:
            target = spec["step_name"]
            expected_command = (
                f"\tcd $(ZIGUX_ROOT) && $(ZIG) build {target} "
                "--build-file zigux/tests/phase7_build.zig --summary all"
            )

            original = makefile_path.read_text(encoding="utf-8")
            makefile_path.write_text(remove_phony_token_once(original, target), encoding="utf-8")
            expected = f"zigux/Makefile PHONY: {target}:expected=1:actual=0"
            assert expected in validate(build_path, makefile_path), f"{target}_missing_phony"
            makefile_path.write_text(makefile_fixture, encoding="utf-8")
            makefile_marker_cases += 1

            original = makefile_path.read_text(encoding="utf-8")
            makefile_path.write_text(duplicate_phony_token_once(original, target), encoding="utf-8")
            expected = f"zigux/Makefile PHONY: {target}:expected=1:actual=2"
            assert expected in validate(build_path, makefile_path), f"{target}_duplicate_phony"
            makefile_path.write_text(makefile_fixture, encoding="utf-8")
            makefile_marker_cases += 1

            mutate_text(
                makefile_path,
                expected_command,
                expected_command.replace("--summary all", ""),
                f"{target}_command_drift",
            )
            expected = (
                f"zigux/Makefile target {target}: {expected_command}:expected=1:actual=0"
            )
            assert expected in validate(build_path, makefile_path), f"{target}_command_drift"
            makefile_path.write_text(makefile_fixture, encoding="utf-8")
            makefile_marker_cases += 1

    print("PHASE7_BUILD_WIRING_SELF_TEST=pass")
    print(
        "PHASE7_BUILD_WIRING_SELF_TEST_CASE_COUNT=%d"
        % (len(marker_cases) + len(exact_count_cases) + makefile_marker_cases)
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check Phase 7 helper-module, build-step, and Makefile survey wiring."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-test cases without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing = validate(TARGET, MAKEFILE)
    if missing:
        print("PHASE7_BUILD_WIRING=fail")
        print("MISSING_PHASE7_BUILD_WIRING_MARKERS_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE7_BUILD_WIRING_MARKERS_END")
        return 1

    print("PHASE7_BUILD_WIRING=pass")
    print(
        "PHASE7_BUILD_WIRING_REQUIRED_MARKER_COUNT=%d"
        % (len(BUILD_REQUIRED_MARKERS) + (2 * len(REVIEW_GATE_SPECS)))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
