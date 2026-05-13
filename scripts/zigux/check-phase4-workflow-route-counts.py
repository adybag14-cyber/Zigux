#!/usr/bin/env python3
"""Validate the shipped Phase 4 wrapper-route inventory.

This checker stays intentionally narrow: it verifies that the live Linux-style
Makefile wrapper inventory, the shared workflow, the Phase 4 validation notes,
and the dedicated local perf-baseline survey packet all agree on the bounded
Phase 4 review surface.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


EXPECTED_MAKE_TARGETS = [
    "phase4-validate",
    "phase4-artifact-diff-contract",
    "phase4-test",
    "phase4-runtime-atomic64-diff",
    "phase4-runtime-atomic64-diff-survey",
    "phase4-perf-baseline-survey",
    "phase4-bitmap-diff",
    "phase4-bitmap-diff-survey",
    "phase4-bitmap-live-helper-replay",
    "phase4-test-fsmount-survey",
    "phase4-kprobe-example-survey",
    "phase4",
]

REQUIRED_MAKE_MARKERS = [
    "PHONY += phase4-validate phase4-artifact-diff-contract phase4-test "
    "phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey "
    "phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey "
    "phase4-bitmap-live-helper-replay phase4-test-fsmount-survey "
    "phase4-kprobe-example-survey phase4",
    "phase4-validate:",
    "scripts/zigux/validate-phase4.py --self-test",
    "scripts/zigux/validate-phase4.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-remaining-gap-matrix.py",
    "scripts/zigux/check-phase4-workflow-route-counts.py",
    "phase4-artifact-diff-contract:",
    "scripts/zigux/artifact_diff.py --self-test",
    "scripts/zigux/check-artifact-diff-contract.py --self-test",
    "phase4-test:",
    "$(ZIG) build test --build-file zigux/tests/phase4_build.zig",
    "phase4-runtime-atomic64-diff:",
    "$(ZIG) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
    "phase4-runtime-atomic64-diff-survey:",
    "$(ZIG) build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-perf-baseline-survey:",
    "$(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-diff:",
    "$(ZIG) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-diff-survey:",
    "$(ZIG) build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-live-helper-replay:",
    "$(ZIG) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig",
    "phase4-test-fsmount-survey:",
    "$(ZIG) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-kprobe-example-survey:",
    "$(ZIG) test zigux/tests/phase4_kprobe_example_survey.zig",
    "phase4: phase4-validate phase4-test",
]

REQUIRED_PHASE4_VALIDATE_COMMANDS = [
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-remaining-gap-matrix.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py",
]

REQUIRED_PHASE4_ARTIFACT_DIFF_CONTRACT_COMMANDS = [
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py",
]

REQUIRED_WORKFLOW_MARKERS = [
    "- name: Validate Phase 4 diff gates",
    "run: make -C zigux phase4-validate",
    "- name: Self-test Phase 4 validator directly",
    "run: python3 scripts/zigux/validate-phase4.py --self-test",
    "- name: Validate Phase 4 diff packet directly",
    "run: python3 scripts/zigux/validate-phase4.py",
    "- name: Self-test Phase 4 artifact-diff contract directly",
    "run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test",
    "- name: Check Phase 4 artifact-diff contract directly",
    "run: python3 scripts/zigux/check-artifact-diff-contract.py",
    "- name: Self-test Phase 4 artifact-diff determinism directly",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "- name: Check Phase 4 artifact-diff determinism directly",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "- name: Self-test Phase 4 remaining-gap matrix directly",
    "run: python3 scripts/zigux/check-phase4-remaining-gap-matrix.py --self-test",
    "- name: Check Phase 4 remaining-gap matrix directly",
    "run: python3 scripts/zigux/check-phase4-remaining-gap-matrix.py",
    "- name: Self-test Phase 4 workflow route counts directly",
    "run: python3 scripts/zigux/check-phase4-workflow-route-counts.py --self-test",
    "- name: Check Phase 4 workflow route counts directly",
    "run: python3 scripts/zigux/check-phase4-workflow-route-counts.py",
    "- name: Check Phase 4 gate evidence directly",
    "run: python3 scripts/zigux/check-phase4-gate-evidence.py",
    "- name: Run Phase 4 diff tests directly",
    "run: zig build test --build-file zigux/tests/phase4_build.zig",
]

REQUIRED_WORKFLOW_ORDER_MARKERS = [
    "run: make -C zigux phase4-validate",
    "run: python3 scripts/zigux/validate-phase4.py --self-test",
    "run: python3 scripts/zigux/validate-phase4.py",
    "run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test",
    "run: python3 scripts/zigux/check-artifact-diff-contract.py",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "run: python3 scripts/zigux/check-phase4-remaining-gap-matrix.py --self-test",
    "run: python3 scripts/zigux/check-phase4-remaining-gap-matrix.py",
    "run: python3 scripts/zigux/check-phase4-workflow-route-counts.py --self-test",
    "run: python3 scripts/zigux/check-phase4-workflow-route-counts.py",
    "run: python3 scripts/zigux/check-phase4-gate-evidence.py",
    "run: zig build test --build-file zigux/tests/phase4_build.zig",
]

REQUIRED_BUILD_MARKERS = [
    'b.path("phase4_perf_baseline_survey.zig")',
    '"phase4-perf-baseline-survey-tests"',
    "const perf_baseline_survey_step = b.step(",
    '"phase4-perf-baseline-survey",',
    '"Run the dedicated Phase 4 perf-baseline posture survey without widening the shared correctness-first packet",',
    "perf_baseline_survey_step.dependOn(&run_perf_baseline_survey_tests.step);",
]

REQUIRED_MATRIX_MARKERS = [
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-perf-baseline-survey",
    "scripts/zigux/check-phase4-remaining-gap-matrix.py",
]

REQUIRED_GATE_EVIDENCE_MARKERS = [
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-perf-baseline-survey",
    "zig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-bitmap-diff-survey",
]

REQUIRED_TESTS_README_MARKERS = [
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-perf-baseline-survey",
]

FORBIDDEN_BUILD_MARKERS = [
    "test_step.dependOn(&run_perf_baseline_survey_tests.step);",
]

SELFTEST_CASES = [
    "baseline_round_trip",
    "workflow_order_drift",
    "missing_make_artifact_diff_contract_selftest_command",
    "missing_make_route_counts_command",
    "missing_make_remaining_gap_command",
    "missing_workflow_validate_route",
    "missing_workflow_artifact_diff_determinism_self_test_route",
    "missing_workflow_artifact_diff_determinism_route",
    "missing_workflow_remaining_gap_self_test_route",
    "missing_workflow_remaining_gap_route",
    "missing_workflow_route_counts_self_test_route",
    "missing_workflow_route_counts_route",
    "missing_workflow_gate_evidence_route",
    "missing_matrix_remaining_gap_marker",
    "missing_gate_evidence_bitmap_wrapper",
    "missing_tests_readme_perf_make_route",
    "forbidden_perf_baseline_dependency",
]

SELFTEST_MAKEFILE = """PHONY += phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4

phase4-validate:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-remaining-gap-matrix.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py

phase4-artifact-diff-contract:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py

phase4-test:
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase4_build.zig

phase4-runtime-atomic64-diff:
\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig

phase4-runtime-atomic64-diff-survey:
\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig

phase4-perf-baseline-survey:
\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig

phase4-bitmap-diff:
\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig

phase4-bitmap-diff-survey:
\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig

phase4-bitmap-live-helper-replay:
\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig

phase4-test-fsmount-survey:
\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig

phase4-kprobe-example-survey:
\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/phase4_kprobe_example_survey.zig

phase4: phase4-validate phase4-test
"""

SELFTEST_WORKFLOW = """jobs:
  bootstrap:
    steps:
      - name: Validate Phase 4 diff gates
        run: make -C zigux phase4-validate
      - name: Self-test Phase 4 validator directly
        run: python3 scripts/zigux/validate-phase4.py --self-test
      - name: Validate Phase 4 diff packet directly
        run: python3 scripts/zigux/validate-phase4.py
      - name: Self-test Phase 4 artifact-diff contract directly
        run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test
      - name: Check Phase 4 artifact-diff contract directly
        run: python3 scripts/zigux/check-artifact-diff-contract.py
      - name: Self-test Phase 4 artifact-diff determinism directly
        run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test
      - name: Check Phase 4 artifact-diff determinism directly
        run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py
      - name: Self-test Phase 4 remaining-gap matrix directly
        run: python3 scripts/zigux/check-phase4-remaining-gap-matrix.py --self-test
      - name: Check Phase 4 remaining-gap matrix directly
        run: python3 scripts/zigux/check-phase4-remaining-gap-matrix.py
      - name: Self-test Phase 4 workflow route counts directly
        run: python3 scripts/zigux/check-phase4-workflow-route-counts.py --self-test
      - name: Check Phase 4 workflow route counts directly
        run: python3 scripts/zigux/check-phase4-workflow-route-counts.py
      - name: Check Phase 4 gate evidence directly
        run: python3 scripts/zigux/check-phase4-gate-evidence.py
      - name: Run Phase 4 diff tests directly
        run: zig build test --build-file zigux/tests/phase4_build.zig
"""

SELFTEST_BUILD = """const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const perf_baseline_survey_module = b.createModule(.{
        .root_source_file = b.path("phase4_perf_baseline_survey.zig"),
        .target = target,
        .optimize = optimize,
    });
    const perf_baseline_survey_tests = b.addTest(.{
        .name = "phase4-perf-baseline-survey-tests",
        .root_module = perf_baseline_survey_module,
    });
    const run_perf_baseline_survey_tests = b.addRunArtifact(perf_baseline_survey_tests);
    const test_step = b.step("test", "Run Phase 4 differential validation tests");
    const perf_baseline_survey_step = b.step(
        "phase4-perf-baseline-survey",
        "Run the dedicated Phase 4 perf-baseline posture survey without widening the shared correctness-first packet",
    );
    perf_baseline_survey_step.dependOn(&run_perf_baseline_survey_tests.step);
}
"""

SELFTEST_MATRIX = """# Phase 4 Validation Matrix
scripts/zigux/check-phase4-remaining-gap-matrix.py
zigux/tests/phase4_perf_baseline_manifest.json
zigux/tests/phase4_perf_baseline_survey.zig
zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig
make -C zigux phase4-perf-baseline-survey
"""

SELFTEST_GATE_EVIDENCE = """# Phase 4 Gate Evidence
zigux/tests/phase4_perf_baseline_manifest.json
zigux/tests/phase4_perf_baseline_survey.zig
zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig
make -C zigux phase4-perf-baseline-survey
zig build phase4-bitmap-diff-survey --build-file zigux/tests/phase4_build.zig
make -C zigux phase4-bitmap-diff-survey
"""

SELFTEST_TESTS_README = """# zigux/tests
zigux/tests/phase4_perf_baseline_manifest.json
zigux/tests/phase4_perf_baseline_survey.zig
zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig
make -C zigux phase4-perf-baseline-survey
"""


def repo_root_from_script(script_path: Path) -> Path:
    return script_path.resolve().parents[2]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {path}") from exc


def ensure_markers(label: str, text: str, markers: list[str]) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        joined = "\n".join(f"  - {marker}" for marker in missing)
        raise SystemExit(f"{label} is missing required Phase 4 markers:\n{joined}")


def ensure_marker_order(label: str, text: str, ordered_markers: list[str]) -> None:
    lines = [line.strip() for line in text.splitlines()]
    positions: list[int] = []
    for marker in ordered_markers:
        try:
            positions.append(lines.index(marker))
        except ValueError as exc:
            raise SystemExit(
                f"{label} is missing required Phase 4 order marker:\n  - {marker}"
            ) from exc
    for idx in range(1, len(positions)):
        if positions[idx] <= positions[idx - 1]:
            joined = "\n".join(f"  - {marker}" for marker in ordered_markers)
            raise SystemExit(
                f"{label} has out-of-order Phase 4 workflow markers:\n{joined}"
            )


def ensure_absent_markers(label: str, text: str, markers: list[str]) -> None:
    present = [marker for marker in markers if marker in text]
    if present:
        joined = "\n".join(f"  - {marker}" for marker in present)
        raise SystemExit(f"{label} contains forbidden Phase 4 markers:\n{joined}")


def target_body(makefile_text: str, target: str) -> str:
    lines = makefile_text.splitlines()
    inside_target = False
    body_lines: list[str] = []
    target_prefix = f"{target}:"
    for line in lines:
        if inside_target:
            if line.startswith("\t"):
                body_lines.append(line)
                continue
            break
        if line.startswith(target_prefix):
            inside_target = True
    if not inside_target:
        raise SystemExit(
            f"zigux/Makefile is missing expected Phase 4 target body:\n  - {target}"
        )
    return "\n".join(body_lines)


def declared_targets(makefile_text: str) -> set[str]:
    targets: set[str] = set()
    for line in makefile_text.splitlines():
        if not line or line.startswith(("\t", "#", "PHONY", ".")):
            continue
        match = re.match(r"^([A-Za-z0-9][A-Za-z0-9_-]*):", line)
        if match:
            targets.add(match.group(1))
    return targets


def required_file_count() -> int:
    return 8


def required_check_count() -> int:
    return (
        len(EXPECTED_MAKE_TARGETS)
        + len(REQUIRED_MAKE_MARKERS)
        + len(REQUIRED_PHASE4_VALIDATE_COMMANDS)
        + len(REQUIRED_PHASE4_ARTIFACT_DIFF_CONTRACT_COMMANDS)
        + len(REQUIRED_WORKFLOW_MARKERS)
        + len(REQUIRED_WORKFLOW_ORDER_MARKERS)
        + len(REQUIRED_BUILD_MARKERS)
        + len(REQUIRED_MATRIX_MARKERS)
        + len(REQUIRED_GATE_EVIDENCE_MARKERS)
        + len(REQUIRED_TESTS_README_MARKERS)
        + len(FORBIDDEN_BUILD_MARKERS)
    )


def ensure_expected_targets(makefile_text: str) -> None:
    targets = declared_targets(makefile_text)
    missing = [target for target in EXPECTED_MAKE_TARGETS if target not in targets]
    if missing:
        joined = "\n".join(f"  - {target}" for target in missing)
        raise SystemExit(f"zigux/Makefile is missing expected Phase 4 targets:\n{joined}")


def ensure_target_commands(makefile_text: str, target: str, commands: list[str]) -> None:
    body_lines = target_body(makefile_text, target).splitlines()
    missing = [command for command in commands if command not in body_lines]
    if missing:
        joined = "\n".join(f"  - {command}" for command in missing)
        raise SystemExit(
            f"zigux/Makefile target {target} is missing required Phase 4 commands:\n{joined}")


def check(
    makefile_path: Path,
    workflow_path: Path,
    build_path: Path,
    validation_matrix_path: Path,
    gate_evidence_path: Path,
    tests_readme_path: Path,
    perf_manifest_path: Path,
    perf_survey_path: Path,
) -> None:
    makefile_text = read_text(makefile_path)
    workflow_text = read_text(workflow_path)
    build_text = read_text(build_path)
    validation_matrix_text = read_text(validation_matrix_path)
    gate_evidence_text = read_text(gate_evidence_path)
    tests_readme_text = read_text(tests_readme_path)
    read_text(perf_manifest_path)
    read_text(perf_survey_path)

    ensure_expected_targets(makefile_text)
    ensure_markers("zigux/Makefile", makefile_text, REQUIRED_MAKE_MARKERS)
    ensure_target_commands(makefile_text, "phase4-validate", REQUIRED_PHASE4_VALIDATE_COMMANDS)
    ensure_target_commands(
        makefile_text,
        "phase4-artifact-diff-contract",
        REQUIRED_PHASE4_ARTIFACT_DIFF_CONTRACT_COMMANDS,
    )
    ensure_markers(".github/workflows/zigux-bootstrap.yml", workflow_text, REQUIRED_WORKFLOW_MARKERS)
    ensure_marker_order(
        ".github/workflows/zigux-bootstrap.yml",
        workflow_text,
        REQUIRED_WORKFLOW_ORDER_MARKERS,
    )
    ensure_markers("zigux/tests/phase4_build.zig", build_text, REQUIRED_BUILD_MARKERS)
    ensure_markers(
        "Documentation/zigux/phase4-validation-matrix.md",
        validation_matrix_text,
        REQUIRED_MATRIX_MARKERS,
    )
    ensure_markers(
        "Documentation/zigux/phase4-gate-evidence.md",
        gate_evidence_text,
        REQUIRED_GATE_EVIDENCE_MARKERS,
    )
    ensure_markers("zigux/tests/README.md", tests_readme_text, REQUIRED_TESTS_README_MARKERS)
    ensure_absent_markers("zigux/tests/phase4_build.zig", build_text, FORBIDDEN_BUILD_MARKERS)


def emit_status(*, self_test: bool) -> None:
    if self_test:
        print("PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass")
        print(f"PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASE_COUNT={len(SELFTEST_CASES)}")
        print("PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASES=" + ",".join(SELFTEST_CASES))
    else:
        print("PHASE4_WORKFLOW_ROUTE_COUNTS_CHECK=pass")
        print("PHASE4_WORKFLOW_ROUTE_COUNTS=pass")
    print(f"PHASE4_WORKFLOW_ROUTE_COUNT={len(EXPECTED_MAKE_TARGETS)}")
    print(f"PHASE4_WORKFLOW_MARKER_COUNT={len(REQUIRED_WORKFLOW_MARKERS)}")
    print(f"PHASE4_WORKFLOW_ORDER_MARKER_COUNT={len(REQUIRED_WORKFLOW_ORDER_MARKERS)}")
    print(f"PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT={required_file_count()}")
    print(f"PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_CHECK_COUNT={required_check_count()}")


def expect_failure(label: str, fn) -> None:
    try:
        fn()
    except SystemExit:
        return
    raise SystemExit(f"{label} did not fail the Phase 4 workflow-route self-test")


def run_selftest() -> None:
    with TemporaryDirectory(prefix="zigux_phase4_workflow_routes_") as tempdir:
        root = Path(tempdir)
        makefile = root / "zigux/Makefile"
        workflow = root / ".github/workflows/zigux-bootstrap.yml"
        build = root / "zigux/tests/phase4_build.zig"
        validation_matrix = root / "Documentation/zigux/phase4-validation-matrix.md"
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        tests_readme = root / "zigux/tests/README.md"
        perf_manifest = root / "zigux/tests/phase4_perf_baseline_manifest.json"
        perf_survey = root / "zigux/tests/phase4_perf_baseline_survey.zig"

        for path in (
            makefile.parent,
            workflow.parent,
            build.parent,
            validation_matrix.parent,
            gate_evidence.parent,
        ):
            path.mkdir(parents=True, exist_ok=True)

        def write_baseline() -> None:
            makefile.write_text(SELFTEST_MAKEFILE, encoding="utf-8")
            workflow.write_text(SELFTEST_WORKFLOW, encoding="utf-8")
            build.write_text(SELFTEST_BUILD, encoding="utf-8")
            validation_matrix.write_text(SELFTEST_MATRIX, encoding="utf-8")
            gate_evidence.write_text(SELFTEST_GATE_EVIDENCE, encoding="utf-8")
            tests_readme.write_text(SELFTEST_TESTS_README, encoding="utf-8")
            perf_manifest.write_text("{}\n", encoding="utf-8")
            perf_survey.write_text('test "phase4 perf baseline selftest" {}\n', encoding="utf-8")

        write_baseline()
        check(
            makefile,
            workflow,
            build,
            validation_matrix,
            gate_evidence,
            tests_readme,
            perf_manifest,
            perf_survey,
        )

        write_baseline()
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                "      - name: Validate Phase 4 diff gates\n"
                "        run: make -C zigux phase4-validate\n"
                "      - name: Self-test Phase 4 validator directly\n"
                "        run: python3 scripts/zigux/validate-phase4.py --self-test\n",
                "      - name: Self-test Phase 4 validator directly\n"
                "        run: python3 scripts/zigux/validate-phase4.py --self-test\n"
                "      - name: Validate Phase 4 diff gates\n"
                "        run: make -C zigux phase4-validate\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "workflow order drift",
            lambda: check(
                makefile,
                workflow,
                build,
                validation_matrix,
                gate_evidence,
                tests_readme,
                perf_manifest,
                perf_survey,
            ),
        )

        write_baseline()
        makefile.write_text(
            makefile.read_text(encoding="utf-8").replace(
                "phase4-artifact-diff-contract:\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py --self-test\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py\n",
                "phase4-artifact-diff-contract:\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "missing artifact-diff contract self-test Makefile command",
            lambda: check(
                makefile,
                workflow,
                build,
                validation_matrix,
                gate_evidence,
                tests_readme,
                perf_manifest,
                perf_survey,
            ),
        )

        write_baseline()
        makefile.write_text(
            makefile.read_text(encoding="utf-8").replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "missing workflow-route-counts Makefile command",
            lambda: check(
                makefile,
                workflow,
                build,
                validation_matrix,
                gate_evidence,
                tests_readme,
                perf_manifest,
                perf_survey,
            ),
        )

        write_baseline()
        makefile.write_text(
            makefile.read_text(encoding="utf-8").replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-remaining-gap-matrix.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "missing remaining-gap Makefile command",
            lambda: check(
                makefile,
                workflow,
                build,
                validation_matrix,
                gate_evidence,
                tests_readme,
                perf_manifest,
                perf_survey,
            ),
        )

        write_baseline()
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                "        run: make -C zigux phase4-validate\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "missing workflow validate route",
            lambda: check(
                makefile,
                workflow,
                build,
                validation_matrix,
                gate_evidence,
                tests_readme,
                perf_manifest,
                perf_survey,
            ),
        )

        write_baseline()
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                "        run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "missing workflow artifact-diff determinism self-test route",
            lambda: check(
                makefile,
                workflow,
                build,
                validation_matrix,
                gate_evidence,
                tests_readme,
                perf_manifest,
                perf_survey,
            ),
        )

        write_baseline()
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                "        run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "missing workflow artifact-diff determinism route",
            lambda: check(
                makefile,
                workflow,
                build,
                validation_matrix,
                gate_evidence,
                tests_readme,
                perf_manifest,
                perf_survey,
            ),
        )

        write_baseline()
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                "        run: python3 scripts/zigux/check-phase4-remaining-gap-matrix.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "missing workflow remaining-gap self-test route",
            lambda: check(
                makefile,
                workflow,
                build,
                validation_matrix,
                gate_evidence,
                tests_readme,
                perf_manifest,
                perf_survey,
            ),
        )

        write_baseline()
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                "        run: python3 scripts/zigux/check-phase4-remaining-gap-matrix.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "missing workflow remaining-gap route",
            lambda: check(
                makefile,
                workflow,
                build,
                validation_matrix,
                gate_evidence,
                tests_readme,
                perf_manifest,
                perf_survey,
            ),
        )

        write_baseline()
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                "        run: python3 scripts/zigux/check-phase4-workflow-route-counts.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "missing workflow route-counts self-test route",
            lambda: check(
                makefile,
                workflow,
                build,
                validation_matrix,
                gate_evidence,
                tests_readme,
                perf_manifest,
                perf_survey,
            ),
        )

        write_baseline()
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                "        run: python3 scripts/zigux/check-phase4-workflow-route-counts.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "missing workflow route-counts route",
            lambda: check(
                makefile,
                workflow,
                build,
                validation_matrix,
                gate_evidence,
                tests_readme,
                perf_manifest,
                perf_survey,
            ),
        )

        write_baseline()
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                "        run: python3 scripts/zigux/check-phase4-gate-evidence.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "missing workflow gate-evidence route",
            lambda: check(
                makefile,
                workflow,
                build,
                validation_matrix,
                gate_evidence,
                tests_readme,
                perf_manifest,
                perf_survey,
            ),
        )

        write_baseline()
        validation_matrix.write_text(
            validation_matrix.read_text(encoding="utf-8").replace(
                "scripts/zigux/check-phase4-remaining-gap-matrix.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "missing matrix remaining-gap marker",
            lambda: check(
                makefile,
                workflow,
                build,
                validation_matrix,
                gate_evidence,
                tests_readme,
                perf_manifest,
                perf_survey,
            ),
        )

        write_baseline()
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "make -C zigux phase4-bitmap-diff-survey\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "missing gate-evidence bitmap wrapper",
            lambda: check(
                makefile,
                workflow,
                build,
                validation_matrix,
                gate_evidence,
                tests_readme,
                perf_manifest,
                perf_survey,
            ),
        )

        write_baseline()
        tests_readme.write_text(
            tests_readme.read_text(encoding="utf-8").replace(
                "make -C zigux phase4-perf-baseline-survey\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "missing tests README perf make route",
            lambda: check(
                makefile,
                workflow,
                build,
                validation_matrix,
                gate_evidence,
                tests_readme,
                perf_manifest,
                perf_survey,
            ),
        )

        write_baseline()
        build.write_text(
            build.read_text(encoding="utf-8").replace(
                'const test_step = b.step("test", "Run Phase 4 differential validation tests");',
                'const test_step = b.step("test", "Run Phase 4 differential validation tests"); test_step.dependOn(&run_perf_baseline_survey_tests.step);',
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "forbidden perf-baseline dependency",
            lambda: check(
                makefile,
                workflow,
                build,
                validation_matrix,
                gate_evidence,
                tests_readme,
                perf_manifest,
                perf_survey,
            ),
        )

    emit_status(self_test=True)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        run_selftest()
        return 0

    root = repo_root_from_script(Path(__file__))
    check(
        root / "zigux/Makefile",
        root / ".github/workflows/zigux-bootstrap.yml",
        root / "zigux/tests/phase4_build.zig",
        root / "Documentation/zigux/phase4-validation-matrix.md",
        root / "Documentation/zigux/phase4-gate-evidence.md",
        root / "zigux/tests/README.md",
        root / "zigux/tests/phase4_perf_baseline_manifest.json",
        root / "zigux/tests/phase4_perf_baseline_survey.zig",
    )
    emit_status(self_test=False)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
