#!/usr/bin/env python3
"""Check the current Phase 7 runtime-workspace bootstrap handoff chain."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(".")

CATALOG_PATH = Path("Documentation/zigux/phase7-leaf-library-evidence-catalog.md")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase7.py")
MAKEFILE_PATH = Path("zigux/Makefile")
BUILD_PATH = Path("zigux/tests/phase7_build.zig")

REQUIRED_FILES = [
    CATALOG_PATH,
    WORKFLOW_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
    BUILD_PATH,
]

WORKFLOW_REQUIRED_ORDER = [
    "run: zig test zigux/tests/runtime_trace_events_survey.zig",
    "run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test",
    "run: python3 scripts/zigux/check-phase7-shared-control-gap.py",
    "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test",
]

WORKFLOW_PHASE7_HOOKS = [
    "run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test",
    "run: python3 scripts/zigux/check-phase7-shared-control-gap.py",
    "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
]

WORKFLOW_FORBIDDEN_LINES = [
    "run: make -C zigux phase7-validate",
    "run: python3 scripts/zigux/validate-phase7.py --self-test",
    "run: python3 scripts/zigux/validate-phase7.py",
    "run: zig build test --build-file zigux/tests/phase7_build.zig --summary all",
]

VALIDATOR_REQUIRED_ORDER = [
    "run_checker_self_test(root, CHECKER_PATH)",
    "run_checker(root, CHECKER_PATH)",
    "run_checker_self_test(root, BUILD_WIRING_CHECKER_PATH)",
    "run_checker(root, BUILD_WIRING_CHECKER_PATH)",
    "run_checker_self_test(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH)",
    'run_checker(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, "--root")',
    "run_checker_self_test(root, CMDLINE_PACKET_CHECKER_PATH)",
    "run_checker(root, CMDLINE_PACKET_CHECKER_PATH)",
    "run_checker_self_test(root, ARGV_SPLIT_PACKET_CHECKER_PATH)",
    "run_checker(root, ARGV_SPLIT_PACKET_CHECKER_PATH)",
    "run_checker_self_test(root, STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH)",
    'run_checker(root, STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH, "--root")',
    "run_checker_self_test(root, RBTREE_PARITY_PACKET_CHECKER_PATH)",
    "run_checker(root, RBTREE_PARITY_PACKET_CHECKER_PATH)",
]

MAKEFILE_REQUIRED_LINES = [
    "phase7-validate:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py",
]

MAKEFILE_FORBIDDEN_LINES = [
    "phase7-test:",
    "phase7:",
]

BUILD_TEST_STEP_ORDER = [
    "test_step.dependOn(&run_string_helpers_tests.step);",
    "test_step.dependOn(&run_string_helpers_survey_tests.step);",
    "test_step.dependOn(&run_string_helpers_sample_boundary_tests.step);",
    "test_step.dependOn(&run_string_helpers_format_boundary_tests.step);",
    "test_step.dependOn(&run_cmdline_tests.step);",
    "test_step.dependOn(&run_cmdline_survey_tests.step);",
    "test_step.dependOn(&run_argv_split_tests.step);",
    "test_step.dependOn(&run_argv_split_survey_tests.step);",
    "test_step.dependOn(&run_rbtree_tests.step);",
    "test_step.dependOn(&run_rbtree_survey_tests.step);",
]

CATALOG_REQUIRED_SNIPPETS = [
    "- `zigux/tests/phase7_build.zig` keeps the shared `test` build step aggregating every helper, survey, sample-boundary, and format-boundary replay through the current `test_step.dependOn(...)` handoff list.",
    "- `zigux/Makefile` keeps the narrow `phase7-validate` foothold explicit while broader wrapper routes remain outside this packet.",
]

SELF_TEST_CASE_COUNT = 17


class ValidationError(RuntimeError):
    pass


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {rel.as_posix()}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker.strip())


def require_exact_line_once(text: str, rel: Path, marker: str) -> None:
    count = count_exact_lines(text, marker)
    if count == 0:
        raise ValidationError(f"missing expected line in {rel.as_posix()}: {marker}")
    if count != 1:
        raise ValidationError(f"duplicate expected line in {rel.as_posix()}: {marker}")


def require_absent_line(text: str, rel: Path, marker: str) -> None:
    if count_exact_lines(text, marker):
        raise ValidationError(f"unexpected line in {rel.as_posix()}: {marker}")


def require_exact_line_order(text: str, rel: Path, markers: list[str]) -> None:
    lines = text.splitlines()
    cursor = -1
    for marker in markers:
        found = False
        for idx, line in enumerate(lines):
            if line.strip() == marker.strip():
                if idx <= cursor:
                    raise ValidationError(f"out-of-order marker in {rel.as_posix()}: {marker}")
                cursor = idx
                found = True
                break
        if not found:
            raise ValidationError(f"missing expected line in {rel.as_posix()}: {marker}")


def validate(root: Path) -> None:
    missing = [rel.as_posix() for rel in REQUIRED_FILES if not (root / rel).is_file()]
    if missing:
        raise ValidationError("missing required files: " + ", ".join(missing))

    workflow = read_text(root, WORKFLOW_PATH)
    validator = read_text(root, VALIDATOR_PATH)
    makefile = read_text(root, MAKEFILE_PATH)
    build = read_text(root, BUILD_PATH)
    catalog = read_text(root, CATALOG_PATH)

    require_exact_line_order(workflow, WORKFLOW_PATH, WORKFLOW_REQUIRED_ORDER)
    for marker in WORKFLOW_PHASE7_HOOKS:
        require_exact_line_once(workflow, WORKFLOW_PATH, marker)
    for marker in WORKFLOW_FORBIDDEN_LINES:
        require_absent_line(workflow, WORKFLOW_PATH, marker)

    require_exact_line_order(validator, VALIDATOR_PATH, VALIDATOR_REQUIRED_ORDER)

    for marker in MAKEFILE_REQUIRED_LINES:
        require_exact_line_once(makefile, MAKEFILE_PATH, marker)
    for marker in MAKEFILE_FORBIDDEN_LINES:
        require_absent_line(makefile, MAKEFILE_PATH, marker)

    require_exact_line_order(build, BUILD_PATH, BUILD_TEST_STEP_ORDER)
    require_exact_line_once(
        build,
        BUILD_PATH,
        'const test_step = b.step("test", "Run the Phase 7 runtime helper tests");',
    )

    for snippet in CATALOG_REQUIRED_SNIPPETS:
        if snippet not in catalog:
            raise ValidationError(f"missing expected marker in {CATALOG_PATH.as_posix()}: {snippet}")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_fixture_root(root: Path) -> None:
    write(root / CATALOG_PATH, "\n".join(CATALOG_REQUIRED_SNIPPETS) + "\n")
    workflow_lines = [
        "run: zig test zigux/tests/runtime_trace_events_survey.zig",
        "run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test",
        "run: python3 scripts/zigux/check-phase7-shared-control-gap.py",
        "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
        "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "run: python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test",
    ]
    write(root / WORKFLOW_PATH, "\n".join(workflow_lines) + "\n")
    write(root / VALIDATOR_PATH, "\n".join(VALIDATOR_REQUIRED_ORDER) + "\n")
    write(root / MAKEFILE_PATH, "\n".join(MAKEFILE_REQUIRED_LINES) + "\n")
    build_lines = [
        'const test_step = b.step("test", "Run the Phase 7 runtime helper tests");',
        *BUILD_TEST_STEP_ORDER,
    ]
    write(root / BUILD_PATH, "\n".join(build_lines) + "\n")


def mutate_once(root: Path, rel: Path, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    updated = text.replace(old, new, 1)
    if updated == text:
        raise AssertionError(f"marker not found for mutation: {old}")
    path.write_text(updated, encoding="utf-8")


def expect_failure(root: Path) -> None:
    try:
        validate(root)
    except ValidationError:
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_runtime_workspace_handoff_") as tmpdir:
        root = Path(tmpdir)
        build_fixture_root(root)
        validate(root)

        scenarios = [
            (WORKFLOW_PATH, WORKFLOW_PHASE7_HOOKS[0], "run: true"),
            (WORKFLOW_PATH, WORKFLOW_PHASE7_HOOKS[1], "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py"),
            (WORKFLOW_PATH, WORKFLOW_PHASE7_HOOKS[3], "run: python3 scripts/zigux/check-phase7-shared-control-gap.py"),
            (WORKFLOW_PATH, WORKFLOW_REQUIRED_ORDER[5], "run: python3 scripts/zigux/check-phase7-shared-control-gap.py"),
            (WORKFLOW_PATH, WORKFLOW_REQUIRED_ORDER[0], "run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test"),
            (WORKFLOW_PATH, WORKFLOW_PHASE7_HOOKS[0], WORKFLOW_PHASE7_HOOKS[0] + "\n" + WORKFLOW_PHASE7_HOOKS[0]),
            (VALIDATOR_PATH, VALIDATOR_REQUIRED_ORDER[5], 'run_checker(root, CHECKER_PATH)'),
            (VALIDATOR_PATH, VALIDATOR_REQUIRED_ORDER[9], "run_checker(root, CMDLINE_PACKET_CHECKER_PATH)"),
            (VALIDATOR_PATH, VALIDATOR_REQUIRED_ORDER[13], "run_checker(root, ARGV_SPLIT_PACKET_CHECKER_PATH)"),
            (MAKEFILE_PATH, MAKEFILE_REQUIRED_LINES[0], "phase7-verify:"),
            (MAKEFILE_PATH, MAKEFILE_REQUIRED_LINES[1], "\ttrue"),
            (MAKEFILE_PATH, MAKEFILE_REQUIRED_LINES[2], MAKEFILE_REQUIRED_LINES[2] + "\nphase7-test:"),
            (BUILD_PATH, BUILD_TEST_STEP_ORDER[3], BUILD_TEST_STEP_ORDER[4]),
            (BUILD_PATH, BUILD_TEST_STEP_ORDER[9], BUILD_TEST_STEP_ORDER[8]),
            (BUILD_PATH, BUILD_TEST_STEP_ORDER[0], 'const test_step = b.step("phase7-test", "Run the Phase 7 runtime helper tests");'),
            (CATALOG_PATH, CATALOG_REQUIRED_SNIPPETS[0], ""),
            (CATALOG_PATH, CATALOG_REQUIRED_SNIPPETS[1], ""),
        ]

        for rel, old, new in scenarios:
            build_fixture_root(root)
            mutate_once(root, rel, old, new)
            expect_failure(root)
            cases += 1

    if cases != SELF_TEST_CASE_COUNT:
        raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases}")
    print("PHASE7_RUNTIME_WORKSPACE_BOOTSTRAP_HANDOFF_SELF_TEST=pass")
    print(f"PHASE7_RUNTIME_WORKSPACE_BOOTSTRAP_HANDOFF_SELF_TEST_CASE_COUNT={cases}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE7_RUNTIME_WORKSPACE_BOOTSTRAP_HANDOFF=fail: {exc}")
        return 1

    print("PHASE7_RUNTIME_WORKSPACE_BOOTSTRAP_HANDOFF=pass")
    print(f"PHASE7_RUNTIME_WORKSPACE_BOOTSTRAP_HANDOFF_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE7_RUNTIME_WORKSPACE_BOOTSTRAP_HANDOFF_WORKFLOW_PHASE7_HOOK_COUNT={len(WORKFLOW_PHASE7_HOOKS)}")
    print(f"PHASE7_RUNTIME_WORKSPACE_BOOTSTRAP_HANDOFF_VALIDATOR_CHAIN_COUNT={len(VALIDATOR_REQUIRED_ORDER)}")
    print(f"PHASE7_RUNTIME_WORKSPACE_BOOTSTRAP_HANDOFF_BUILD_TEST_STEP_COUNT={len(BUILD_TEST_STEP_ORDER)}")
    print(
        "PHASE7_RUNTIME_WORKSPACE_BOOTSTRAP_HANDOFF_WORKFLOW_ORDER="
        "phase9-runtime-survey>phase7-shared-gap-selftest>phase7-shared-gap>"
        "phase7-make-wrapper-selftest>phase7-make-wrapper>phase10-bootstrap-selftest"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
